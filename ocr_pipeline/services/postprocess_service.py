import re
import unicodedata

from utils.logger import get_logger

logger = get_logger(__name__)


class PostProcessService:
    """
    Cleans raw OCR text through a series of deterministic transformations:
      1. Unicode NFKC normalisation (fixes ligatures, smart quotes, etc.)
      2. OCR-specific character substitutions (0→O, l→1, |→I, 3→e)
      3. Whitespace normalisation
      4. Non-printable character removal
      5. ALL-CAPS short-line title-casing (section headers)
    """

    # Each key is a regex pattern, value is its replacement.
    OCR_CORRECTIONS: dict[str, str] = {
        r"\b0(?=[a-zA-Z])": "O",              # Leading zero → O  (e.g. 0CR → OCR)
        r"(?<=[a-zA-Z])0\b": "o",             # Trailing zero → o
        r"\bl\b": "1",                         # Standalone l → 1
        r"\|": "I",                            # Pipe → I
        r"(?<=[A-Za-z])3(?=[A-Za-z])": "e",   # 3 → e inside a word
    }

    def clean(self, raw_text: str) -> str:
        logger.info("Post-processing raw OCR text")
        text = raw_text

        # 1. Unicode normalisation
        text = unicodedata.normalize("NFKC", text)

        # 2. OCR corrections
        for pattern, replacement in self.OCR_CORRECTIONS.items():
            text = re.sub(pattern, replacement, text)

        # 3. Whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 4. Non-printable / non-ASCII characters (keep common currency symbols)
        text = re.sub(r"[^\x20-\x7E\n€£¥°]", "", text)

        # 5. Section-header title-casing
        lines: list[str] = []
        for line in text.split("\n"):
            stripped = line.strip()
            if len(stripped) < 30 and stripped.isupper() and stripped:
                lines.append(stripped.title())
            else:
                lines.append(line)
        text = "\n".join(lines)

        result = text.strip()
        logger.info(f"Post-processing complete: {len(result)} chars")
        return result
