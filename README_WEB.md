# Servidor Web Modbus CLP

Interface web moderna para controle e monitoramento de variáveis Modbus em CLPs.

## 🚀 Como Usar

### Opção 1: Iniciar Automaticamente (Recomendado)

Execute o arquivo `start_web.bat`:

```bash
start_web.bat
```

Isso irá:
1. Ativar o ambiente virtual
2. Instalar dependências necessárias
3. Iniciar o Mock Server (para testes)
4. Iniciar o Servidor Web

### Opção 2: Iniciar Manualmente

1. **Ative o ambiente virtual:**
```bash
venv\Scripts\activate.bat
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Inicie o Mock Server (para testes):**
```bash
python mock_server.py
```

4. **Em outro terminal, inicie o Servidor Web:**
```bash
python web_server.py
```

## 🌐 Acessar a Interface

Abra seu navegador e acesse:

```
http://localhost:5000
```

## ⚙️ Configuração

### Conectar ao CLP Real

1. Na interface web, altere o IP e a porta:
   - **IP**: Endereço IP do seu CLP (ex: `192.168.0.200`)
   - **Porta**: Porta Modbus (geralmente `502`)

2. Clique em **"Atualizar"**

### Usar o Mock Server (Testes)

Para testes locais, use:
- **IP**: `localhost`
- **Porta**: `5020`

## 📊 Funcionalidades

### Variáveis Booleanas
- **OPC_Start**: Comando Start
- **OPC_Stop**: Comando Stop
- **OPC_Reset**: Comando Reset

### Variáveis Inteiras
- **OPC_Estado**: Estado da Máquina
- **OPC_Contador**: Contador de Peças
- **OPC_Watchdog**: Watchdog

### Variáveis Reais
- **OPC_Temp**: Temperatura (°C)
- **OPC_Pressao**: Pressão (bar)
- **OPC_Velocidade**: Velocidade (m/s)

## 🔧 Operações

### Ler Variáveis
- **Individualmente**: Clique no botão "📖 Ler" ao lado de cada variável
- **Todas de uma vez**: Clique em "📊 Ler Todas" no topo da página
- **Auto-refresh**: As variáveis são atualizadas automaticamente a cada 5 segundos

### Escrever Variáveis

#### Booleanas
- Clique no switch para alternar entre ON/OFF

#### Inteiras e Reais
1. Digite o valor desejado no campo
2. Clique em "✍️ Escrever"
3. O valor será enviado ao CLP e o display será atualizado

## 📁 Estrutura do Projeto

```
modbus_app/
├── web_server.py          # Servidor Flask (Backend)
├── modbus_client.py       # Cliente Modbus
├── mock_server.py         # Servidor Mock para testes
├── start_web.bat          # Script de inicialização
├── requirements.txt       # Dependências
├── templates/
│   └── index.html        # Interface HTML
└── static/
    ├── css/
    │   └── style.css     # Estilos modernos
    └── js/
        └── app.js        # Lógica JavaScript
```

## 🎨 Características da Interface

- ✨ Design moderno com gradientes vibrantes
- 🌙 Modo escuro elegante
- 🎭 Animações suaves e micro-interações
- 📱 Responsivo (funciona em desktop e mobile)
- 🔔 Notificações toast elegantes
- 🔄 Auto-refresh de variáveis
- 🎯 Interface intuitiva e organizada

## 🔐 Segurança

⚠️ **IMPORTANTE**: Esta aplicação é destinada para uso em redes locais protegidas. Não exponha diretamente à internet sem implementar autenticação e criptografia adequadas.

## 📝 Notas

- O servidor web roda na porta `5000`
- O mock server roda na porta `5020`
- CLPs reais geralmente usam a porta `502`
- Certifique-se de que o firewall permite a comunicação

## 🆘 Solução de Problemas

### Erro de Conexão
- Verifique se o IP e porta estão corretos
- Verifique se o CLP está acessível na rede
- Para testes, certifique-se de que o Mock Server está rodando

### Variáveis não atualizam
- Clique em "📊 Ler Todas" para forçar atualização
- Verifique a conexão com o CLP
- Verifique os logs no terminal do servidor

### Porta já em uso
- Feche outras instâncias do servidor web
- Ou altere a porta no arquivo `web_server.py` (linha final)

## 📞 Suporte

Para mais informações sobre o protocolo Modbus e comunicação com CLPs, consulte a documentação do fabricante do seu CLP.
