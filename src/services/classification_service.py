from src.models.schemas import IntermediateClassification, DocumentCategory
from src.utils.logger import logger

def classify_text(text: str) -> IntermediateClassification:
    logger.info("Running intermediate rule-based classification")
    text_lower = text.lower()
    
    # Simple rule-based classifier
    invoice_keywords = ["invoice", "total due", "net 30", "tax", "amount"]
    identity_keywords = ["passport", "dob", "expire", "id", "gender", "sex"]
    medical_keywords = ["medical", "patient", "doctor", "diagnosis", "prescription", "symptoms"]
    
    inv_matches = [k for k in invoice_keywords if k in text_lower]
    id_matches = [k for k in identity_keywords if k in text_lower]
    med_matches = [k for k in medical_keywords if k in text_lower]
    
    # Determine winner
    counts = {
        DocumentCategory.INVOICE: len(inv_matches),
        DocumentCategory.IDENTITY_DOCUMENT: len(id_matches),
        DocumentCategory.MEDICAL_REPORT: len(med_matches)
    }
    
    best_category = DocumentCategory.UNKNOWN
    max_count = 0
    matched_keywords = []
    
    for cat, count in counts.items():
        if count > max_count:
            max_count = count
            best_category = cat
            if cat == DocumentCategory.INVOICE:
                matched_keywords = inv_matches
            elif cat == DocumentCategory.IDENTITY_DOCUMENT:
                matched_keywords = id_matches
            elif cat == DocumentCategory.MEDICAL_REPORT:
                matched_keywords = med_matches

    confidence = 0.0
    reasoning = "Not enough keywords matched to classify."
    
    if max_count >= 2:
        confidence = min(0.4 + (max_count * 0.1), 0.9)
        reasoning = f"Matched {max_count} keywords strongly indicating {best_category.value}."
    elif max_count == 1:
        confidence = 0.5
        reasoning = f"Weak match for {best_category.value} based on a single keyword."
        
    return IntermediateClassification(
        predicted_category=best_category,
        confidence=confidence,
        matched_keywords=matched_keywords,
        method="rule_based_keyword_matching",
        reasoning=reasoning
    )
