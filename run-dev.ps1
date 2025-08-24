$activate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activate) { . $activate } else { Write-Error "Primero ejecutá .\setup-cta_back.ps1"; exit 1 }
uvicorn app.main:app --reload --port 8000
