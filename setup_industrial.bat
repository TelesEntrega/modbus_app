@echo off
setlocal enabledelayedexpansion
title Setup Industrial - Monitoramento Modbus

cd /d "%~dp0"

echo ===============================================================================
echo   CONFIGURACAO INICIAL - PC INDUSTRIAL
echo   Sistema de Monitoramento e Controle (Weintek/Altus)
echo ===============================================================================
echo.

:: 1. Verificacao de Permissoes (Admin opcional, mas recomendavel para firewall)
:: (Ignorado para simplificar, assume usuario padrao)

:: 2. Verificacao do Python
echo [1/5] Verificando instalacao do Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO CRITICO] Python nao encontrado!
    echo.
    echo Para prosseguir:
    echo 1. Baixe o Python 3.x em python.org
    echo 2. Instale marcando a opcao "Add Python to PATH"
    echo 3. Reinicie este script.
    echo.
    pause
    exit /b 1
)
echo    - Python detectado.

:: 3. Criacao do Ambiente Virtual (Isolamento)
if not exist "venv" (
    echo.
    echo [2/5] Criando ambiente virtual (Primeira execucao)...
    python -m venv venv
    if !ERRORLEVEL! NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual. Verifique permissoes.
        pause
        exit /b 1
    )
    echo    - Ambiente criado com sucesso.
) else (
    echo [2/5] Ambiente virtual ja existe. Pulando criacao.
)

:: 4. Instalacao de Bibliotecas
echo.
echo [3/5] Atualizando bibliotecas do sistema...
.\venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao instalar dependencias.
    echo Verifique sua conexao com a internet ou proxy.
    pause
    exit /b 1
)
echo    - Todas as bibliotecas instaladas.

:: 5. Configuracao Padrao (.env)
if not exist ".env" (
    echo.
    echo [4/5] Gerando arquivo de configuracao padrao...
    echo GEMINI_API_KEY=> .env
    echo    - Arquivo .env criado. (Edite-o se for usar IA)
) else (
    echo [4/5] Configuracao encontrada.
)

:: 6. Inicializacao do Sistema
echo.
echo [5/5] INICIANDO SISTEMA...
echo.
echo    -> Iniciando Watchdog (Monitoramento de Conexao)...
start "Watchdog Modbus - NAO FECHE" /min .\venv\Scripts\python.exe watchdog.py

echo    -> Iniciando Servidor Web...
echo    -> Interface disponivel em: http://localhost:5000
echo.

:: Abre o navegador
timeout /t 5 /nobreak >nul
start http://localhost:5000

:: Inicia o App Web (este comando segura a janela aberta)
.\venv\Scripts\python.exe web_app.py

:: Se a janela do web_app fechar, mata o watchdog
taskkill /F /FI "WINDOWTITLE eq Watchdog Modbus - NAO FECHE" >nul 2>&1
