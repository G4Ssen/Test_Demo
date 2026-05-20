import asyncio
from src.models.schemas import LLMClassification, DocumentCategory, IntermediateClassification
from src.utils.logger import logger

async def run_llm_classification(
    text: str, 
    intermediate_result: IntermediateClassification
) -> LLMClassification:
    logger.info("Running simulated LLM classification")
    
    # Simulate API call latency
    await asyncio.sleep(1.0)
    
    # In a real system, we would construct a prompt:
    # "Classify this text into: INVOICE, IDENTITY_DOCUMENT, MEDICAL_REPORT, UNKNOWN. 
    # Text: {text}. The intermediate classifier guessed {intermediate_result.predicted_category}."
    
    # Mock behavior based on the intermediate result or text content
    text_lower = text.lower()
    
    structured_data = {}
    label = DocumentCategory.UNKNOWN
    confidence = 0.5
    reasoning = "Could not confidently classify the document."
    
    if intermediate_result.predicted_category == DocumentCategory.INVOICE or "invoice" in text_lower:
        label = DocumentCategory.INVOICE
        confidence = 0.98
        reasoning = "Document contains clear invoice structure with total amount due, date, and invoice number."
        structured_data = {
            "extract_date": "2023-10-01",
            "total_amount": 1200.50,
            "vendor_name": "ACME Corp."
        }
    elif intermediate_result.predicted_category == DocumentCategory.IDENTITY_DOCUMENT or "passport" in text_lower:
        label = DocumentCategory.IDENTITY_DOCUMENT
        confidence = 0.99
        reasoning = "Matches standard international passport MRZ and field structure."
        structured_data = {
            "first_name": "JOHN",
            "last_name": "DOE",
            "document_type": "PASSPORT",
            "country": "GBR"
        }
    elif intermediate_result.predicted_category == DocumentCategory.MEDICAL_REPORT or "medical" in text_lower:
        label = DocumentCategory.MEDICAL_REPORT
        confidence = 0.96
        reasoning = "Text explicitly contains patient information, doctor notes, and a medical diagnosis."
        structured_data = {
            "patient_name": "Jane Smith",
            "doctor_name": "Dr. House",
            "diagnosis_keywords": ["headache", "fatigue"]
        }
        
    return LLMClassification(
        label=label,
        confidence=confidence,
        reasoning=reasoning,
        model="gpt-4o-mini-mock",
        tokens_used=len(text) // 4 + 150, # Rough mock
        structured_entities=structured_data
    )
