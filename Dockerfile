FROM python:3.13-slim

# Evita archivos .pyc y fuerza salida de logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema necesarias para compilar drivers (mysqlclient/pymysql deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Carpeta de uploads locales (fallback si STORAGE_TYPE=local)
RUN mkdir -p app/static/uploads

EXPOSE 5000

# Healthcheck interno del contenedor (independiente del Target Group del ALB)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# gunicorn en vez del servidor de desarrollo de Flask
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "60", "run:app"]
