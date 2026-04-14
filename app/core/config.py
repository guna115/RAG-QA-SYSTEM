from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "RAG QA System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    OPENAI_API_KEY: str = ""   # optional fallback
    GROQ_API_KEY: str = ""

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    LLM_PROVIDER: str = "groq"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama-3.1-8b-instant"

    CHUNK_SIZE_CHARS: int = 2000
    CHUNK_OVERLAP_CHARS: int = 300

    TOP_K_DEFAULT: int = 4
    MAX_UPLOAD_MB: int = 20


settings = Settings()