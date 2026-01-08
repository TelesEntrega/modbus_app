from modbus_client import ModbusCLP
import time
import sys

# Adaptação da classe para permitir porta customizada se não tiver sido passado no init (embora a original tenha)
# Mas vamos usar a classe original importada

def main():
    # Usa porta 5020 (Mock) em vez de 502
    # Usa localhost
    TARGET_IP = 'localhost'
    TARGET_PORT = 5020
    
    print(f"Inicializando cliente de TESTE (Mock)...")
    clp = ModbusCLP(ip=TARGET_IP, port=TARGET_PORT)
    
    # Tenta conectar
    print(f"Conectando a {clp.ip}:{clp.port}...")
    if not clp.connect():
        print("FALHA: Não foi possível conectar ao Mock Server.")
        print("Verifique se o mock_server.py está rodando.")
        return

    print("Conexão com Mock Server estabelecida!")
    print("-" * 50)

    try:
        # --- TESTE 1: BOOL - OPC_Start (Address 0) ---
        print("[TESTE 1] BOOL - OPC_Start (Index 0)")
        val_inicial = clp.read_bool(0)
        print(f"  > Leitura Inicial: {val_inicial}")
        
        print("  > Escrevendo True...")
        clp.write_bool(0, True)
        print(f"  > Leitura Pós-Escrita: {clp.read_bool(0)}")
        
        # --- TESTE 2: INT - OPC_Estado (Address 0) ---
        print("\n[TESTE 2] INT - OPC_Estado (Index 0)")
        val_inicial = clp.read_int(0)
        print(f"  > Leitura Inicial: {val_inicial}")
        
        print("  > Escrevendo 1234...")
        clp.write_int(0, 1234)
        print(f"  > Leitura Confirmada: {clp.read_int(0)}")

        # --- TESTE 3: REAL - OPC_Temp (Address 1) ---
        print("\n[TESTE 3] REAL - OPC_Temp (Index 1)")
        val_inicial = clp.read_real(1)
        print(f"  > Leitura Inicial: {val_inicial:.2f}")
        
        print("  > Escrevendo 75.5...")
        clp.write_real(1, 75.5)
        print(f"  > Leitura Confirmada: {clp.read_real(1):.2f}")

        # --- TESTE 4: WATCHDOG Simulado (Address 3) ---
        print("\n[TESTE 4] Watchdog (Index 3)")
        print("  > Escrevendo 10...")
        clp.write_int(3, 10)
        print(f"  > Leitura: {clp.read_int(3)}")
        
        print("-" * 50)
        print("TODOS OS TESTES DO MOCK REALIZADOS COM SUCESSO.")

    except Exception as e:
        print(f"ERRO CRÍTICO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Encerrando conexão...")
        clp.close()

if __name__ == "__main__":
    main()
