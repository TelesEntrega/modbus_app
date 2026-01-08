from pymodbus.client import ModbusTcpClient
import time
import sys

# IP do PLC
PLC_IP = "192.168.0.200"
PLC_PORT = 502

def test_connection():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    print(f"Tentando conectar a {PLC_IP}:{PLC_PORT}...")
    
    if not client.connect():
        print("❌ Falha na conexão!")
        return
    
    print("✅ Conectado com sucesso!\n")
    
    # Teste 1: Ler Tensão (HR 40001) - Validar conexão
    print("--- Teste de Leitura (Referência) ---")
    try:
        # Ler 40001 (Index 0)
        result = client.read_holding_registers(0, 2)
        if not result.isError():
            print(f"✅ Leitura HR 40001 (Index 0): {result.registers}")
        else:
            print(f"❌ Erro ao ler HR 40001: {result}")
    except Exception as e:
        print(f"❌ Exceção na leitura: {e}")

    # Teste 2: Escrever PC_Estado (HR 40003 -> Index 2)
    print("\n--- Teste de Escrita: PC_Estado (HR 40003) ---")
    try:
        val_to_write = 123
        print(f"Tentando escrever {val_to_write} em HR 40003 (Index 2)...")
        result = client.write_register(2, val_to_write)
        
        if not result.isError():
            print("✅ Escrita SUCESSO!")
            # Ler de volta
            check = client.read_holding_registers(2, 1)
            if not check.isError() and check.registers[0] == val_to_write:
                 print(f"✅ Valor verificado: {check.registers[0]}")
            else:
                 print(f"⚠️ Escrita confirmada mas leitura retornou: {check.registers if not check.isError() else check}")
        else:
            print(f"❌ Erro na escrita: {result}")
            
    except Exception as e:
        print(f"❌ Exceção na escrita: {e}")

    # Teste 3: Escrever Coils (PC_Start - Coil 1, PC_Stop - Coil 2)
    print("\n--- Teste de Escrita: Coils ---")
    
    # Index 0 (Coil 1?)
    try:
        print("Tentando escrever True em Coil 1 (Index 0)...")
        result = client.write_coil(0, True)
        if not result.isError():
            print("✅ Escrita Coil Index 0 SUCESSO!")
        else:
            print(f"❌ Erro Coil Index 0: {result}")
    except Exception as e:
        print(f"❌ Exceção: {e}")
        
    # Index 1 (Coil 2? Ou Coil 1 se 1-based?)
    try:
        print("Tentando escrever True em Coil 1 (Index 1)...")
        result = client.write_coil(1, True)
        if not result.isError():
            print("✅ Escrita Coil Index 1 SUCESSO!")
        else:
            print(f"❌ Erro Coil Index 1: {result}")
    except Exception as e:
        print(f"❌ Exceção: {e}")

    client.close()

if __name__ == "__main__":
    test_connection()
