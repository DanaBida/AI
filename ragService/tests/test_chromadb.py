"""Smoke tests for ChromaDB client contract."""

from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

fake_chromadb = types.ModuleType("chromadb")
fake_chromadb.PersistentClient = object
sys.modules.setdefault("chromadb", fake_chromadb)

fake_chromadb_config = types.ModuleType("chromadb.config")


class _FakeSettings:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


fake_chromadb_config.Settings = _FakeSettings
sys.modules.setdefault("chromadb.config", fake_chromadb_config)

fake_sentence_transformers = types.ModuleType("sentence_transformers")


class _FakeSentenceTransformer:
    def __init__(self, *_args, **_kwargs):
        pass

    def encode(self, value):
        return value


fake_sentence_transformers.SentenceTransformer = _FakeSentenceTransformer
sys.modules.setdefault("sentence_transformers", fake_sentence_transformers)

from lib.chromadb_client import ChromaDBClient


class ChromaClientContractTests(unittest.TestCase):
    def test_chromadb_client_rejects_invalid_top_k_without_initialization(self):
        client = ChromaDBClient.__new__(ChromaDBClient)
        client.collection = None
        client.embedding_model = None

        with self.assertRaises(ValueError):
            client.search("query", top_k=0)

    def test_chromadb_client_disables_telemetry_by_default(self):
        fake_collection = object()

        class _FakePersistentClient:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def get_collection(self, name):
                raise RuntimeError("missing")

            def get_or_create_collection(self, name, metadata):
                return fake_collection

        with patch("lib.chromadb_client.chromadb.PersistentClient", _FakePersistentClient):
            client = ChromaDBClient(
                db_path="db",
                collection_name="properties",
                embedding_model_name="mini-model",
            )

        settings = client.client.kwargs.get("settings")
        self.assertIsNotNone(settings)
        self.assertEqual(
            settings.kwargs.get("anonymized_telemetry"),
            False,
        )
        self.assertIs(client.collection, fake_collection)


if __name__ == "__main__":
    unittest.main()
