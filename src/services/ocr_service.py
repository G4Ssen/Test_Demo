import json
from typing import Dict, Any
import asyncio

from src.models.schemas import OCROutput
from src.utils.logger import logger

async def run_ocr(job_id: str, filename: str, content: bytes) -> OCROutput:
    logger.info(f"Running mock OCR for job {job_id}")
    
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    filename_lower = filename.lower()
    
    # Mock behavior based on filename
    if "invoice" in filename_lower:
        raw_text = "INVOICE\n\nDate: 2023-10-01\nInv Num: #100234\n\nTotal Due:   $1,200.50\nCompany: ACME Corp.\nNotes: Plz pay by net 30.\nTHANK YOU"
        pages = [raw_text]
        confidence = 0.95
    elif "identity" in filename_lower or "passport" in filename_lower or "id" in filename_lower:
        raw_text = "PASSPORT\n\nCountry: GBR\nName: JOHN DOE\nDOB: 12 JAN 1980\nSex: M\nExpire: 14 FEB 2030\nP<GBRDOE<<JOHN<<<<<<<<<<<<<<<<<<\n"
        pages = [raw_text]
        confidence = 0.88
    elif "medical" in filename_lower or "report" in filename_lower:
        raw_text = "MEDICAL REPORT\n\nPatient: Jane Smith\nDoctor: Dr. House\nDate: 2023-11-15\n\nDIAGNOSIS:\nPatient reports mild headache and fatigue.\nBlood pressure: 120/80.\nRecommendation: Rest and hydration."
        pages = [raw_text]
        confidence = 0.92
    elif "error" in filename_lower or "corrupt" in filename_lower:
        logger.warning(f"Simulating OCR failure for {filename}")
        raw_text = ""
        pages = []
        confidence = 0.0
    else:
        raw_text = "Generic Document Text\nLine 1\nLine 2\nEnd of document."
        pages = [raw_text]
        confidence = 0.85
        
    warnings = []
    if confidence < 0.9:
        warnings.append("Low confidence OCR result. Some text may be inaccurate.")
        
    output = OCROutput(
        raw_text=raw_text,
        page_texts=pages,
        confidence=confidence,
        engine="tesseract-mock",
        warnings=warnings
    )
    
    return output
