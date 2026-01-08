# 🔧 Configuração do CLP Real

## ❓ Informações Necessárias

Para conectar a interface web ao seu CLP real, preciso das seguintes informações:

### 1. Endereço de Rede
- **IP do CLP**: _____________________ (exemplo: 192.168.0.200)
- **Porta Modbus**: _____________________ (geralmente 502)

### 2. Endereços das Variáveis no CLP

De acordo com a imagem, as variáveis no software do CLP são:

| Variável no CLP | Tipo | Endereço Modbus | Observação |
|----------------|------|-----------------|------------|
| PC_Start | BOOL | ? | Coil address |
| PC_Stop | BOOL | ? | Coil address |
| PC_Falha | BOOL | ? | Coil address |
| PC_Estado | INT | ? | Holding Register address |
| PC_Temp | REAL | ? | Holding Register address (2 registros) |

### 3. Verificação Atual

Atualmente a interface está conectada em:
- **IP**: `localhost` 
- **Porta**: `5020` (Mock Server)

Por isso os valores chegam no Mock Server mas não no CLP real.

## 📋 Como Descobrir os Endereços

1. **No software do CLP**, verifique a configuração do servidor Modbus
2. Procure pela tabela de mapeamento de variáveis
3. Anote os endereços Modbus de cada variável
4. Confirme se são Coils (0xxxx) ou Holding Registers (4xxxx)

## ✅ Próximos Passos

Depois que você me fornecer essas informações, vou:
1. Atualizar a interface com os endereços corretos
2. Configurar a conexão com o CLP real (não o mock)
3. Testar a comunicação
4. Validar leitura e escrita de cada variável
