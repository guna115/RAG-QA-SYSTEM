import os
from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.rate_limit import limiter
from app.api.routes_documents import router as documents_router
from app.api.routes_qa import router as qa_router

# Reduce TensorFlow log noise
os.environ["TF_CPP_MIN_LOG_LEVEL"] = os.getenv("TF_CPP_MIN_LOG_LEVEL", "2")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(documents_router)
app.include_router(qa_router)


@app.get("/")
@limiter.limit("30/minute")
def health_check(request: Request):
    return {"message": "RAG QA API is running"}