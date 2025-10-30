"""Shared document utilities."""

import hashlib
import mimetypes

# Initialize mimetypes and add common types that might be missing
mimetypes.init()
mimetypes.add_type("text/yaml", ".yaml")
mimetypes.add_type("text/yaml", ".yml")
mimetypes.add_type("text/markdown", ".markdown")


def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash of content."""
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def detect_mime_type(filename: str) -> str:
    """Detect MIME type using Python stdlib."""
    mime_type, _ = mimetypes.guess_type(filename, strict=False)
    return mime_type or "application/octet-stream"
