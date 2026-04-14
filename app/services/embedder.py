from sentence_transformers import SentenceTransformer
from app.core.config import settings


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        vector = self.model.encode([query], normalize_embeddings=True)[0]
        return vector.tolist()


embedder = Embedder()