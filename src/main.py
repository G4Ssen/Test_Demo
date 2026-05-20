import time
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from src.models.schemas import (
    UploadResponse, PipelineResult, DocumentStatus, ErrorResponse
)
from src.services.input_service import process_upload
from src.services.ocr_service import run_ocr
from src.services.postprocessing_service import clean_text
from src.services.classification_service import classify_text
from src.services.llm_service import run_llm_classification
from src.services import result_store
from src.utils.logger import logger

app = FastAPI(
    title="OCR Document Processing System",
    description="Simulated OCR pipeline with REST APIs for Karate testing",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document to start a processing job."""
    try:
        job_id, response = await process_upload(file)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="Internal Server Error", detail=str(e)).model_dump()
        )

async def _pipeline_task(job_id: str):
    start_time = time.time()
    logger.info(f"Starting pipeline for job {job_id}")
    
    job_data = result_store.get(job_id)
    if not job_data:
        logger.error(f"Job data not found for {job_id} in background task")
        return
        
    try:
        result_store.update(job_id, {"status": DocumentStatus.PROCESSING})
        
        filename = job_data["filename"]
        content = job_data.get("file_content", b"")
        
        # Step 1: OCR
        ocr_out = await run_ocr(job_id, filename, content)
        result_store.update(job_id, {"ocr_output": ocr_out.model_dump()})
        
        if not ocr_out.raw_text.strip():
            raise ValueError("OCR failed to extract any text.")
            
        # Step 2: Post-Processing
        cleaned_out = clean_text(ocr_out.raw_text)
        result_store.update(job_id, {"post_processing": cleaned_out.model_dump()})
        
        # Step 3: Intermediate Classification
        intermediate_out = classify_text(cleaned_out.cleaned_text)
        result_store.update(job_id, {"intermediate_classification": intermediate_out.model_dump()})
        
        # Step 4: LLM Classification
        llm_out = await run_llm_classification(cleaned_out.cleaned_text, intermediate_out)
        result_store.update(job_id, {"llm_classification": llm_out.model_dump()})
        
        # Finish
        processing_time = (time.time() - start_time) * 1000
        result_store.update(job_id, {
            "status": DocumentStatus.COMPLETED,
            "processing_time_ms": processing_time
        })
        logger.info(f"Pipeline completed for {job_id} in {processing_time:.2f}ms")
        
    except Exception as e:
        logger.error(f"Pipeline failed for {job_id}: {str(e)}")
        result_store.update(job_id, {
            "status": DocumentStatus.FAILED,
            "error": str(e)
        })

@app.post("/process/{job_id}", response_model=dict)
async def process_document(job_id: str, background_tasks: BackgroundTasks):
    """Trigger the processing pipeline for a given job ID. Runs asynchronously."""
    job_data = result_store.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job_data["status"] != DocumentStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Job is not pending. Current status: {job_data['status']}")
        
    background_tasks.add_task(_pipeline_task, job_id)
    return {"job_id": job_id, "message": "Processing started in background."}

@app.get("/classify/{job_id}")
async def get_classification(job_id: str):
    """Get just the classification results (intermediate + LLM)."""
    job_data = result_store.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job_data["status"] == DocumentStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Processing failed: {job_data.get('error')}")
        
    if job_data["status"] != DocumentStatus.COMPLETED:
        return JSONResponse(status_code=202, content={"status": job_data["status"], "message": "Processing not completed yet."})
        
    return {
        "job_id": job_id,
        "intermediate_classification": job_data.get("intermediate_classification"),
        "llm_classification": job_data.get("llm_classification")
    }

@app.get("/result/{job_id}", response_model=PipelineResult)
async def get_result(job_id: str):
    """Get the full processing pipeline result."""
    job_data = result_store.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Remove file_content from response to keep it clean
    response_data = {k: v for k, v in job_data.items() if k != "file_content"}
    return response_data
