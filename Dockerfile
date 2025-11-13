FROM python:3.10-bullseye

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias y sincronizar
COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen --no-dev

# Copiar el código fuente
COPY . .

# Normalizar line endings de entrypoint.sh (CRLF -> LF) y hacerlo ejecutable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Usar entrypoint para ejecutar migraciones antes de iniciar
ENTRYPOINT ["/app/entrypoint.sh"]
