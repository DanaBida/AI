"""ChromaDB client wrapper for managing property embeddings and retrieval."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from sentence_transformers import SentenceTransformer

try:
    from chromadb.config import Settings
except (ImportError, ModuleNotFoundError):
    Settings = None

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """Wrapper for ChromaDB operations: injection and search."""

    def __init__(
        self,
        db_path: str,
        collection_name: str,
        embedding_model_name: str,
        anonymized_telemetry: bool = False,
    ):
        """
        Initialize ChromaDB client.
        
        Args:
            db_path: Path to persistent ChromaDB storage
            collection_name: Name of the collection
            embedding_model_name: HuggingFace model name for embeddings
            anonymized_telemetry: Whether ChromaDB usage telemetry is enabled
        """
        self.db_path = str(Path(db_path))
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model_name
        self.anonymized_telemetry = anonymized_telemetry

        Path(self.db_path).mkdir(parents=True, exist_ok=True)

        logger.info("Loading embedding model: %s", embedding_model_name)
        self.embedding_model = SentenceTransformer(embedding_model_name)

        logger.info(
            "Initializing ChromaDB at %s (anonymized telemetry=%s)",
            self.db_path,
            self.anonymized_telemetry,
        )
        client_kwargs = {"path": self.db_path}
        if Settings is not None:
            client_kwargs["settings"] = Settings(
                anonymized_telemetry=self.anonymized_telemetry,
            )
        self.client = chromadb.PersistentClient(**client_kwargs)

        self.collection = None
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Get or create the collection."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info("Retrieved existing collection: %s", self.collection_name)
        except Exception:
            logger.info("Creating new collection: %s", self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def inject(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> int:
        """
        Inject documents into ChromaDB collection.
        
        Args:
            documents: List of text documents
            metadatas: List of metadata dicts (one per document)
            ids: List of unique IDs (one per document)
            
        Returns:
            Number of documents injected
        """
        if not documents or not metadatas or not ids:
            logger.warning("Empty documents, metadatas, or ids provided to inject()")
            return 0

        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("documents, metadatas, and ids must have same length")

        logger.info("Generating embeddings for %s documents", len(documents))
        embeddings = self.embedding_model.encode(documents)

        logger.info("Upserting %s documents into collection '%s'", len(documents), self.collection_name)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
        )

        count = self.collection.count()
        logger.info("Collection now contains %s documents", count)

        return len(documents)

    def search(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar properties in ChromaDB.
        
        Args:
            query_text: Query text to search
            top_k: Number of top results to return
            
        Returns:
            List of result dicts with keys: id, text, metadata, distance
        """
        if not query_text or not query_text.strip():
            logger.warning("Empty query text provided to search()")
            return []

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        logger.info("Searching for similar properties (top_k=%s)", top_k)
        query_embedding = self.embedding_model.encode([query_text])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )

        formatted_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            ids = results["ids"][0]
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []

            for i, doc_id in enumerate(ids):
                formatted_results.append({
                    "id": doc_id,
                    "text": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else None,
                })

        logger.info("Found %s similar properties", len(formatted_results))
        return formatted_results

    def get_count(self) -> int:
        """Get total document count in collection."""
        return self.collection.count()

    def delete_collection(self):
        """Delete the entire collection (use with caution)."""
        logger.warning("Deleting collection: %s", self.collection_name)
        self.client.delete_collection(name=self.collection_name)
        self.collection = None
