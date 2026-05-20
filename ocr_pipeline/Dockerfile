# ── Stage 1: system dependencies ─────────────────────────────────────────────
FROM python:3.11-slim AS base

# Install Tesseract + English language pack + OpenCV system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 2: Python deps ──────────────────────────────────────────────────────
FROM base AS deps

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/pkg -r requirements.txt

# ── Stage 3: application ──────────────────────────────────────────────────────
FROM base AS app

WORKDIR /app

# Copy installed packages
COPY --from=deps /install/pkg /usr/local

# Copy source
COPY . .

EXPOSE 8000

# Env defaults (override via docker run -e or compose env_file)
ENV REDIS_URL=memory://
ENV MOCK_LLM=false

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
