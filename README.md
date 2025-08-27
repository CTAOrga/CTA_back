# cta_back — Base FastAPI (sin Docker)

<p align="center">
  <img src="assets/logo.png" alt="CTA – Compra Tu Auto" width="180" />
</p>
<h1 align="center">CTA – Compra Tu Auto</h1>

Backend base con **FastAPI**, CORS listo para React y configuración por `.env`.
No se fuerza la conexión a la base (podés arrancar sin DB y sumarla después). Ya incluye ejemplo con **MySQL**.

---

## Requisitos

- **Python 3.11+**
- **VS Code** (recomendado)
- **MySQL Server 8.x** (o 5.7)
- (Windows) PowerShell habilitado para scripts

## Extensiones VS Code

- Python (ms-python.python), Pylance, Black Formatter, Ruff
- (Opcional) Thunder Client, DotENV

---

## Pasos para correr el proyecto (Windows y Linux)

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

5. **Configurar conexión a MySQL en `.env`**

```
DATABASE_URL=mysql+pymysql://appuser:AppPass!123@localhost:3306/appdb
APP_NAME=CTA Backend
APP_VERSION=0.1.0
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

> Nota: usamos **localhost** porque el usuario es `'appuser'@'localhost'`.

6. **Levantar la API (modo desarrollo)**

```bash
uvicorn app.main:app --reload
# Navegá a: http://127.0.0.1:8000/docs
# Si el puerto 8000 está ocupado:
# uvicorn app.main:app --reload --port 8010
```

7. **Probar el ejemplo**

- **POST** `/api/v1/items/` → body: `{ "name": "Primer item" }`
- **GET** `/api/v1/items/` → devuelve la lista de items

---

## Scripts “1-click” (Windows)

```powershell
# En la carpeta del proyecto
powershell -ExecutionPolicy Bypass -File .\setup-cta_back.ps1   # crea .venv, instala deps, copia .env
powershell -ExecutionPolicy Bypass -File .\run-dev.ps1          # levanta la API
```

> Alternativa con CMD: `setup-cta_back.bat` y `run-dev.bat`.

---

## Primera vez: crear base y usuario en MySQL

**Windows (PowerShell):**

```powershell
$SQL = @'
CREATE DATABASE IF NOT EXISTS appdb
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'AppPass!123';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
'@
mysql -u root -p -e $SQL
```

**Linux:**

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS appdb DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci; CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'AppPass!123'; GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost'; FLUSH PRIVILEGES;"
```

> Si tu server es 5.7, usá `utf8mb4_unicode_ci`.

---

## Estructura del proyecto

```
app/
  api/
    v1/
      endpoints/
        ping.py
        items.py          # ← CRUD mínimo de ejemplo
      router.py
  core/
    config.py
  db/
    base.py
    session.py            # engine lazy (no conecta hasta usarse)
  models/
    __init__.py
    item.py               # ← modelo de ejemplo
  main.py                 # lifespan: crea tablas al iniciar
.vscode/
  launch.json
  settings.json
  tasks.json
requirements.txt
.env.example
```

> El arranque usa **lifespan** (no `@on_event`), y crea tablas con `Base.metadata.create_all(...)`.

---

## Troubleshooting

**`ERROR 1045 (Access denied)`**

- Usá host correcto: si el usuario es `'appuser'@'localhost'`, tu URL debe usar **localhost** (no `127.0.0.1`).
- Reset de clave (como root):
  ```sql
  ALTER USER 'appuser'@'localhost' IDENTIFIED BY 'AppPass!123';
  FLUSH PRIVILEGES;
  ```

**`mysql` no se reconoce (Windows)**

- Agregá al PATH (ajustá la ruta si difiere):
  ```powershell
  $mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.0\bin"
  $cur = [Environment]::GetEnvironmentVariable("Path","User")
  if (-not $cur) { $cur = "" }
  if ($cur -notlike "*$mysqlBin*") {
    [Environment]::SetEnvironmentVariable("Path", ($cur.TrimEnd(';') + ";" + $mysqlBin), "User")
  }
  ```
  Cerrá y reabrí la terminal. `mysql --version` debería responder.

**CORS**

- Si el front corre en otro puerto/host, agregalo en `CORS_ORIGINS` y reiniciá el server.

**Puerto 8000 ocupado**

```bash
uvicorn app.main:app --reload --port 8010
```

**VS Code no toma el venv**

```json
// .vscode/settings.json
"python.defaultInterpreterPath": ".venv\Scripts\python.exe",
"python.terminal.activateEnvironment": true
```

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
