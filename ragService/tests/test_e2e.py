"""End-to-end API shape tests."""

from pathlib import Path
import importlib.util
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

fake_chromadb = types.ModuleType("chromadb")
fake_chromadb.PersistentClient = object
sys.modules.setdefault("chromadb", fake_chromadb)

fake_sentence_transformers = types.ModuleType("sentence_transformers")


class _FakeSentenceTransformer:
    def __init__(self, *_args, **_kwargs):
        pass

    def encode(self, value):
        return value


fake_sentence_transformers.SentenceTransformer = _FakeSentenceTransformer
sys.modules.setdefault("sentence_transformers", fake_sentence_transformers)

HTTPX_AVAILABLE = importlib.util.find_spec("httpx") is not None
if HTTPX_AVAILABLE:
    from fastapi.testclient import TestClient
    import app as rag_app


@unittest.skipUnless(HTTPX_AVAILABLE, "httpx is required for FastAPI TestClient")
class ApiShapeTests(unittest.TestCase):
    def test_health_endpoint_returns_expected_keys(self):
        client = TestClient(rag_app.app)
        with patch("services.health_service.get_db_client") as get_db_client_mock:
            get_db_client_mock.return_value.embedding_model = object()
            get_db_client_mock.return_value.get_count.return_value = 22

            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("status", payload)
        self.assertIn("collection_count", payload)


if __name__ == "__main__":
    unittest.main()
