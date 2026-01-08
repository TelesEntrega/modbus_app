import time
import sys
from modbus_client import ModbusCLP

def main():
    print("=== INICIANDO SERVIÇO DE WATCHDOG ===")
    print("CLP Alvo: 192.168.0.200 | Tag: Watchdog (HR 40004 -> Index 3)")
    print("Intervalo: 500ms | Pressione Ctrl+C para sair.")
    print("-" * 50)

    clp = ModbusCLP(ip='192.168.0.200', port=502)
    
    last_connection_attempt = 0
    connection_retry_interval = 2.0  # Segundos

    while True:
        try:
            # Verifica conexão
            if not clp.client.connected:
                now = time.time()
                if now - last_connection_attempt > connection_retry_interval:
                    print("Tentando conectar ao CLP...")
                    last_connection_attempt = now
                    if clp.connect():
                        print(">> CONECTADO! Retomando Watchdog.")
                    else:
                        print(f"Falha na conexão. Nova tentativa em {connection_retry_interval}s...")
                
                # Se não conectado, aguarda um pouco para não travar CPU
                if not clp.client.connected:
                    time.sleep(0.1)
                    continue

            # Lógica do Watchdog
            # 1. Ler valor atual
            # Address 3 (HR 40004)
            current_val = clp.read_int(3)
            
            # 2. Incrementar
            new_val = current_val + 1
            if new_val > 30000: # Reseta antes do limite do INT (32767)
                new_val = 0
            
            # 3. Escrever novo valor
            clp.write_int(3, new_val)
            
            # Opcional: Feedback visual (pode remover para serviço)
            # print(f"Watchdog Heartbeat: {new_val}", end='\r')

            # 4. Aguardar 500ms
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\nParando serviço de Watchdog...")
            break
        except Exception as e:
            print(f"\nErro no loop: {e}")
            print("Tentando reconectar em breve...")
            try:
                clp.close()
            except:
                pass
            time.sleep(2)  # Delay antes de tentar reconectar

    clp.close()
    print("Serviço encerrado.")
    sys.exit(0)

if __name__ == "__main__":
    main()
