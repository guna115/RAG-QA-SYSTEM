import uuid
from pathlib import Path
from typing import Dict

from app.core.config import settings
from app.services.parser import parse_document
from app.services.chunker import chunk_text
from app.services.embedder import embedder
from app.services.vector_store import vector_store


# In-memory document status tracker
DOC_STATUS: Dict[str, Dict[str, str]] = {}


def new_document_id() -> str:
    return str(uuid.uuid4())


def start_document(document_id: str, filename: str) -> None:
    DOC_STATUS[document_id] = {
        "status": "processing",
        "detail": f"Started ingestion for {filename}"
    }


def complete_document(document_id: str) -> None:
    DOC_STATUS[document_id] = {
        "status": "done",
        "detail": "Ingestion completed successfully"
    }


def fail_document(document_id: str, detail: str) -> None:
    DOC_STATUS[document_id] = {
        "status": "failed",
        "detail": detail
    }


def ingest_document(document_id: str, file_path: str) -> None:
    """
    Background task function:
    1) Parse document
    2) Chunk text
    3) Embed chunks
    4) Save vectors + metadata in FAISS
    """
    try:
        path = Path(file_path)
        raw_text = parse_document(path)

        chunks = chunk_text(
            raw_text,
            chunk_size=settings.CHUNK_SIZE_CHARS,
            overlap=settings.CHUNK_OVERLAP_CHARS
        )

        if not chunks:
            raise ValueError("No text could be extracted from document.")

        vectors = embedder.embed_texts(chunks)

        metas = []
        for i, chunk in enumerate(chunks):
            metas.append({
                "document_id": document_id,
                "chunk_id": f"{document_id}-chunk-{i}",
                "text": chunk,
                "source_file": path.name
            })

        vector_store.add(vectors, metas)
        complete_document(document_id)

    except Exception as e:
        fail_document(document_id, str(e))