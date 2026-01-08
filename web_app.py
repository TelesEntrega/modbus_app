from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from modbus_client import ModbusCLP
from temperature_monitor import TemperatureCollector
from ai_analyzer import TemperatureAIAnalyzer
import threading
import time

app = Flask(__name__, static_folder='static')
CORS(app)

# Instância global do cliente Modbus
clp = ModbusCLP(ip='192.168.0.200', port=502)
operation_lock = threading.Lock()

# Estado de conexão (para display apenas)
connection_status = {
    'connected': False,
    'last_check': None,
    'error': None
}

def ensure_connection():
    """Garante que há uma conexão ativa antes de cada operação"""
    try:
        # Se já estiver conectado, retornar True
        if clp.client.is_socket_open():
            return True
            
        # Tentar conectar
        if clp.connect():
            connection_status['connected'] = True
            connection_status['error'] = None
            connection_status['last_check'] = time.time()
            print("✅ [MODBUS] Conexão restabelecida.")
            return True
        else:
            connection_status['connected'] = False
            connection_status['error'] = "Falha ao conectar"
            print("❌ [MODBUS] Falha ao conectar.")
            return False
    except Exception as e:
        connection_status['connected'] = False
        connection_status['error'] = str(e)
        return False

def check_connection_status():
    """Thread separada apenas para verificar se CLP está acessível"""
    while True:
        try:
            with operation_lock:
                if clp.client.is_socket_open():
                     connection_status['connected'] = True
                     connection_status['error'] = None
                else:
                    # Tentar reconectar silenciosamente
                    if clp.connect():
                        connection_status['connected'] = True
                        connection_status['error'] = None
                    else:
                        connection_status['connected'] = False
                        connection_status['error'] = "Desconectado"
            
            connection_status['last_check'] = time.time()
        except Exception as e:
            connection_status['connected'] = False
            connection_status['error'] = str(e)
        
        time.sleep(5)  # Verifica a cada 5 segundos

# Iniciar thread de verificação de status
status_thread = threading.Thread(target=check_connection_status, daemon=True)
status_thread.start()

# ==================== ROTAS DA API ====================

@app.route('/')
def index():
    """Servir página principal"""
    return send_from_directory('static', 'index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retorna status da conexão"""
    return jsonify(connection_status)

@app.route('/api/bool/read', methods=['POST'])
def read_bool():
    """Lê valor booleano
    Body: {"address": 0}
    """
    try:
        data = request.get_json()
        address = data.get('address', 0)
        
        with operation_lock:
            # Conectar para esta operação
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                value = clp.read_bool(address)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': value
                })
            except Exception as e:
                # Se falhar, tentar reconectar uma vez
                clp.close()
                if ensure_connection():
                    value = clp.read_bool(address)
                    return jsonify({'success': True, 'address': address, 'value': value})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bool/write', methods=['POST'])
def write_bool():
    """Escreve valor booleano
    Body: {"address": 0, "value": true}
    """
    try:
        data = request.get_json()
        address = data.get('address', 0)
        value = data.get('value', False)
        
        with operation_lock:
            # Conectar para esta operação
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                clp.write_bool(address, value)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': value,
                    'message': f'BOOL {address} definido para {value}'
                })
            except Exception as e:
                clp.close()
                if ensure_connection():
                    clp.write_bool(address, value)
                    return jsonify({'success': True, 'address': address, 'value': value, 'message': f'BOOL {address} definido para {value}'})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/int/read', methods=['POST'])
def read_int():
    """Lê valor inteiro
    Body: {"address": 0}
    """
    try:
        data = request.get_json()
        address = data.get('address', 0)
        
        with operation_lock:
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                value = clp.read_int(address)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': value
                })
            except Exception as e:
                clp.close()
                if ensure_connection():
                    value = clp.read_int(address)
                    return jsonify({'success': True, 'address': address, 'value': value})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/int/write', methods=['POST'])
def write_int():
    """Escreve valor inteiro
    Body: {"address": 0, "value": 1234}
    """
    try:
        data = request.get_json()
        address = data.get('address', 0)
        value = int(data.get('value', 0))
        
        with operation_lock:
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                clp.write_int(address, value)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': value,
                    'message': f'INT {address} definido para {value}'
                })
            except Exception as e:
                clp.close()
                if ensure_connection():
                     clp.write_int(address, value)
                     return jsonify({'success': True, 'address': address, 'value': value, 'message': f'INT {address} definido para {value}'})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/real/read', methods=['POST'])
