"""
Script de Teste de Conexão com CLP Real
Ajuda a diagnosticar problemas de conexão Modbus
"""
from modbus_client import ModbusCLP
import sys

def test_connection():
    print("=" * 70)
    print("  🔧 TESTE DE CONEXÃO MODBUS - CLP")
    print("=" * 70)
    
    # Solicita configurações
    print("\n📝 Digite as informações de conexão:")
    ip = input("  IP do CLP (ex: 192.168.0.200): ").strip()
    if not ip:
        ip = '192.168.0.200'
        print(f"  Usando padrão: {ip}")
    
    port_input = input("  Porta Modbus (ex: 502): ").strip()
    port = int(port_input) if port_input else 502
    print(f"  Usando porta: {port}")
    
    print("\n" + "-" * 70)
    print("  [1/3] Tentando conectar ao CLP...")
    print(f"  IP: {ip}")
    print(f"  Porta: {port}")
    print("-" * 70)
    
    # Tenta conectar
    try:
        clp = ModbusCLP(ip=ip, port=port)
        if not clp.connect():
            print("\n❌ FALHA: Não foi possível estabelecer conexão!")
            print("\n  Possíveis causas:")
            print("  • IP ou porta incorretos")
            print("  • CLP offline ou inacessível")
            print("  • Firewall bloqueando a porta")
            print("  • Servidor Modbus não habilitado no CLP")
            return False
        
        print("✅ Conexão estabelecida com sucesso!")
        
        # Teste de leitura
        print("\n" + "-" * 70)
        print("  [2/3] Testando leitura de variáveis...")
        print("-" * 70)
        
        # Solicita endereços para teste
        print("\n  Digite os endereços para teste (deixe em branco para pular)")
        
        # Teste BOOL
        bool_addr = input("  Endereço de uma COIL (BOOL) para teste: ").strip()
        if bool_addr:
            try:
                addr = int(bool_addr)
                value = clp.read_bool(addr)
                print(f"  ✅ BOOL @{addr} = {value}")
            except Exception as e:
                print(f"  ❌ Erro ao ler BOOL @{addr}: {e}")
        
        # Teste INT
        int_addr = input("  Endereço de um HOLDING REGISTER (INT) para teste: ").strip()
        if int_addr:
            try:
                addr = int(int_addr)
                value = clp.read_int(addr)
                print(f"  ✅ INT @{addr} = {value}")
            except Exception as e:
                print(f"  ❌ Erro ao ler INT @{addr}: {e}")
        
        # Teste REAL
        real_addr = input("  Endereço de um HOLDING REGISTER (REAL) para teste: ").strip()
        if real_addr:
            try:
                addr = int(real_addr)
                value = clp.read_real(addr)
                print(f"  ✅ REAL @{addr} = {value:.2f}")
            except Exception as e:
                print(f"  ❌ Erro ao ler REAL @{addr}: {e}")
        
        # Teste de escrita
        print("\n" + "-" * 70)
        print("  [3/3] Testando escrita de variáveis...")
        print("-" * 70)
        
        write_test = input("\n  Deseja testar escrita? (s/n): ").strip().lower()
        if write_test == 's':
            # Teste INT
            int_write_addr = input("  Endereço INT para escrever: ").strip()
            if int_write_addr:
                try:
                    addr = int(int_write_addr)
                    value = int(input("  Valor INT para escrever: ").strip())
                    
                    # Lê valor atual
                    old_value = clp.read_int(addr)
                    print(f"  Valor atual: {old_value}")
                    
                    # Escreve novo valor
                    clp.write_int(addr, value)
                    print(f"  ✍️  Escrito: {value}")
                    
                    # Lê novamente para confirmar
                    new_value = clp.read_int(addr)
                    print(f"  📖 Lido após escrita: {new_value}")
                    
                    if new_value == value:
                        print(f"  ✅ Escrita confirmada! {old_value} → {new_value}")
                    else:
                        print(f"  ⚠️  Valor lido ({new_value}) diferente do escrito ({value})")
                        
                except Exception as e:
                    print(f"  ❌ Erro na escrita: {e}")
        
        # Sucesso!
        print("\n" + "=" * 70)
        print("  ✅ TESTE CONCLUÍDO!")
        print("=" * 70)
        print("\n  Próximos passos:")
        print("  1. Anote os endereços que funcionaram")
        print("  2. Configure esses endereços no web_server.py")
        print("  3. Reinicie o servidor web")
        print()
        
        clp.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    success = test_connection()
    print("\n")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
