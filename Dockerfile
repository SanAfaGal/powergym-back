FROM python:3.10-bullseye

# ==============================================
# 1️⃣ Instalar dependencias del sistema
# ==============================================
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

# ==============================================
# 2️⃣ Crear carpeta para modelos e instalar InsightFace modelo
#    Este bloque se cachea mientras no cambie
# ==============================================
RUN mkdir -p /root/.insightface/models && \
    curl -L -o /root/.insightface/models/buffalo_l.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip && \
    unzip /root/.insightface/models/buffalo_l.zip -d /root/.insightface/models && \
    rm /root/.insightface/models/buffalo_l.zip

# ==============================================
# 3️⃣ Crear directorio de trabajo
# ==============================================
WORKDIR /app

# ==============================================
# 4️⃣ Copiar dependencias y sincronizar
# ==============================================
COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen --no-dev

# ==============================================
# 5️⃣ Copiar el código fuente
# ==============================================
COPY . .

# ==============================================
# 6️⃣ Exponer puerto y definir comando de inicio
# ==============================================
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
