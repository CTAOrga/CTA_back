@echo off
if not exist ".venv\Scripts\activate.bat" (
  echo Primero ejecuta setup-cta_back.bat
  exit /b 1
)
call .\.venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000
