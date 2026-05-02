import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration container."""

    APP_NAME = os.getenv("APP_NAME", "image-analyzer")
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8002"))
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_RELOAD = os.getenv("APP_RELOAD", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

    MODEL_PATH = os.getenv("MODEL_PATH", "./models/efficientnet_multihead_best.pt")
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

    RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "./data/raw")
    PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "./data/processed")
    MODEL_DIR = os.getenv("MODEL_DIR", "./models")
    KAGGLE_DATASET = os.getenv("KAGGLE_DATASET", "galinakg/interior-design-images-and-metadata")
