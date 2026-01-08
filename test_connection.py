"""
Script rápido para testar conexão com o CLP
"""
from modbus_client import ModbusCLP
import sys

def test_connection():
    print("=" * 60)
    print("  TESTE RÁPIDO DE CONEXÃO - CLP ALTUS XP-325")
    print("=" * 60)
    print(f"IP Alvo: 192.168.0.200")
    print(f"Porta: 502")
    print("-" * 60)
    
    # Criar instância
    clp = ModbusCLP(ip='192.168.0.200', port=502)
    
    # Tentar conectar
    print("\n[1] Tentando conectar...")
    try:
        if clp.connect():
            print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
            print(f"   Cliente conectado: {clp.client.connected}")
            
            # Teste simples de leitura
            print("\n[2] Testando leitura de um registro (HR 40001)...")
            try:
                valor = clp.read_int(0)
                print(f"✅ Leitura bem-sucedida! Valor: {valor}")
            except Exception as e:
                print(f"❌ Erro na leitura: {e}")
            
            # Fechar conexão
            clp.close()
            print("\n[3] Conexão fechada normalmente.")
            print("\n" + "=" * 60)
            print("✅ TESTE DE CONEXÃO APROVADO!")
            print("=" * 60)
            return True
        else:
            print("❌ FALHA NA CONEXÃO!")
            print("\nPossíveis causas:")
            print("  • PLC está desligado ou não acessível")
            print("  • IP incorreto (verifique se é 192.168.0.200)")
            print("  • Firewall bloqueando porta 502")
            print("  • Cabo de rede desconectado")
            return False
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
