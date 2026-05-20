import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image

from utils.logger import get_logger

logger = get_logger(__name__)


class OCRService:

    def preprocess_image(self, img_array: np.ndarray) -> np.ndarray:
        """Grayscale → fast NL-means denoise → Otsu threshold."""
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_text(self, pdf_bytes: bytes, lang: str = "eng") -> str:
        """
        Render every page of *pdf_bytes* at 300 DPI, preprocess with OpenCV,
        then run Tesseract PSM-6 (uniform block of text).
        Returns the concatenated text of all pages.
        """
        logger.info("Starting OCR extraction")
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text: list[str] = []

        for page_num in range(doc.page_count):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")

            # Decode to numpy array for OpenCV
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_array is None:
                logger.warning(f"Page {page_num + 1}: could not decode image — skipping")
                full_text.append("")
                continue

            preprocessed = self.preprocess_image(img_array)
            pil_img = Image.fromarray(preprocessed)

            try:
                text = pytesseract.image_to_string(pil_img, lang=lang, config="--psm 6")
                full_text.append(text)
                logger.debug(f"Page {page_num + 1}: extracted {len(text)} chars")
            except pytesseract.TesseractError as e:
                logger.error(f"OCR error on page {page_num + 1}: {e}")
                full_text.append("")   # graceful fallback

        result = "\n".join(full_text)
        logger.info(f"OCR complete: {len(result)} total chars across {doc.page_count} pages")
        doc.close()
        return result
