"""Script to load synthetic property data into ChromaDB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from lib.chromadb_client import ChromaDBClient

DATA_FILE = Path(__file__).parent / "properties.json"


def text_to_property_description(property_dict: dict) -> str:
    """Convert a property dict to the text stored in the vector database."""
    return (
        f"Property {property_dict['id']}: NIS {property_dict['price']}, "
        f"{property_dict['rooms']} rooms, {property_dict['bedrooms']} bed, "
        f"{property_dict['bathrooms']} bath, located in {property_dict['location']}, "
        f"condition {property_dict['condition']}. {property_dict['description']}"
    )


def _build_seed_payload() -> tuple[list[str], list[dict], list[str]]:
    """Load JSON property data and convert it into Chroma payload parts."""
    print(f"Loading synthetic data from {DATA_FILE}...")
    with DATA_FILE.open("r", encoding="utf-8") as file_handle:
        properties = json.load(file_handle)

    print(f"Loaded {len(properties)} properties")

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    print("Preparing properties...")
    for index, property_item in enumerate(properties, start=1):
        documents.append(text_to_property_description(property_item))
        metadatas.append(property_item)
        ids.append(property_item["id"])

        if index % 5 == 0:
            print(f"  Prepared {index}/{len(properties)} properties")

    return documents, metadatas, ids


def _create_db_client() -> ChromaDBClient:
    """Create the configured ChromaDB client."""
    return ChromaDBClient(
        db_path=Config.CHROMA_DB_PATH,
        collection_name=Config.CHROMA_COLLECTION_NAME,
        embedding_model_name=Config.EMBEDDING_MODEL,
        anonymized_telemetry=Config.CHROMA_ANONYMIZED_TELEMETRY,
    )


def load_synthetic_data() -> int:
    """Load synthetic properties into ChromaDB."""
    db_client = _create_db_client()
    documents, metadatas, ids = _build_seed_payload()
    injected = db_client.inject(documents=documents, metadatas=metadatas, ids=ids)

    print("\nSynthetic data loaded successfully!")
    print(f"   ChromaDB path: {Config.CHROMA_DB_PATH}")
    print(f"   Collection: {Config.CHROMA_COLLECTION_NAME}")
    print(f"   Total properties injected: {injected}")
    return injected


def load_synthetic_data_if_empty() -> int:
    """Load synthetic properties only when the configured collection is empty."""
    db_client = _create_db_client()
    current_count = db_client.get_count()
    if current_count > 0:
        print(
            f"Skipping seed because collection '{Config.CHROMA_COLLECTION_NAME}' "
            f"already contains {current_count} documents."
        )
        return 0

    documents, metadatas, ids = _build_seed_payload()
    injected = db_client.inject(documents=documents, metadatas=metadatas, ids=ids)

    print("\nSynthetic data loaded successfully!")
    print(f"   ChromaDB path: {Config.CHROMA_DB_PATH}")
    print(f"   Collection: {Config.CHROMA_COLLECTION_NAME}")
    print(f"   Total properties injected: {injected}")
    return injected


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Load synthetic properties into ChromaDB.")
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="Only seed when the configured Chroma collection has no documents.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        arguments = parse_args()
        if arguments.if_empty:
            load_synthetic_data_if_empty()
        else:
            load_synthetic_data()
    except Exception as exc:
        print(f"Error loading synthetic data: {exc}", file=sys.stderr)
        sys.exit(1)
