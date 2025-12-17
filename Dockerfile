# Usamos la versión slim para reducir el tamaño de ~1GB a ~150MB
FROM python:3.10-slim-bullseye

# Solo instalamos lo estrictamente necesario para la base de datos y utilidades básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Instalar 'uv' y sincronizar dependencias antes de copiar el código
# Esto aprovecha mejor el cache de Docker
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

# Copiar el resto del código
COPY . .

# Limpiar finales de línea del entrypoint y dar permisos
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]