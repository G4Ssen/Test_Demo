import re
from dataclasses import dataclass, field

from utils.logger import get_logger

logger = get_logger(__name__)


# ── Classification rules ──────────────────────────────────────────────────────

CLASSIFICATION_RULES: dict[str, dict] = {
    "INVOICE": {
        "keywords": [
            "invoice", "bill to", "amount due", "total", "vat",
            "tax invoice", "payment terms",
        ],
        "patterns": [
            r"invoice\s*(n[°o#]|number|num)\s*[\d\-]+",
            r"(total|subtotal)\s*[:\s]\s*[\d,\.]+",
        ],
    },
    "IDENTITY": {
        "keywords": [
            "passport", "date of birth", "nationality",
            "expiry date", "dni", "national id",
        ],
        "patterns": [
            r"\b(passport|id)\s*(no|number)[:\s]*[A-Z0-9]+",
            r"\bborn\s+\d{2}/\d{2}/\d{4}",
        ],
    },
    "REPORT": {
        "keywords": [
            "executive summary", "findings", "recommendations",
            "conclusion", "methodology",
        ],
        "patterns": [
            r"section\s+\d+[\.:\s]+",
            r"figure\s+\d+[\.:\s]+",
        ],
    },
    "CONTRACT": {
        "keywords": [
            "agreement", "hereby", "parties", "clause",
            "obligations", "termination", "whereas",
        ],
        "patterns": [
            r"article\s+\d+[\.:\s]+",
            r"this\s+agreement\s+is\s+entered",
        ],
    },
}


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    matched_keywords: list = field(default_factory=list)
    method: str = "RULE_BASED"


class ClassifierService:

    def classify(self, text: str) -> ClassificationResult:
        text_lower = text.lower()
        scores: dict[str, dict] = {}

        for label, rules in CLASSIFICATION_RULES.items():
            keyword_hits = [kw for kw in rules["keywords"] if kw in text_lower]
            pattern_hits = [p for p in rules["patterns"] if re.search(p, text_lower)]
            total_possible = len(rules["keywords"]) + len(rules["patterns"])
            hit_count = len(keyword_hits) + len(pattern_hits)
            scores[label] = {
                "score": hit_count / total_possible if total_possible else 0.0,
                "keywords": keyword_hits,
            }

        best_label = max(scores, key=lambda lbl: scores[lbl]["score"])
        best = scores[best_label]

        if best["score"] < 0.15:
            logger.info("Rule-based classification → UNCLASSIFIED (score too low)")
            return ClassificationResult(
                label="UNCLASSIFIED",
                confidence=0.0,
                matched_keywords=[],
                method="RULE_BASED",
            )

        logger.info(
            f"Rule-based classification → {best_label} "
            f"(score={best['score']:.2f}, keywords={best['keywords']})"
        )
        return ClassificationResult(
            label=best_label,
            confidence=round(best["score"], 2),
            matched_keywords=best["keywords"],
            method="RULE_BASED",
        )
