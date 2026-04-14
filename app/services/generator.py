from openai import OpenAI
from app.core.config import settings


def _build_client() -> OpenAI:
    # Prefer GROQ_API_KEY when provider is groq
    if settings.LLM_PROVIDER.lower() == "groq":
        api_key = settings.GROQ_API_KEY or settings.OPENAI_API_KEY
        return OpenAI(api_key=api_key, base_url=settings.LLM_BASE_URL)

    # fallback for OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


client = _build_client()


def generate_answer(question: str, contexts: list[str]) -> str:
    if not contexts:
        return "I don't know based on the provided documents."

    context_block = "\n\n---\n\n".join(contexts)

    system_prompt = (
        "You are a helpful QA assistant. "
        "Answer only using the provided context. "
        "If context is insufficient, say you don't know."
    )
    user_prompt = f"Question:\n{question}\n\nContext:\n{context_block}"

    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (resp.choices[0].message.content or "").strip()