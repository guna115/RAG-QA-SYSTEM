import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import faiss
import numpy as np


FAISS_DIR = Path("app/storage/faiss")
FAISS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = FAISS_DIR / "index.faiss"
META_FILE = FAISS_DIR / "metadata.json"


class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if INDEX_FILE.exists() and META_FILE.exists():
            self.index = faiss.read_index(str(INDEX_FILE))
            self.metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
        else:
            self.index = None
            self.metadata = []

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(INDEX_FILE))
        META_FILE.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add(self, vectors: List[List[float]], metas: List[Dict[str, Any]]) -> None:
        if not vectors:
            return

        xb = np.array(vectors, dtype="float32")
        dim = xb.shape[1]

        if self.index is None:
            # Using inner-product with normalized vectors ~= cosine similarity
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(xb)
        self.metadata.extend(metas)
        self._save()

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if self.index is None or len(self.metadata) == 0:
            return []

        xq = np.array([query_vector], dtype="float32")
        # fetch extra then filter by doc_id if needed
        fetch_k = min(max(top_k * 5, top_k), len(self.metadata))
        scores, indices = self.index.search(xq, fetch_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            meta = self.metadata[idx]

            if document_ids and meta["document_id"] not in document_ids:
                continue

            results.append({
                "score": float(score),
                **meta
            })

            if len(results) >= top_k:
                break

        return results


vector_store = VectorStore()