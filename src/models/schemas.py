"""
Pydantic schemas for request/response validation.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentCategory(str, Enum):
    INVOICE = "invoice"
    IDENTITY_DOCUMENT = "identity_document"
    MEDICAL_REPORT = "medical_report"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the processing job")
    filename: str = Field(..., description="Original filename of the uploaded PDF")
    file_size_bytes: int = Field(..., description="Size of the uploaded file in bytes")
    page_count: int = Field(..., description="Number of pages detected")
    status: DocumentStatus = DocumentStatus.PENDING
    message: str = "File uploaded successfully. Use /process/{job_id} to start processing."


# ---------------------------------------------------------------------------
# OCR Stage
# ---------------------------------------------------------------------------

class OCROutput(BaseModel):
    raw_text: str = Field(..., description="Raw text extracted by the OCR engine")
    page_texts: List[str] = Field(default_factory=list, description="Per-page OCR output")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Average OCR confidence score")
    engine: str = Field(default="tesseract-mock", description="OCR engine used")
    warnings: List[str] = Field(default_factory=list, description="OCR warnings or anomalies")


# ---------------------------------------------------------------------------
# Post-Processing Stage
# ---------------------------------------------------------------------------

class PostProcessingOutput(BaseModel):
    cleaned_text: str = Field(..., description="Cleaned and normalized text")
    original_length: int = Field(..., description="Character count before cleaning")
    cleaned_length: int = Field(..., description="Character count after cleaning")
    transformations_applied: List[str] = Field(
        default_factory=list, description="List of normalization steps applied"
    )


# ---------------------------------------------------------------------------
# Intermediate Classification Stage
# ---------------------------------------------------------------------------

class IntermediateClassification(BaseModel):
    predicted_category: DocumentCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    matched_keywords: List[str] = Field(default_factory=list)
    method: str = Field(default="rule_based", description="Classification method used")
    reasoning: str = Field(default="", description="Brief reasoning for the classification")


# ---------------------------------------------------------------------------
# LLM Stage
# ---------------------------------------------------------------------------

class LLMClassification(BaseModel):
    label: DocumentCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="LLM reasoning for the classification")
    model: str = Field(default="gpt-4o-mini-mock", description="LLM model used")
    tokens_used: int = Field(default=0, description="Approximate token count")
    structured_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key entities extracted by the LLM (e.g., invoice number, patient name)",
    )


# ---------------------------------------------------------------------------
# Full Pipeline Result
# ---------------------------------------------------------------------------

class PipelineResult(BaseModel):
    job_id: str
    filename: str
    status: DocumentStatus
    ocr_output: Optional[OCROutput] = None
    post_processing: Optional[PostProcessingOutput] = None
    intermediate_classification: Optional[IntermediateClassification] = None
    llm_classification: Optional[LLMClassification] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    job_id: Optional[str] = None
