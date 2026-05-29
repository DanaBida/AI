"""
Centralized configuration for LangGraph Agent service.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/models",
    )
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8001")
    IMAGE_ANALYZER_URL = os.getenv("IMAGE_ANALYZER_URL", "http://localhost:8002")
    EXTERNAL_API_TIMEOUT_SECONDS = int(os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "600"))
    AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    AGENT_LOG_LEVEL = os.getenv("AGENT_LOG_LEVEL", "INFO")
    MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "5000"))
