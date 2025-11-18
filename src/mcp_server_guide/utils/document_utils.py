"""Shared document utilities."""

import hashlib
import mimetypes
import magic
from typing import Optional
from pathlib import Path
from ..logging_config import get_logger

logger = get_logger()

# Initialize mimetypes and add common types that might be missing
mimetypes.init()
mimetypes.add_type("text/yaml", ".yaml")
mimetypes.add_type("text/yaml", ".yml")
mimetypes.add_type("text/markdown", ".markdown")
mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("text/markdown", ".mdown")


def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash of content."""
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def detect_mime_type(filename: str) -> str:
    """Detect MIME type using Python stdlib (from filename only)."""
    mime_type, _ = mimetypes.guess_type(filename, strict=False)
    return mime_type or "application/octet-stream"


def detect_mime_type_from_content(content: str) -> str:
    """Detect MIME type from actual content using python-magic.

    Note: If content cannot be encoded as UTF-8, it's treated as binary
    and returns application/octet-stream.

    Args:
        content: File content as string

    Returns:
        Detected MIME type
    """
    try:
        # Convert string to bytes for magic detection
        content_bytes = content.encode("utf-8")
        mime_type = magic.from_buffer(content_bytes, mime=True)
        return mime_type
    except (UnicodeDecodeError, Exception) as e:
        logger.warning(f"Failed to detect mime-type from content ({type(e).__name__}): {e}")
        return "application/octet-stream"


def detect_best_mime_type(filename: str, content: str) -> str:
    """Detect best mime-type using both filename and content.

    Uses hybrid approach:
    - Detect from content (python-magic) - authoritative
    - Detect from filename (stdlib) - more specific
    - If both agree on category (e.g., text/*), use filename (more specific)
    - If they disagree, trust content detection

    Args:
        filename: Filename with extension
        content: File content

    Returns:
        Best detected MIME type
    """
    content_mime = detect_mime_type_from_content(content)
    filename_mime = detect_mime_type(filename)

    # If filename detection failed, use content
    if filename_mime == "application/octet-stream":
        return content_mime

    # Extract category (e.g., "text" from "text/plain")
    content_category = content_mime.split("/")[0]
    filename_category = filename_mime.split("/")[0]

    # If both agree on category, use filename (more specific)
    if content_category == filename_category:
        return filename_mime

    # Otherwise, trust content detection
    return content_mime


def get_extension_for_mime_type(mime_type: str) -> Optional[str]:
    """Get the primary file extension for a mime-type using stdlib.

    Args:
        mime_type: MIME type string (e.g., "text/markdown")

    Returns:
        Extension with leading dot (e.g., ".md") or None if no extension available
    """
    extensions = mimetypes.guess_all_extensions(mime_type, strict=False)
    return extensions[0] if extensions else None


def normalize_document_name(name: str, content: str) -> str:
    """Normalize document name by detecting mime-type from content and ensuring correct extension.

    Uses hybrid detection: prefers filename-based mime-type if it agrees with content category.

    Args:
        name: Document filename
        content: Document content (used to detect actual mime-type)

    Returns:
        Normalized filename with appropriate extension
    """
    # Detect best mime-type using hybrid approach
    detected_mime = detect_best_mime_type(name, content)

    # Get valid extensions for this mime-type
    valid_extensions = mimetypes.guess_all_extensions(detected_mime, strict=False)

    # Special case: octet-stream or no known extensions - keep name as-is
    if not valid_extensions or detected_mime == "application/octet-stream":
        return name

    path = Path(name)
    current_extension = path.suffix.lower()

    # If current extension is valid, keep it
    if current_extension and current_extension in valid_extensions:
        return name

    # Otherwise, append the first valid extension
    primary_extension = valid_extensions[0]
    return f"{name}{primary_extension}"
