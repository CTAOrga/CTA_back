Write-Host "==> Creando y activando entorno virtual (.venv)..." -ForegroundColor Cyan
python -m venv .venv
$activate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activate) { . $activate } else { Write-Error "No se encontró $activate"; exit 1 }

Write-Host "==> Actualizando pip e instalando dependencias..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "==> Configurando .env..." -ForegroundColor Cyan
if (-Not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Se creó .env desde .env.example"
} else {
  Write-Host ".env ya existe, no se sobreescribe"
}

Write-Host "Listo. Podés ejecutar 'F5' en VS Code o correr './run-dev.ps1'." -ForegroundColor Green
