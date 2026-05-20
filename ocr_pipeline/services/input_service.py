import fitz  # PyMuPDF
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile, HTTPException
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class InputService:

    async def validate_and_store(self, file: UploadFile) -> dict:
        logger.info(f"Received upload: {file.filename} (content_type={file.content_type})")

        # ── 1. MIME type validation ──────────────────────────────────────────
        if file.content_type not in settings.SUPPORTED_MIME:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Only PDF files are accepted.",
            )

        content = await file.read()

        # ── 2. Size validation ───────────────────────────────────────────────
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit (received {size_mb:.1f} MB).",
            )

        # ── 3. PDF structural validation ─────────────────────────────────────
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            pages = doc.page_count
            doc.close()
        except Exception as e:
            logger.error(f"PDF parse error for '{file.filename}': {e}")
            raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file.")

        if pages == 0:
            raise HTTPException(status_code=400, detail="PDF has no pages.")

        job_id = str(uuid.uuid4())
        logger.info(f"Job {job_id} created — file='{file.filename}', pages={pages}, size={size_mb:.2f}MB")

        return {
            "job_id": job_id,
            "content": content,
            "filename": file.filename,
            "pages": pages,
            "created_at": datetime.now(timezone.utc),
        }
