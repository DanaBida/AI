FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for:
# - torch / torchvision
# - pillow image support
# - general native builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Create user early
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Upgrade pip tooling (important for torch + transformers ecosystem stability)
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .

# Install torch first (prevents resolver issues)
RUN pip install \
    torch==2.4.1 torchvision==0.19.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/data/raw /app/data/processed /app/models \
    && chmod +x /app/scripts/docker-start.sh \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://127.0.0.1:8002/health || exit 1

ENTRYPOINT ["/app/scripts/docker-start.sh"]