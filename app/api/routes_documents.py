from pathlib import Path
import aiofiles

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.models.schemas import UploadResponse, StatusResponse
from app.services.ingestion import (
    DOC_STATUS,
    ingest_document,
    start_document,
    new_document_id,
)

router = APIRouter(prefix="/documents", tags=["documents"])

FILES_DIR = Path("app/storage/files")
FILES_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt are supported")

    document_id = new_document_id()
    save_path = FILES_DIR / f"{document_id}_{file.filename}"

    async with aiofiles.open(save_path, "wb") as out:
        content = await file.read()
        await out.write(content)

    start_document(document_id, file.filename)
    background_tasks.add_task(ingest_document, document_id, str(save_path))

    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="processing"
    )


@router.get("/{document_id}/status", response_model=StatusResponse)
def get_document_status(document_id: str):
    if document_id not in DOC_STATUS:
        raise HTTPException(status_code=404, detail="Document ID not found")

    data = DOC_STATUS[document_id]
    return StatusResponse(
        document_id=document_id,
        status=data["status"],
        detail=data.get("detail"),
    )