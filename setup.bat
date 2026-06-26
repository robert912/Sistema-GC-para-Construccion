@echo off
title GCIA - Setup
echo ============================================
echo  GCIA - Sistema de Lecciones Aprendidas
echo  Instalacion de dependencias
echo ============================================
echo.

echo [1/2] Instalando dependencias Python...
cd /d "%~dp0backend"

pip install fastapi uvicorn[standard] httpx numpy pydantic python-multipart aiofiles
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar dependencias base.
    pause
    exit /b 1
)

echo.
echo [2/2] Instalando llama-cpp-python ^(motor de IA local^)...

REM Buscar wheel precompilada en wheels/ o en la carpeta raiz
set WHL_FILE=
for %%f in ("%~dp0wheels\llama_cpp_python*.whl") do set WHL_FILE=%%f
if not defined WHL_FILE (
    for %%f in ("%~dp0llama_cpp_python*.whl") do set WHL_FILE=%%f
)

if defined WHL_FILE (
    echo Wheel encontrada: %WHL_FILE%
    pip install "%WHL_FILE%"
) else (
    echo No se encontro wheel local. Intentando desde PyPI...
    pip install llama-cpp-python
)

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo  AVISO: No se pudo instalar llama-cpp-python
    echo.
    echo  Descarga el archivo .whl desde:
    echo  https://github.com/abetlen/llama-cpp-python/releases
    echo  Busca: llama_cpp_python-X.X.X-py3-none-win_amd64.whl
    echo  Coloca el archivo en esta carpeta y vuelve a ejecutar setup.bat
    echo ============================================================
)

echo.
echo Setup completado.
echo Recuerda colocar tu archivo .gguf en la carpeta modelo/
echo Luego ejecuta: start.bat
echo.
pause
