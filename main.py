from modbus_client import ModbusCLP
import time
import sys

def main():
    # Instancia a classe
    print("Inicializando cliente Modbus...")
    clp = ModbusCLP(ip='192.168.0.200', port=502)
    
    # Tenta conectar
    print(f"Conectando ao IP {clp.ip}...")
    if not clp.connect():
        print("FALHA: Não foi possível conectar ao CLP.")
        return

    print("Conexão estabelecida com sucesso!")
    print("-" * 50)

    try:
        # --- TESTE 1: BOOL - OPC_Start (Coil 00001 -> Index 0) ---
        print("[TESTE 1] BOOL - OPC_Start (Index 0)")
        
        # Leitura inicial
        val_inicial = clp.read_bool(0)
        print(f"  > Leitura Inicial: {val_inicial}")
        
        # Escrita True
        print("  > Escrevendo True...")
        clp.write_bool(0, True)
        print(f"  > Leitura Pós-Escrita: {clp.read_bool(0)}")
        
        # Escrita False (opcional, para deixar limpo)
        print("  > Escrevendo False...")
        clp.write_bool(0, False)
        print(f"  > Leitura Final: {clp.read_bool(0)}")
        print("-" * 50)

        # --- TESTE 2: INT - OPC_Estado (HR 40001 -> Index 0) ---
        print("[TESTE 2] INT - OPC_Estado (Index 0)")
        
        val_inicial = clp.read_int(0)
        print(f"  > Leitura Inicial: {val_inicial}")
        
        print("  > Escrevendo 1234...")
        clp.write_int(0, 1234)
        print(f"  > Leitura Confirmada: {clp.read_int(0)}")
        print("-" * 50)

        # --- TESTE 3: REAL - OPC_Temp (HR 40002 -> Index 1) ---
        print("[TESTE 3] REAL - OPC_Temp (Index 1)")
        # Real ocupa 2 registros (1 e 2)
        val_inicial = clp.read_real(1)
        print(f"  > Leitura Inicial: {val_inicial:.2f}")
        
        print("  > Escrevendo 75.5...")
        clp.write_real(1, 75.5)
        print(f"  > Leitura Confirmada: {clp.read_real(1):.2f}")
        print("-" * 50)

        print("TODOS OS TESTES REALIZADOS COM SUCESSO.")

    except Exception as e:
        print(f"ERRO CRÍTICO DURANTE OS TESTES: {e}")
    finally:
        print("Encerrando conexão...")
        clp.close()
        print("Conexão fechada.")

if __name__ == "__main__":
    main()
