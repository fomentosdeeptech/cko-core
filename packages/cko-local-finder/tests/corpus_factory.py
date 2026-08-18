"""Deterministic, standard-library-only synthetic corpus generation."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import zipfile

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "source"
DEFAULT_TEST_SIZE_LIMIT = 128
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _minimal_pdf() -> bytes:
    stream = b"BT /F1 12 Tf 72 720 Td (Synthetic local knowledge corpus) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    result = bytearray(b"%PDF-1.4\n%synthetic\n")
    offsets = [0]
    for number, payload in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode("ascii") + payload + b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    result.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    result.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(result)


def _minimal_docx() -> bytes:
    entries = {
        "[Content_Types].xml": b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        "_rels/.rels": b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        "word/document.xml": b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Synthetic local knowledge corpus</w:t></w:r></w:p><w:sectPr/></w:body></w:document>',
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o600 << 16
            archive.writestr(info, entries[name])
    return output.getvalue()


def materialize_corpus(root: Path, *, size_limit: int = DEFAULT_TEST_SIZE_LIMIT) -> list[dict[str, object]]:
    """Materialize the corpus below an explicit empty or existing test directory."""
    root = Path(root)
    if size_limit < 1:
        raise ValueError("size_limit must be positive")
    root.mkdir(parents=True, exist_ok=True)
    utf8 = (FIXTURE_ROOT / "sample_utf8.txt").read_bytes()
    markdown = (FIXTURE_ROOT / "sample_markdown.md").read_bytes()
    duplicate = "Conteúdo sintético duplicado byte a byte.\n".encode("utf-8")
    payloads = {
        "valid/sample_utf8.txt": utf8,
        "valid/sample_utf8_sig.txt": b"\xef\xbb\xbf" + utf8,
        "valid/sample.md": markdown,
        "valid/sample.pdf": _minimal_pdf(),
        "valid/sample.docx": _minimal_docx(),
        "edge/empty.txt": b"",
        "edge/oversized.txt": b"X" * (size_limit + 1),
        "corrupt/corrupt.pdf": b"%PDF-corrupt-synthetic\n",
        "corrupt/corrupt.docx": b"PK\x03\x04corrupt-synthetic",
        "unsupported/sample.bin": bytes(range(16)),
        "duplicates/original.txt": duplicate,
        "duplicates/copy.txt": duplicate,
    }
    conditions = {
        "edge/empty.txt": "empty", "edge/oversized.txt": "oversized",
        "corrupt/corrupt.pdf": "corrupt", "corrupt/corrupt.docx": "corrupt",
        "unsupported/sample.bin": "unsupported", "duplicates/original.txt": "duplicate",
        "duplicates/copy.txt": "duplicate",
    }
    manifest = []
    resolved_root = root.resolve()
    for relative, content in payloads.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.resolve().is_relative_to(resolved_root):
            raise ValueError("corpus path escapes root")
        destination.write_bytes(content)
        manifest.append({
            "path": relative,
            "case_type": conditions.get(relative, "valid"),
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    return manifest
