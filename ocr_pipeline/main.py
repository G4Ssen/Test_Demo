import time
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.input_service import InputService
from services.ocr_service import OCRService
from services.postprocess_service import PostProcessService
from services.classifier_service import ClassifierService
from services.llm_service import LLMService
from store.result_store import ResultStore
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Service singletons ────────────────────────────────────────────────────────
input_svc = InputService()
ocr_svc = OCRService()
post_svc = PostProcessService()
classifier_svc = ClassifierService()
llm_svc = LLMService()
store = ResultStore()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="OCR Document Processing Pipeline",
    description=(
        "Modular pipeline: PDF upload → OCR extraction → text post-processing "
        "→ rule-based + LLM classification → Redis result store."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ── POST /api/v1/upload ───────────────────────────────────────────────────────

@app.post("/api/v1/upload", status_code=202, tags=["pipeline"])
async def upload(
    file: UploadFile = File(..., description="PDF file (max 20 MB)"),
    lang: str = "eng",
):
    """Upload a scanned PDF and queue it for processing."""
    result = await input_svc.validate_and_store(file)

    job = {
        "job_id":        result["job_id"],
        "status":        "QUEUED",
        "filename":      result["filename"],
        "pages":         result["pages"],
        "lang":          lang,
        "created_at":    result["created_at"].isoformat(),
        "pipeline_stages": {},
    }

    # Cache raw PDF bytes in memory (separate from the JSON-serialisable job)
    store.cache_pdf(result["job_id"], result["content"])
    await store.save(result["job_id"], job)

    return {k: v for k, v in job.items() if k != "pdf_bytes"}


# ── POST /api/v1/process/{job_id} ─────────────────────────────────────────────

@app.post("/api/v1/process/{job_id}", tags=["pipeline"])
async def process(job_id: str):
    """Run OCR extraction and post-processing on a queued job."""
    job = await store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "QUEUED":
        raise HTTPException(
            status_code=409,
            detail=f"Job status is {job['status']}, expected QUEUED",
        )

    pdf_bytes = store.get_pdf(job_id)
    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="PDF bytes not found in cache")

    # ── OCR ──────────────────────────────────────────────────────────────────
    t0 = time.time()
    raw_text = ocr_svc.extract_text(pdf_bytes, lang=job.get("lang", "eng"))
    ocr_ms = int((time.time() - t0) * 1000)

    # ── Post-process ─────────────────────────────────────────────────────────
    t1 = time.time()
    cleaned_text = post_svc.clean(raw_text)
    post_ms = int((time.time() - t1) * 1000)

    job.update({
        "status":      "PROCESSED",
        "ocr_raw":     raw_text,
        "ocr_cleaned": cleaned_text,
        "pipeline_stages": {
            "ocr":             {"status": "OK", "duration_ms": ocr_ms},
            "post_processing": {"status": "OK", "duration_ms": post_ms},
        },
    })
    await store.save(job_id, job)

    return {
        "job_id":             job_id,
        "status":             "PROCESSED",
        "ocr_raw":            raw_text,
        "ocr_cleaned":        cleaned_text,
        "word_count":         len(cleaned_text.split()),
        "processing_time_ms": ocr_ms + post_ms,
    }


# ── POST /api/v1/classify/{job_id} ───────────────────────────────────────────

@app.post("/api/v1/classify/{job_id}", tags=["pipeline"])
async def classify(job_id: str):
    """Run rule-based and LLM classification on a processed job."""
    job = await store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "PROCESSED":
        raise HTTPException(
            status_code=409,
            detail=f"Job status is {job['status']}, expected PROCESSED",
        )

    # ── Intermediate (rule-based) ─────────────────────────────────────────────
    t0 = time.time()
    intermediate = classifier_svc.classify(job["ocr_cleaned"])
    int_ms = int((time.time() - t0) * 1000)

    # ── LLM ──────────────────────────────────────────────────────────────────
    t1 = time.time()
    llm_result = llm_svc.classify(job["ocr_cleaned"], intermediate.label)
    llm_ms = int((time.time() - t1) * 1000)

    intermediate_dict = {
        "label":            intermediate.label,
        "method":           intermediate.method,
        "matched_keywords": intermediate.matched_keywords,
        "confidence":       intermediate.confidence,
    }

    stages = job.get("pipeline_stages", {})
    stages.update({
        "intermediate_classification": {"status": "OK", "duration_ms": int_ms},
        "llm_classification":          {"status": "OK", "duration_ms": llm_ms},
    })

    job.update({
        "status":                    "CLASSIFIED",
        "intermediate_classification": intermediate_dict,
        "llm_classification":        llm_result,
        "final_label":               llm_result["label"],
        "confidence":                llm_result["confidence"],
        "pipeline_stages":           stages,
        "completed_at":              datetime.now(timezone.utc).isoformat(),
    })
    await store.save(job_id, job)

    return {
        "job_id":                    job_id,
        "status":                    "CLASSIFIED",
        "intermediate_classification": intermediate_dict,
        "llm_classification":        llm_result,
    }


# ── GET /api/v1/result/{job_id} ───────────────────────────────────────────────

@app.get("/api/v1/result/{job_id}", tags=["pipeline"])
async def result(job_id: str):
    """Retrieve the complete pipeline result for a job."""
    job = await store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "QUEUED":
        # 202 with body (FastAPI doesn't raise 202, so return manually)
        return JSONResponse(
            status_code=202,
            content={"detail": "Job still processing", "job_id": job_id},
        )

    return {
        "job_id":          job_id,
        "status":          job["status"],
        "filename":        job.get("filename"),
        "created_at":      job.get("created_at"),
        "completed_at":    job.get("completed_at"),
        "pipeline_stages": job.get("pipeline_stages", {}),
        "ocr_cleaned":     job.get("ocr_cleaned", ""),
        "final_label":     job.get("final_label"),
        "confidence":      job.get("confidence"),
    }
