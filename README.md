# cta_back — Base FastAPI

<p align="center">
  <img src="assets/logo.png" alt="CTA – Compra Tu Auto" width="180" />
</p>
<h1 align="center">CTA – Compra Tu Auto</h1>

Backend base con **FastAPI**, CORS listo para React y configuración por `.env`.
No se fuerza la conexión a la base (podés arrancar sin DB y sumarla después). Ya incluye ejemplo con **MySQL**.

---

## FastAPi sin docker

### Requisitos

- **Python 3.11+**
- **VS Code** (recomendado)
- **MySQL Server 8.x** (o 5.7)
- (Windows) PowerShell habilitado para scripts

### Extensiones VS Code

- Python (ms-python.python), Pylance, Black Formatter, Ruff
- (Opcional) Thunder Client, DotENV

---

### Pasos para correr el proyecto (Windows y Linux)

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

### 🧪 Cómo correr los tests (Windows y Linux)

1. **Instalar dependencias para test desde la raíz del proyecto**

```bash
pip install -r requirements-test.txt
```

2. **Activar el entorno virtual (si ya no estaba activo)**

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux
source .venv/bin/activate
```

3. **Comandos de test útiles**

```bash
# (corre todos)
pytest
# (mas verboso)
pytest -vv
# (silencioso)
pytest -q
# (un solo archivo)
pytest tests/test_favorites_service.py
# (solo el directorio bdd, verboso)
pytest -vv -k bdd
# (todo lo que hay en bdd)
pytest -q tests/bdd
# (todo lo que haya en el dir tests)
pytest -q tests
# (mas verboso)
pytest -vv -k tests
# (filtro por escenario)
pytest -vv -k "Password válido"
# (re-ejecutar solo los últimos fallos)
python -m pytest --lf
# (cortar al primer fallo)
python -m pytest -x
# (mostrar prints/logs en consola)
python -m pytest -vv -s
```

> Nota_1: los tests configuran el entorno a APP_ENV=test desde tests/conftest.py, por lo que no tenés que setear variables manualmente.
>
> Nota_2: Asegurate de correr los tests con el venv activo; en Windows es recomendable usar `python -m pytest` para evitar problemas de PATH.

---

### Scripts “1-click” (Windows)

```powershell
# En la carpeta del proyecto
powershell -ExecutionPolicy Bypass -File .\setup-cta_back.ps1   # crea .venv, instala deps, copia .env
powershell -ExecutionPolicy Bypass -File .\run-dev.ps1          # levanta la API
```

> Alternativa con CMD: `setup-cta_back.bat` y `run-dev.bat`.

---

### Primera vez: crear base y usuario en MySQL

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

## 🔐 Autenticación (JWT) y Roles

> Cambiar `SECRET_KEY` invalida todos los tokens existentes (los usuarios deben loguearse de nuevo).

El backend usa **JWT (HS256)**. La clave `SECRET_KEY` firma/verifica los tokens y **no debe publicarse**.

### 1) Variables de entorno

Agregá en tu `.env` (no versionar):

--- auth/jwt ---

SECRET_KEY=<GENERAR_CON_EL_COMANDO_DE_ABAJO>
ACCESS_TOKEN_EXPIRE_MINUTES=30
TOKEN_ALGORITHM=HS256

### 2) Generar una SECRET_KEY fuerte

- **Windows (PowerShell):**
  ```powershell
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

-**Linux/macOS:**

```python3 -
  import secrets; print(secrets.token_urlsafe(64))
```

### (alternativa) openssl rand -base64 48

Semilla del usuario Admin (solo una vez). El usuario Admin se agregar por db.

#### 1) Generar hash:

```
  python -c "from passlib.hash import bcrypt; print(bcrypt.hash('Admin123!'))"
```

#### 2) Insertar en MySQL:

```
USE appdb;
INSERT INTO users (email, password_hash, role, is_active)
VALUES ('admin@example.com', '<PEGA_HASH_AQUI>', 'admin', 1);
```

## 🚀 FastApi con Docker

Este proyecto utiliza **`just`** como un ejecutor de comandos para simplificar la gestión del entorno de Docker. El `justfile` en la raíz del proyecto contiene todas las recetas necesarias para interactuar con los servicios.

### Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

- **Docker y Docker Compose:** [Guía de instalación de Docker](https://docs.docker.com/engine/install/)
- **Just:** [Instrucciones de instalación de Just](https://www.google.com/search?q=https://github.com/casey/just%23installation)

### Comandos Principales

#### Iniciar el entorno

Para levantar todos los servicios definidos en `./devops/compose.yml` en segundo plano (modo detached).

- **Comando:**
  ```bash
  just up
  ```
- **Equivale a:** `docker-compose -f ./devops/compose.yml up -d`

---

#### Detener el entorno

Para detener y eliminar los contenedores, redes y volúmenes creados por `up`.

- **Comando:**
  ```bash
  just down
  ```
- **Equivale a:** `docker-compose -f ./devops/compose.yml down`

---

#### Ejecutar un comando en un servicio

Para ejecutar un comando dentro de un contenedor específico que ya está en funcionamiento.

- **Comando:**
  ```bash
  just exec [service] [command]
  ```
- **Acción:** Si no se especifican parámetros, la receta por defecto abre una shell (`bash`) en el servicio `app`.
- **Equivale a:** `docker-compose -f ./devops/compose.yml exec <service> <command>`

**Ejemplos de uso:**

- **Abrir una terminal en el contenedor por defecto (`app`):**
  ```bash
  just exec
  ```
- **Abrir una terminal `sh` en el servicio de la base de datos:**
  ```bash
  just exec service='database' command='sh'
  ```
- **Ejecutar la instalación de dependencias en el servicio `api`:**
  ```bash
  just exec service='api' command='npm install'
  ```

### Listar todos los comandos

Para ver una lista de todas las recetas disponibles y sus descripciones directamente desde la terminal, ejecuta:

```bash
just --list
```

### Ejecucion para todos los servicios

1. Para poder ejecutar se debe renombrar el `/devops/env.compose.example` por `/devops/.env.compose`

2. Ademas se debe ejecutar en el proyecto `CTA_Front` el comando de just: `just build_dev` y debe tener creado una imagen de nombre `cta_front_dev`

3. Ejecutar `just up` en el repositorio.

## Estructura del proyecto

```

app/
api/
v1/
endpoints/
ping.py
items.py # ← CRUD mínimo de ejemplo
router.py
core/
config.py
db/
base.py
session.py # engine lazy (no conecta hasta usarse)
models/
**init**.py
item.py # ← modelo de ejemplo
main.py # lifespan: crea tablas al iniciar
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
