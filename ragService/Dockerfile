FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies required for:
# - torch
# - chromadb (hnswlib)
# - llama-cpp-python (C++ build)
# - sentence-transformers / tokenizers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    ninja-build \
    git \
    curl \
    libstdc++6 \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip tooling (important for torch + transformers wheels)
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .

# Install PyTorch first (prevents dependency solver chaos)
RUN pip install torch==2.0.1

# Install remaining requirements
RUN pip install -r requirements.txt

COPY . .

# Create runtime user and folders
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/artifacts/chroma_db /app/artifacts/models \
    && chmod +x /app/scripts/docker-start.sh \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://127.0.0.1:8001/health || exit 1

CMD ["/app/scripts/docker-start.sh"]