import sqlite3
import threading
import time
from datetime import datetime
from modbus_client import ModbusCLP
import statistics

class TemperatureCollector:
    """Coleta e armazena dados de temperatura do CLP em tempo real"""
    
    def __init__(self, plc_ip='192.168.0.200', hr_address=40001, interval=5):
        """
        Args:
            plc_ip: IP do CLP
            hr_address: Endereço Holding Register da temperatura
            interval: Intervalo de coleta em segundos
        """
        self.plc_ip = plc_ip
        self.hr_address = hr_address
        self.interval = interval
        self.running = False
        self.thread = None
        self.db_path = 'temperature_data.db'
        
        # Inicializar banco de dados
        self._init_database()
        
        print(f"[TEMP MONITOR] Inicializado - HR {hr_address}, intervalo {interval}s")
    
    def _init_database(self):
        """Cria tabela se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                anomaly BOOLEAN DEFAULT FALSE,
                rate_of_change REAL DEFAULT 0
            )
        ''')
        
        # Índice para consultas rápidas por timestamp
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON temperature_readings(timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
        print("[TEMP MONITOR] Banco de dados inicializado")
    
    def start(self):
        """Inicia coleta de dados em background"""
        if self.running:
            print("[TEMP MONITOR] Já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
        print("[TEMP MONITOR] Coleta iniciada")
    
    def stop(self):
        """Para a coleta de dados"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("[TEMP MONITOR] Coleta parada")
    
    def _collect_loop(self):
        """Loop principal de coleta"""
        last_temp = None
        
        while self.running:
            try:
                # Ler temperatura do CLP
                temp = self._read_temperature()
                
                if temp is not None:
                    # Calcular taxa de variação
                    rate = 0
                    if last_temp is not None:
                        rate = (temp - last_temp) / self.interval  # °C/s
                    
                    # Detectar anomalia (variação > 2°C em 5s = 0.4°C/s)
                    is_anomaly = abs(rate) > 0.4 if last_temp is not None else False
                    
                    # Salvar no banco
                    self._save_reading(temp, is_anomaly, rate)
                    
                    if is_anomaly:
                        print(f"[TEMP MONITOR] ⚠️ ANOMALIA: {temp:.2f}°C (Δ{rate:.2f}°C/s)")
                    
                    last_temp = temp
                else:
                    print("[TEMP MONITOR] Falha ao ler temperatura")
                
            except Exception as e:
                print(f"[TEMP MONITOR] Erro no loop: {e}")
            
            # Aguardar próximo ciclo
            time.sleep(self.interval)
    
    def _read_temperature(self):
        """Lê temperatura do CLP via Modbus"""
        clp = ModbusCLP(ip=self.plc_ip, port=502)
        
        try:
            if not clp.connect():
                return None
            
            # Converter endereço HR para index (40001 -> 0)
            index = self.hr_address - 40001
            temp = clp.read_real(index)
            
            clp.close()
            return temp
            
        except Exception as e:
            print(f"[TEMP MONITOR] Erro Modbus: {e}")
            try:
                clp.close()
            except:
                pass
            return None
    
    def _save_reading(self, temperature, anomaly, rate):
        """Salva leitura no banco de dados com timestamp local"""
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Usar horário local do sistema
        timestamp_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO temperature_readings (timestamp, temperature, anomaly, rate_of_change)
            VALUES (?, ?, ?, ?)
        ''', (timestamp_local, temperature, anomaly, rate))
        
        conn.commit()
        conn.close()
    
    def get_latest(self, limit=100):
        """Retorna últimas N leituras"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, temperature, anomaly, rate_of_change
            FROM temperature_readings
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'temperature': row[1],
                'anomaly': bool(row[2]),
                'rate_of_change': row[3]
            }
            for row in reversed(rows)  # Ordem cronológica
        ]
    
    def get_statistics(self, hours=24):
        """Calcula estatísticas das últimas N horas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT temperature, anomaly
            FROM temperature_readings
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        temps = [row[0] for row in rows]
        anomalies = sum(1 for row in rows if row[1])
        
        return {
            'count': len(temps),
            'min': min(temps),
            'max': max(temps),
            'avg': statistics.mean(temps),
            'stdev': statistics.stdev(temps) if len(temps) > 1 else 0,
            'anomalies': anomalies,
            'period_hours': hours
        }
    
    def get_current(self):
        """Retorna leitura mais recente"""
        latest = self.get_latest(limit=1)
        return latest[0] if latest else None
