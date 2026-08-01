"""Official technology-neutral enumerations for canonical documents."""

from enum import Enum


class DocumentType(str, Enum):
    DOCUMENT = "document"
    ARTICLE = "article"
    BOOK = "book"
    REPORT = "report"
    MANUAL = "manual"
    CONTRACT = "contract"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    EMAIL = "email"
    IMAGE = "image"
    TRANSCRIPT = "transcript"
    OTHER = "other"


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"
    XLSX = "xlsx"
    ODS = "ods"
    CSV = "csv"
    PPTX = "pptx"
    ODP = "odp"
    HTML = "html"
    XML = "xml"
    JSON = "json"
    MARKDOWN = "markdown"
    EMAIL = "email"
    IMAGE = "image"
    OCR = "ocr"
    AUDIO_TRANSCRIPT = "audio_transcript"
    VIDEO_TRANSCRIPT = "video_transcript"
    OTHER = "other"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REVIEWED = "reviewed"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class DocumentLanguageCode(str, Enum):
    UNDETERMINED = "und"
    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    LATIN = "la"
    MULTIPLE = "mul"


class DocumentSourceType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    IMPORTED = "imported"
    EMAIL = "email"
    WEB = "web"
    SCANNED = "scanned"
    GENERATED = "generated"
    OTHER = "other"


class IntegrityStatus(str, Enum):
    UNKNOWN = "unknown"
    VERIFIED = "verified"
    MISMATCH = "mismatch"
    UNAVAILABLE = "unavailable"


__all__ = [
    "DocumentFormat", "DocumentLanguageCode", "DocumentSourceType",
    "DocumentStatus", "DocumentType", "IntegrityStatus",
]
