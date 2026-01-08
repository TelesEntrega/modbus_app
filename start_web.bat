@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ===============================================
REM  SERVIDOR WEB MODBUS CLP
REM  Inicializa o Mock Server e o Servidor Web
REM ===============================================

echo.
echo ================================================
echo   SERVIDOR WEB MODBUS CLP
echo ================================================
echo.

REM Verifica se venv existe
IF NOT EXIST "venv\" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Execute install_and_run.bat primeiro.
    pause
    exit /b 1
)

REM Ativa o ambiente virtual
echo [1/3] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instala dependencias do Flask se necessario
echo [2/3] Verificando dependencias...
pip install flask flask-cors --quiet

REM Inicia o Mock Server em background
echo [3/3] Iniciando Mock Server...
start "Mock Server Modbus" cmd /k "venv\Scripts\activate.bat && python mock_server.py"

REM Aguarda 2 segundos para o Mock Server iniciar
timeout /t 2 /nobreak >nul

REM Inicia o Servidor Web
echo.
echo ================================================
echo   SERVIDOR WEB INICIADO!
echo ================================================
echo.
echo   Acesse: http://localhost:5000
echo.
echo   Press Ctrl+C para parar o servidor
echo ================================================
echo.

python web_server.py

REM Se o servidor for interrompido
echo.
echo Servidor Web encerrado.
pause
