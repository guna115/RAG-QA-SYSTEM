# RAG-Based Question Answering System

A FastAPI + Streamlit project that allows users to upload documents (PDF/TXT) and ask questions using Retrieval-Augmented Generation (RAG).

## Features

- Upload documents (`.pdf`, `.txt`)
- Background ingestion pipeline
- Text chunking with overlap
- Embedding generation using Sentence Transformers
- Local vector search using FAISS
- LLM-based answer generation (Groq via OpenAI-compatible API)
- FastAPI endpoints with Pydantic request/response models
- Basic rate limiting (SlowAPI)
- Streamlit chat UI for end users

---

## Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Store:** FAISS (local)
- **LLM Provider:** Groq API
- **Validation:** Pydantic
- **Background Jobs:** FastAPI `BackgroundTasks`
- **Rate Limiting:** SlowAPI

---

## Project Structure

```text
rag-qa-system/
├─ app/
│  ├─ api/
│  │  ├─ routes_documents.py
│  │  └─ routes_qa.py
│  ├─ core/
│  │  ├─ config.py
│  │  └─ rate_limit.py
│  ├─ models/
│  │  └─ schemas.py
│  ├─ services/
│  │  ├─ chunker.py
│  │  ├─ embedder.py
│  │  ├─ generator.py
│  │  ├─ ingestion.py
│  │  ├─ parser.py
│  │  └─ vector_store.py
│  ├─ storage/
│  │  ├─ files/
│  │  └─ faiss/
│  └─ main.py
├─ docs/
│  └─ task_explanations.md
├─ streamlit_app.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

---

## Setup Instructions

### 1) Clone and enter project

```bash
git clone <your-repo-url>
cd rag-qa-system
```

### 2) Create virtual environment

```bash
python -m venv .venv
```

Activate:
- Windows PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment

Create `.env` from `.env.example` and set your Groq key:

```env
APP_NAME=RAG QA System
APP_VERSION=1.0.0

CHUNK_SIZE_CHARS=2000
CHUNK_OVERLAP_CHARS=300
TOP_K_DEFAULT=4
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

TF_CPP_MIN_LOG_LEVEL=2
```

---

## Run the Application

### Start backend (FastAPI)

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend docs:
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Start frontend (Streamlit)

In a second terminal:

```bash
streamlit run streamlit_app.py
```

---

## API Endpoints

### `POST /documents/upload`
Upload a `.pdf` or `.txt` file for background ingestion.

### `GET /documents/{document_id}/status`
Check ingestion status (`processing`, `done`, `failed`).

### `POST /qa/ask`
Ask a question using selected document IDs.

Example request:

```json
{
  "question": "What is this document about?",
  "document_ids": ["<document_id>"],
  "top_k": 4
}
```

---

## Notes on Design Decisions

See:

- `docs/task_explanations.md`

Includes:
- Chunk size selection rationale
- One retrieval failure case
- One tracked metric (latency + similarity score)

---
## Architecture Diagram

<img width="8192" height="1207" alt="Architecture Diagram" src="https://github.com/user-attachments/assets/25fdc556-1845-42c1-b722-4d65a27425e7" />


## Evaluation Alignment

This project directly addresses:
- Chunking strategy
- Retrieval quality
- API design
- Metrics awareness
- System explanation clarity

---

## Future Improvements

- Better reranking for ambiguous queries
- Hybrid retrieval (keyword + vector)
- Persistent metadata DB (SQLite/Postgres)
- Auth + per-user document isolation
- Docker deployment
