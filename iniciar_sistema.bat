@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo   INICIALIZANDO SISTEMA DE CONTROLE E MONITORAMENTO (WEINTEK/ALTUS)
echo ===============================================================================

cd /d "%~dp0"

:: 1. Verificacao do Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado! Instale o Python 3.x e adicione ao PATH.
    pause
    exit /b 1
)

:: 2. Configuracao do Ambiente Virtual
if not exist "venv" (
    echo [SETUP] Criando ambiente virtual...
    python -m venv venv
)

:: 3. Instalacao de Dependencias
echo [SETUP] Verificando dependencias...
.\venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1

:: 4. Verificacao de Configuracao
if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado. A IA pode nao funcionar.
    echo Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui
)

:: 5. Iniciando Watchdog (Background)
echo [SISTEMA] Iniciando servico de Watchdog (PLC Heartbeat)...
start "Watchdog Modbus" /min .\venv\Scripts\python.exe watchdog.py

:: 6. Iniciando Servidor Web (Foreground)
echo [SISTEMA] Iniciando Interface Web...
echo.
echo    Acesse no navegador: http://localhost:5000
echo    Pressione Ctrl+C nesta janela para encerrar o servidor web.
echo.

:: Abrir navegador automaticamente apos 3 segundos
timeout /t 3 /nobreak >nul
start http://localhost:5000

:: Executar aplicacao
.\venv\Scripts\python.exe web_app.py

:: Ao fechar, tentar matar o watchdog tambem
taskkill /F /FI "WINDOWTITLE eq Watchdog Modbus" >nul 2>&1
