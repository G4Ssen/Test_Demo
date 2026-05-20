from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSED = "PROCESSED"
    CLASSIFIED = "CLASSIFIED"
    FAILED = "FAILED"


class DocLabel(str, Enum):
    INVOICE = "INVOICE"
    IDENTITY = "IDENTITY"
    REPORT = "REPORT"
    CONTRACT = "CONTRACT"
    UNCLASSIFIED = "UNCLASSIFIED"


class ClassificationMethod(str, Enum):
    RULE_BASED = "RULE_BASED"
    LLM = "LLM"
