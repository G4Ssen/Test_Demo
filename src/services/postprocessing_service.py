import re
from src.models.schemas import PostProcessingOutput
from src.utils.logger import logger

def clean_text(raw_text: str) -> PostProcessingOutput:
    logger.info("Running post-processing on OCR text")
    
    if not raw_text:
        return PostProcessingOutput(
            cleaned_text="",
            original_length=0,
            cleaned_length=0,
            transformations_applied=["No text to process"]
        )
        
    original_length = len(raw_text)
    transformations = []
    
    # 1. Strip whitespace
    text = raw_text.strip()
    transformations.append("strip_whitespace")
    
    # 2. Normalize multiple newlines to max two
    if "\n\n\n" in text:
        text = re.sub(r'\n{3,}', '\n\n', text)
        transformations.append("normalize_newlines")
        
    # 3. Clean up weird characters commonly seen in OCR
    if "|" in text or "~" in text:
        text = text.replace("|", "I").replace("~", "-")
        transformations.append("clean_ocr_noise")
        
    # 4. Remove excessive spacing between words
    if "  " in text:
        text = re.sub(r'[ ]{2,}', ' ', text)
        transformations.append("remove_extra_spaces")
        
    cleaned_length = len(text)
    
    return PostProcessingOutput(
        cleaned_text=text,
        original_length=original_length,
        cleaned_length=cleaned_length,
        transformations_applied=transformations
    )
