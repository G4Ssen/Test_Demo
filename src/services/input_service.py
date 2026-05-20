import uuid
from typing import Tuple

from fastapi import UploadFile, HTTPException

from src.models.schemas import UploadResponse, DocumentStatus
from src.services.result_store import save
from src.utils.logger import logger


async def process_upload(file: UploadFile) -> Tuple[str, UploadResponse]:
    logger.info(f"Received upload request for file: {file.filename}")

    if not file.filename.lower().endswith(".pdf"):
        logger.error(f"Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        logger.error("Uploaded file is empty.")
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file_size > 10 * 1024 * 1024:  # 10 MB limit
        logger.error(f"File size exceeds limit: {file_size} bytes")
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    # Mock page detection logic based on file size or predefined names for simulation
    page_count = 1
    if "multi" in file.filename.lower():
        page_count = 3
    elif file_size > 50000:
        page_count = 2

    job_id = str(uuid.uuid4())
    logger.info(f"Generated job_id: {job_id} for file: {file.filename}")

    # Store initial state
    save(job_id, {
        "job_id": job_id,
        "filename": file.filename,
        "status": DocumentStatus.PENDING,
        "ocr_output": None,
        "post_processing": None,
        "intermediate_classification": None,
        "llm_classification": None,
        "file_content": content # Keeping in memory for simulation
    })

    response = UploadResponse(
        job_id=job_id,
        filename=file.filename,
        file_size_bytes=file_size,
        page_count=page_count
    )

    return job_id, response