def read_real():
    """Lê valor real (float)
    Body: {"address": 1}
    """
    try:
        data = request.get_json()
        address = data.get('address', 1)
        
        with operation_lock:
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                value = clp.read_real(address)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': round(value, 2)
                })
            except Exception as e:
                clp.close()
                if ensure_connection():
                    value = clp.read_real(address)
                    return jsonify({'success': True, 'address': address, 'value': round(value, 2)})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/real/write', methods=['POST'])
def write_real():
    """Escreve valor real (float)
    Body: {"address": 1, "value": 75.5}
    """
    try:
        data = request.get_json()
        address = data.get('address', 1)
        value = float(data.get('value', 0.0))
        
        with operation_lock:
            if not ensure_connection():
                return jsonify({'error': 'Falha ao conectar ao CLP'}), 503
            
            try:
                clp.write_real(address, value)
                return jsonify({
                    'success': True,
                    'address': address,
                    'value': value,
                    'message': f'REAL {address} definido para {value}'
                })
            except Exception as e:
                clp.close()
                if ensure_connection():
                    clp.write_real(address, value)
                    return jsonify({'success': True, 'address': address, 'value': value, 'message': f'REAL {address} definido para {value}'})
                raise e
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TEMPERATURE MONITORING ====================

# Inicializar coletor e analisador
temp_collector = TemperatureCollector(plc_ip='192.168.0.200', hr_address=40001, interval=5)
ai_analyzer = TemperatureAIAnalyzer()  # Usa GEMINI_API_KEY do ambiente, se disponível

@app.route('/monitoring')
def monitoring_page():
    """Página de monitoramento de temperatura"""
    return send_from_directory('static', 'monitoring.html')

@app.route('/api/temperature/current', methods=['GET'])
def get_current_temperature():
    """Retorna temperatura atual"""
    try:
        current = temp_collector.get_current()
        if not current:
            return jsonify({'error': 'Nenhuma leitura disponível'}), 404
        
        return jsonify(current)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/history', methods=['GET'])
def get_temperature_history():
    """Retorna histórico de temperatura"""
    try:
        limit = int(request.args.get('limit', 100))
        limit = min(limit, 1000)  # Máximo 1000 pontos
        
        history = temp_collector.get_latest(limit=limit)
        return jsonify({
            'data': history,
            'count': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/stats', methods=['GET'])
def get_temperature_stats():
    """Retorna estatísticas de temperatura"""
    try:
        hours = int(request.args.get('hours', 24))
        stats = temp_collector.get_statistics(hours=hours)
        
        if not stats:
            return jsonify({'error': 'Sem dados para o período'}), 404
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/analyze', methods=['POST'])
def analyze_temperature():
    """Analisa padrões de temperatura com IA"""
    try:
        # Parâmetros opcionais
        data = request.get_json() or {}
        limit = data.get('limit', 200)
        hours = data.get('hours', 24)
        
        # Buscar dados
        readings = temp_collector.get_latest(limit=limit)
        stats = temp_collector.get_statistics(hours=hours)
        
        if not readings:
            return jsonify({'error': 'Sem dados para análise'}), 404
        
        # Analisar com IA
        analysis = ai_analyzer.analyze_temperature_data(readings, stats)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/report', methods=['GET'])
def generate_temperature_report():
    """Gera relatório completo de temperatura"""
    try:
        hours = int(request.args.get('hours', 24))
        
        # Buscar dados
        readings = temp_collector.get_latest(limit=500)
        stats = temp_collector.get_statistics(hours=hours)
        analysis = ai_analyzer.analyze_temperature_data(readings, stats)
        
        # Gerar relatório
        report = ai_analyzer.generate_report(readings, stats, analysis)
        
        return jsonify({
            'report': report,
            'timestamp': analysis.get('timestamp'),
            'ai_powered': analysis.get('ai_powered', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  SERVIDOR WEB MODBUS - INTERFACE DE CONTROLE CLP")
    print("=" * 60)
    print(f"URL: http://localhost:5000")
    print(f"Monitoring: http://localhost:5000/monitoring")
    print(f"CLP: {clp.ip}:{clp.port}")
    print("-" * 60)
    print("Aguardando conexão com o CLP...")
    
    # Iniciar coletor de temperatura
    print("[STARTUP] Iniciando coletor de temperatura...")
    temp_collector.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
