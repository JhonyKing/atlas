"""Bounded upload validation before any private content is parsed or indexed."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from zipfile import BadZipFile, ZipFile

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {
    "text/plain": {".txt"},
    "text/markdown": {".md", ".markdown"},
    "application/pdf": {".pdf"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {".docx"},
}


class UploadValidationError(ValueError):
    """Upload does not satisfy the bounded allowlist or signature checks."""


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    filename: str
    declared_content_type: str
    detected_content_type: str
    size_bytes: int
    content: bytes


def validate_upload(
    *,
    filename: str,
    declared_content_type: str,
    content: bytes,
) -> ValidatedUpload:
    if not filename or filename != filename.strip() or ".." in filename:
        raise UploadValidationError("invalid filename")
    if len(content) == 0 or len(content) > MAX_UPLOAD_BYTES:
        raise UploadValidationError("file size is outside the allowed bound")
    normalized_type = declared_content_type.casefold().strip()
    allowed_extensions = ALLOWED_TYPES.get(normalized_type)
    extension = "." + filename.rsplit(".", 1)[-1].casefold() if "." in filename else ""
    if allowed_extensions is None or extension not in allowed_extensions:
        raise UploadValidationError("content type is not allowlisted")
    if normalized_type == "application/pdf" and not content.startswith(b"%PDF-"):
        raise UploadValidationError("file signature does not match declared type")
    if normalized_type.endswith("wordprocessingml.document"):
        try:
            with ZipFile(BytesIO(content)) as archive:
                if "[Content_Types].xml" not in archive.namelist():
                    raise UploadValidationError("invalid docx package")
        except BadZipFile as exc:
            raise UploadValidationError("invalid docx package") from exc
    if normalized_type.startswith("text/"):
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UploadValidationError("text must be valid UTF-8") from exc
    return ValidatedUpload(filename, normalized_type, normalized_type, len(content), content)
