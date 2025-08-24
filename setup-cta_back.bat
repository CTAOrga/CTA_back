@echo off
echo ==> Creando entorno virtual (.venv)
python -m venv .venv || goto :error

echo ==> Activando entorno
call .\.venv\Scripts\activate.bat || goto :error

echo ==> Actualizando pip e instalando dependencias
python -m pip install --upgrade pip || goto :error
pip install -r requirements.txt || goto :error

echo ==> Configurando .env
if not exist ".env" (
  copy ".env.example" ".env"
)

echo Listo. Ejecuta run-dev.bat o usa F5 en VS Code.
goto :eof

:error
echo Hubo un error durante la instalación.
exit /b 1
