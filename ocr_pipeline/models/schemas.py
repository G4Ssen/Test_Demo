from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UploadResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    pages: int
    created_at: datetime


class ProcessResponse(BaseModel):
    job_id: str
    status: str
    ocr_raw: str
    ocr_cleaned: str
    word_count: int
    processing_time_ms: int


class IntermediateClassification(BaseModel):
    label: str
    method: str
    matched_keywords: list[str]
    confidence: float


class LLMClassification(BaseModel):
    label: str
    confidence: float
    reasoning: str
    model: str
    tokens_used: int


class ClassifyResponse(BaseModel):
    job_id: str
    status: str
    intermediate_classification: IntermediateClassification
    llm_classification: LLMClassification


class PipelineStage(BaseModel):
    status: str
    duration_ms: int


class FullResult(BaseModel):
    job_id: str
    status: str
    filename: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pipeline_stages: dict[str, PipelineStage] = Field(default_factory=dict)
    ocr_cleaned: str = ""
    final_label: Optional[str] = None
    confidence: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
