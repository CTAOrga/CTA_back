# Imagen base oficial de Python actualizada
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar primero los requisitos para aprovechar la caché de Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código incluyendo .env
COPY . .

# Comando para ejecutar FastAPI con Gunicorn
CMD ["uvicorn", "app.main:app", "--reload", "--port", "8010"]