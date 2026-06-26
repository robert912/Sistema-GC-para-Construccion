@echo off
title GCIA - Servidor
echo ============================================
echo  GCIA - Sistema de Lecciones Aprendidas
echo  Iniciando...
echo ============================================
echo.

REM Check local GGUF model
if exist "%~dp0modelo\*.gguf" (
    echo Modelo IA: encontrado en carpeta modelo/
) else (
    echo AVISO: No se encontro modelo .gguf en carpeta modelo/
    echo La IA no estara disponible. Coloca tu archivo .gguf en la carpeta modelo/
)

echo.
echo Iniciando servidor backend...
echo Accede al sistema en: http://localhost:8000
echo Presiona Ctrl+C para detener el servidor.
echo.

REM Open browser after 2 seconds
start /min "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

cd /d "%~dp0backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if %errorlevel% neq 0 (
    echo.
    echo ERROR: El servidor no pudo iniciarse. Revisa los mensajes de arriba.
    pause
)
