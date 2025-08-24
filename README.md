# cta_back — Base FastAPI (sin Docker)

Backend base con **FastAPI**, CORS listo para React y configuración por `.env`.
No se fuerza la conexión a MySQL (podés arrancar sin DB y sumarla después).

---

## Requisitos

- **Python 3.11+**
- **VS Code** (recomendado)
- (Opcional) **MySQL nativo** si vas a conectar la DB
- (Windows) PowerShell habilitado para scripts (ver “Problemas comunes”)

## Extensiones VS Code

- Python (ms-python.python), Pylance, Black Formatter, Ruff
- (Opcional) Thunder Client, DotENV

---

## Pasos para correr el proyecto (Windows y Linux en un mismo flujo)

1. **Abrir en VS Code**

   - File → Open Folder… → `cta_back`
   - `Ctrl+Shift+P` → **Python: Select Interpreter** → elegí el del `.venv` si ya existe (si no, lo creás en el paso 2).

2. **Crear y activar el entorno virtual**

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Actualizar pip e instalar dependencias**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. **Crear el archivo de variables de entorno**

```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

5. **Levantar la API (modo desarrollo)**

```bash
uvicorn app.main:app --reload
# Navegá a: http://127.0.0.1:8000/docs
# Si el puerto 8000 está ocupado:
# uvicorn app.main:app --reload --port 8010
```

6. **(Opcional) Ejecutar con F5 en VS Code**
   - Ya viene `.vscode/launch.json` (debug listo).
   - Si VS Code no usa tu venv: `Ctrl+Shift+P` → _Python: Select Interpreter_ → `.venv`.

---

## Scripts “1‑click” (Windows)

Si preferís automatizar el setup y el arranque:

```powershell
# En la carpeta del proyecto
powershell -ExecutionPolicy Bypass -File .\setup-cta_back.ps1   # crea .venv, instala deps, copia .env
powershell -ExecutionPolicy Bypass -File .\run-dev.ps1          # levanta la API
```

> Alternativa con CMD: `setup-cta_back.bat` y `run-dev.bat`.

---

## Variables de entorno

Editá `.env` (creado desde `.env.example`) si necesitás cambiar algo:

```
DATABASE_URL=mysql+pymysql://appuser:apppass@127.0.0.1:3306/appdb
APP_NAME=CTA Backend
APP_VERSION=0.1.0
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

> Ajustá `CORS_ORIGINS` según el host/puerto del front en React.

---

## Estructura del proyecto

```
app/
  api/
    v1/
      endpoints/
        ping.py
      router.py
  core/
    config.py
  db/
    base.py
    session.py    # engine lazy (no conecta a DB hasta que lo uses)
  main.py
.vscode/
  launch.json
  settings.json
  tasks.json
requirements.txt
.env.example
```

---

## Conectar MySQL (cuando lo pida el TP)

1. Crear base y usuario en tu MySQL nativo:

```sql
CREATE DATABASE appdb DEFAULT CHARACTER SET utf8mb4;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppass';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

2. Ajustar `DATABASE_URL` en `.env` (usar `127.0.0.1` para TCP).
3. Usar `app/db/session.py` en endpoints/servicios y definir modelos SQLAlchemy.

_(Opcional)_ Paquetes útiles para auth/validación (instalalos en tu venv):

```bash
pip install email-validator passlib[bcrypt] python-jose[cryptography]
```

---

## Problemas comunes

- **Windows “running scripts is disabled”**  
  Ejecutar una vez:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
  ```
- **VS Code no toma el venv**  
  `Ctrl+Shift+P` → _Python: Select Interpreter_ → `.venv`.  
  Podés fijarlo en `.vscode/settings.json`:
  ```json
  "python.defaultInterpreterPath": ".venv\Scripts\python.exe",
  "python.terminal.activateEnvironment": true
  ```
- **Puerto ocupado**  
  `uvicorn app.main:app --reload --port 8010`
- **No encuentra paquetes**  
  Activar el venv antes de instalar/correr:
  - Windows: `.\.venv\Scripts\Activate.ps1`
  - Linux: `source .venv/bin/activate`

---

## Notas de versionado (`.gitignore`)

Versionar solo:

```
.vscode/*
!.vscode/launch.json
!.vscode/settings.json
!.vscode/tasks.json
```

Ignorar secretos/artefactos: `.env`, `.venv/`, `__pycache__/`, etc.
