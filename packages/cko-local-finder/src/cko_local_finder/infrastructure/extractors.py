"""Safe text-only extractors for the ratified local formats."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import zipfile

from docx import Document
from pypdf import PdfReader

from cko_local_finder.domain.models import DiscoveredFile, ExtractionPolicy, ExtractionResult
from cko_local_finder.infrastructure.text import TextLimitError, normalize_text


class ExtractionError(RuntimeError):
    def __init__(self, code: str, message: str, *, observed_size: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.observed_size = observed_size


class _BaseExtractor:
    extensions: frozenset[str]
    name: str
    version: str

    def __init__(self, policy: ExtractionPolicy | None = None) -> None:
        self.policy = policy or ExtractionPolicy()

    def supports(self, source: DiscoveredFile) -> bool:
        return source.extension.lower() in self.extensions

    def _check_source(self, source: DiscoveredFile) -> Path:
        path = Path(source.absolute_path)
        observed = path.stat().st_size
        if observed != source.size_bytes:
            raise ExtractionError("SOURCE_CHANGED", "source size changed", observed_size=observed)
        if observed > self.policy.max_source_file_size:
            raise ExtractionError("SOURCE_TOO_LARGE", "source file size limit exceeded", observed_size=observed)
        return path

    def _normalize(self, value: str) -> str:
        try:
            return normalize_text(value, max_characters=self.policy.max_extracted_characters)
        except TextLimitError as exc:
            raise ExtractionError("TEXT_TOO_LARGE", "extracted text character limit exceeded",
                                  observed_size=exc.observed) from exc


class PlainTextExtractor(_BaseExtractor):
    extensions = frozenset({".txt", ".md", ".markdown"})
    name = "plain-text"
    version = "1"

    def extract(self, source: DiscoveredFile) -> ExtractionResult:
        path = self._check_source(source)
        payload = path.read_bytes()
        if len(payload) > self.policy.max_source_file_size:
            raise ExtractionError("SOURCE_TOO_LARGE", "source file size limit exceeded", observed_size=len(payload))
        encoding = "utf-8-sig" if payload.startswith(b"\xef\xbb\xbf") else self.policy.default_text_encoding
        try:
            text = payload.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ExtractionError("INVALID_ENCODING", "source is not valid UTF-8") from exc
        text = self._normalize(text)
        status = "EMPTY" if not text else "SUCCESS"
        return ExtractionResult(source.sha256, text, self.name, self.version,
                                (("encoding", encoding), ("characters", str(len(text)))), status)


class PdfTextExtractor(_BaseExtractor):
    extensions = frozenset({".pdf"})
    name = "pypdf"
    version = "1"

    def extract(self, source: DiscoveredFile) -> ExtractionResult:
        path = self._check_source(source)
        try:
            reader = PdfReader(path, strict=True)
            if reader.is_encrypted:
                try:
                    if not reader.decrypt(""):
                        raise ExtractionError("ENCRYPTED", "PDF requires a password")
                except ExtractionError:
                    raise
                except Exception as exc:
                    raise ExtractionError("ENCRYPTED", "PDF requires a password") from exc
            pages: list[str] = []
            empty_pages = 0
            for page in reader.pages:
                value = page.extract_text() or ""
                if not value:
                    empty_pages += 1
                pages.append(value)
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError("CORRUPT_PDF", "PDF could not be parsed") from exc
        text = self._normalize("\n\n".join(pages))
        status = "NO_TEXT" if not text.strip() else "SUCCESS"
        metadata = (("pages", str(len(pages))), ("pages_without_text", str(empty_pages)))
        return ExtractionResult(source.sha256, text, self.name, self.version, metadata, status)


class DocxExtractor(_BaseExtractor):
    extensions = frozenset({".docx"})
    name = "python-docx"
    version = "1"

    def _validate_archive(self, path: Path) -> None:
        try:
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                if len(entries) > self.policy.max_docx_archive_entries:
                    raise ExtractionError("DOCX_TOO_MANY_ENTRIES", "DOCX archive entry limit exceeded")
                total = sum(entry.file_size for entry in entries)
                if total > self.policy.max_docx_uncompressed_bytes:
                    raise ExtractionError("DOCX_UNCOMPRESSED_TOO_LARGE", "DOCX uncompressed size limit exceeded", observed_size=total)
                names = {entry.filename for entry in entries}
                for entry in entries:
                    pure = PurePosixPath(entry.filename)
                    if pure.is_absolute() or ".." in pure.parts or ":" in pure.parts[0]:
                        raise ExtractionError("UNSAFE_DOCX_PATH", "DOCX contains an unsafe archive path")
                if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                    raise ExtractionError("INVALID_DOCX_STRUCTURE", "DOCX structure is incomplete")
        except ExtractionError:
            raise
        except (OSError, zipfile.BadZipFile) as exc:
            raise ExtractionError("CORRUPT_DOCX", "DOCX could not be parsed") from exc

    def extract(self, source: DiscoveredFile) -> ExtractionResult:
        path = self._check_source(source)
        self._validate_archive(path)
        try:
            document = Document(path)
            blocks: list[str] = []
            for child in document.element.body.iterchildren():
                if child.tag.endswith("}p"):
                    blocks.append("".join(node.text or "" for node in child.iter() if node.tag.endswith("}t")))
                elif child.tag.endswith("}tbl"):
                    for row in child.iterchildren():
                        if row.tag.endswith("}tr"):
                            cells = ["".join(node.text or "" for node in cell.iter() if node.tag.endswith("}t"))
                                     for cell in row.iterchildren() if cell.tag.endswith("}tc")]
                            blocks.append("\t".join(cells))
        except Exception as exc:
            raise ExtractionError("CORRUPT_DOCX", "DOCX could not be parsed") from exc
        text = self._normalize("\n".join(blocks))
        status = "EMPTY" if not text.strip() else "SUCCESS"
        metadata = (("blocks", str(len(blocks))), ("archive_validated", "true"))
        return ExtractionResult(source.sha256, text, self.name, self.version, metadata, status)


class ExtractorRegistry:
    def __init__(self, extractors: tuple[_BaseExtractor, ...] | None = None,
                 policy: ExtractionPolicy | None = None) -> None:
        self.extractors = extractors or (PlainTextExtractor(policy), PdfTextExtractor(policy), DocxExtractor(policy))

    def select(self, source: DiscoveredFile) -> _BaseExtractor:
        for extractor in self.extractors:
            if extractor.supports(source):
                return extractor
        raise ExtractionError("UNSUPPORTED_FORMAT", "no extractor supports this extension")
