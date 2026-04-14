import time
from fastapi import APIRouter

from app.models.schemas import AskRequest, AskResponse, SourceChunk
from app.services.embedder import embedder
from app.services.vector_store import vector_store
from app.services.generator import generate_answer
from app.core.config import settings

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    t0 = time.perf_counter()

    # 1) Embed query
    q_vec = embedder.embed_query(payload.question)
    t1 = time.perf_counter()

    # 2) Retrieve top chunks
    hits = vector_store.search(
        query_vector=q_vec,
        top_k=payload.top_k or settings.TOP_K_DEFAULT,
        document_ids=payload.document_ids
    )
    t2 = time.perf_counter()

    # 3) Generate final answer
    contexts = [h["text"] for h in hits]
    answer = generate_answer(payload.question, contexts)
    t3 = time.perf_counter()

    sources = [
        SourceChunk(
            document_id=h["document_id"],
            chunk_id=h["chunk_id"],
            score=h["score"],
            text_preview=h["text"][:180]
        )
        for h in hits
    ]

    return AskResponse(
        answer=answer,
        sources=sources,
        latency_ms={
            "embedding_ms": round((t1 - t0) * 1000, 2),
            "retrieval_ms": round((t2 - t1) * 1000, 2),
            "generation_ms": round((t3 - t2) * 1000, 2),
            "total_ms": round((t3 - t0) * 1000, 2),
        }
    )