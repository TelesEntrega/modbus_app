========================================================================
             APLICAÇÃO MODBUS TCP - ALTUS XP-325
========================================================================

ESTRUTURA DE PASTAS:
modbus_app/
  ├── modbus_client.py   # Classe de comunicação Modbus (Core)
  ├── main.py            # Script de teste de leitura/escrita
  ├── watchdog.py        # Script de watchdog (loop infinito)
  ├── requirements.txt   # Dependências do projeto
  ├── install_and_run.bat # Script de instalação e execução automática (Novo!)
  └── README.txt         # Este arquivo

PRÉ-REQUISITOS:
- Windows 10 Pro 64 bits
- Python 3.11.x instalado e no PATH
- Acesso à rede do CLP (IP 192.168.0.200)

------------------------------------------------------------------------
0. MODO FÁCIL (AUTOMÁTICO)
------------------------------------------------------------------------
Basta dar dois cliques no arquivo 'install_and_run.bat'.
Ele fará tudo: criará o venv, instalará as dependências e abrirá
um menu para escolher qual script rodar.

Se preferir o modo manual:

Abra o PowerShell ou CMD dentro da pasta 'modbus_app' e execute:

  python -m venv venv

------------------------------------------------------------------------
2. COMO ATIVAR O AMBIENTE
------------------------------------------------------------------------
No Windows (PowerShell):
  .\venv\Scripts\Activate

(Você verá '(venv)' aparecer no início da linha de comando)

------------------------------------------------------------------------
3. COMO INSTALAR AS DEPENDÊNCIAS
------------------------------------------------------------------------
Com o venv ativado, execute:

  pip install -r requirements.txt

Isso instalará o 'pymodbus' versão 3.x.

------------------------------------------------------------------------
4. COMO RODAR O TESTE GERAL (MAIN.PY)
------------------------------------------------------------------------
Este script conecta ao CLP, realiza testes de leitura e escrita nas
tags mapeadas (Start, Estado, Temp) e encerra.

  python main.py

------------------------------------------------------------------------
5. COMO RODAR O WATCHDOG
------------------------------------------------------------------------
Este script roda indefinidamente, incrementando a tag Watchdog
a cada 500ms. Possui reconexão automática.

  python watchdog.py

Para parar, pressione Ctrl+C.

========================================================================
NOTAS TÉCNICAS:
- Endianness configurado para BIG ENDIAN (Byte e Word Order).
- Usando pymodbus 3.x.
- Mapeamento Modbus:
  * Coil 00001 (Index 0): OPC_Start
  * HR 40001   (Index 0): OPC_Estado (INT)
  * HR 40002   (Index 1): OPC_Temp (REAL - 2 words)
  * HR 40004   (Index 3): Watchdog (INT)
========================================================================
