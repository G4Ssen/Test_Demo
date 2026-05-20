import json
from openai import OpenAI

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a document classifier. Given extracted text from a scanned document,
classify it into one of: INVOICE, IDENTITY, REPORT, CONTRACT, UNCLASSIFIED.

Respond ONLY with a valid JSON object in this exact format:
{
  "label": "<LABEL>",
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explaining your decision>"
}
Do not add markdown formatting or any other text."""

VALID_LABELS = {"INVOICE", "IDENTITY", "REPORT", "CONTRACT", "UNCLASSIFIED"}

# ── Mock LLM (used when MOCK_LLM=true or no API key) ─────────────────────────

def _mock_classify(intermediate_label: str) -> dict:
    """Return a deterministic fake LLM response — no API call made."""
    label = intermediate_label if intermediate_label in VALID_LABELS else "UNCLASSIFIED"
    return {
        "label": label,
        "confidence": 0.82,
        "reasoning": "[MOCK] Returning intermediate rule-based label as mock LLM output.",
        "model": "mock",
        "tokens_used": 0,
    }


# ── Real LLM service ──────────────────────────────────────────────────────────

class LLMService:

    def __init__(self):
        use_mock = settings.MOCK_LLM or not settings.OPENAI_API_KEY
        if use_mock:
            logger.warning("LLMService: running in MOCK mode — no real OpenAI calls will be made")
            self._mock = True
        else:
            self._mock = False
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def classify(self, cleaned_text: str, intermediate_label: str) -> dict:
        if self._mock:
            return _mock_classify(intermediate_label)

        # Truncate to ~3 000 chars to keep token usage reasonable
        truncated = cleaned_text[:3000]
        user_prompt = (
            f"Intermediate rule-based classification: {intermediate_label}\n\n"
            f"Document text:\n{truncated}"
        )

        logger.info(f"Sending classification request to {settings.OPENAI_MODEL}")

        try:
            response = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=200,
            )
            raw = response.choices[0].message.content.strip()
            result = json.loads(raw)

            # Validate label
            if result.get("label") not in VALID_LABELS:
                result["label"] = intermediate_label

            result["model"] = settings.OPENAI_MODEL
            result["tokens_used"] = response.usage.total_tokens
            logger.info(
                f"LLM classified as {result['label']} "
                f"(confidence={result.get('confidence')}, tokens={result['tokens_used']})"
            )
            return result

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"LLM response parse error: {e}")
            return {
                "label": intermediate_label,
                "confidence": 0.5,
                "reasoning": "Fallback to intermediate classification due to LLM parse error.",
                "model": settings.OPENAI_MODEL,
                "tokens_used": 0,
            }
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise
