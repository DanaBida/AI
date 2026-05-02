#!/bin/sh
set -eu

echo "Checking whether ChromaDB needs seed data..."
python data/load_synthetic_data.py --if-empty

echo "Starting FastAPI service..."
exec uvicorn app:app --host 0.0.0.0 --port 8001
