# ============================================================
# 🏗️ Stage 1: Build environment
# ============================================================
FROM python:3.10-bullseye AS builder

# Instala dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo lo necesario para instalar dependencias
COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen --no-dev

# ============================================================
# 🚀 Stage 2: Runtime environment
# ============================================================
FROM python:3.10-slim AS runtime

# Instala solo librerías del sistema necesarias para ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependencias ya instaladas del builder
COPY --from=builder /usr/local /usr/local

# Copia tu código fuente y los modelos
COPY . .
COPY models /root/.insightface/models

# Exponer el puerto y definir el comando de arranque
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
