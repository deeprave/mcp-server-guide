"""Document CRUD operations for managed documents."""

import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from ..constants import DOCUMENT_SUBDIR
from ..models.document_metadata import DocumentMetadata
from ..services.sidecar_operations import create_sidecar_metadata, read_sidecar_metadata
from ..services.document_helpers import get_metadata_path
from ..logging_config import get_logger

logger = get_logger()


def _validate_document_name(name: str) -> bool:
    """Validate document name for security and filesystem compatibility."""
    if not name or len(name) > 255:
        return False
    # Prevent path traversal
    if "/" in name or "\\" in name or name == "..":
        return False
    # Prevent hidden files and reserved names
    if name.startswith(".") or name.lower() in ("con", "prn", "aux", "nul"):
        return False
    return True


def _validate_content_size(content: str, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate content size (default 10MB limit)."""
    return len(content.encode("utf-8")) <= max_size


def _detect_mime_type(filename: str) -> str:
    """Detect MIME type from file extension."""
    suffix = Path(filename).suffix.lower()
    mime_types = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".rst": "text/x-rst",
        ".adoc": "text/asciidoc",
    }
    return mime_types.get(suffix, "text/plain")


def _generate_content_hash(content: str) -> str:
    """Generate SHA256 hash of content."""
    return f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"


def _generate_document_uri(category_dir: str, name: str) -> str:
    """Generate guide:// URI for document."""
    return f"guide://{Path(category_dir).name}/{DOCUMENT_SUBDIR}/{name}"


async def create_mcp_document(
    category_dir: str, name: str, content: str, source_type: str = "manual", mime_type: Optional[str] = None
) -> Dict[str, Any]:
    """Create new server document in category/__docs__/ with metadata."""
    # Validate inputs
    if not _validate_document_name(name):
        return {"success": False, "error": f"Invalid document name: {name}", "error_type": "validation"}

    if not _validate_content_size(content):
        return {"success": False, "error": "Document content too large", "error_type": "validation"}

    try:
        category_path = Path(category_dir)
        docs_dir = category_path / DOCUMENT_SUBDIR
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create document file
        doc_path = docs_dir / name
        doc_path.write_text(content, encoding='utf-8')

        # Generate metadata
        if mime_type is None:
            mime_type = _detect_mime_type(name)

        content_hash = _generate_content_hash(content)

        metadata = DocumentMetadata(source_type=source_type, content_hash=content_hash, mime_type=mime_type)

        # Create sidecar metadata
        create_sidecar_metadata(doc_path, metadata)

        # Generate URI
        uri = _generate_document_uri(category_dir, name)

        return {
            "success": True,
            "message": f"Document '{name}' created successfully",
            "uri": uri,
            "path": str(doc_path),
            "metadata": metadata.model_dump(),
        }

    except FileNotFoundError as e:
        return {"success": False, "error": f"Directory not found: {str(e)}", "error_type": "not_found"}
    except PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "error_type": "permission"}
    except OSError as e:
        return {"success": False, "error": f"File system error: {str(e)}", "error_type": "filesystem"}
    except Exception as e:
        logger.exception("Unexpected error in create_mcp_document")
        return {"success": False, "error": f"Unexpected error: {str(e)}", "error_type": "unexpected"}


async def update_mcp_document(category_dir: str, name: str, content: str) -> Dict[str, Any]:
    """Update existing server document in category/__docs__/."""
    # Validate inputs
    if not _validate_document_name(name):
        return {"success": False, "error": f"Invalid document name: {name}", "error_type": "validation"}

    if not _validate_content_size(content):
        return {"success": False, "error": "Document content too large", "error_type": "validation"}

    try:
        category_path = Path(category_dir)
        docs_dir = category_path / DOCUMENT_SUBDIR
        doc_path = docs_dir / name

        # Check if document exists
        if not doc_path.exists():
            return {"success": False, "error": f"Document '{name}' does not exist", "error_type": "not_found"}

        # Read existing metadata to preserve settings
        existing_metadata = read_sidecar_metadata(doc_path)
        if existing_metadata is None:
            # Create default metadata if missing
            existing_metadata = DocumentMetadata(
                source_type="manual", content_hash="", mime_type=_detect_mime_type(name)
            )

        # Update document content
        doc_path.write_text(content, encoding='utf-8')

        # Update metadata with new content hash
        new_content_hash = _generate_content_hash(content)
        updated_metadata = DocumentMetadata(
            source_type=existing_metadata.source_type,
            content_hash=new_content_hash,
            mime_type=existing_metadata.mime_type,
        )

        # Update sidecar metadata
        create_sidecar_metadata(doc_path, updated_metadata)

        # Generate URI
        uri = _generate_document_uri(category_dir, name)

        return {
            "success": True,
            "message": f"Document '{name}' updated successfully",
            "uri": uri,
            "path": str(doc_path),
            "metadata": updated_metadata.model_dump(),
        }

    except FileNotFoundError as e:
        return {"success": False, "error": f"Document or directory not found: {str(e)}", "error_type": "not_found"}
    except PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "error_type": "permission"}
    except OSError as e:
        return {"success": False, "error": f"File system error: {str(e)}", "error_type": "filesystem"}
    except Exception as e:
        logger.exception("Unexpected error in update_mcp_document")
        return {"success": False, "error": f"Unexpected error: {str(e)}", "error_type": "unexpected"}


async def delete_mcp_document(category_dir: str, name: str) -> Dict[str, Any]:
    """Delete server document and metadata from category/__docs__/."""
    # Validate inputs
    if not _validate_document_name(name):
        return {"success": False, "error": f"Invalid document name: {name}", "error_type": "validation"}

    try:
        category_path = Path(category_dir)
        docs_dir = category_path / DOCUMENT_SUBDIR
        doc_path = docs_dir / name

        # Check if document exists
        if not doc_path.exists():
            return {"success": False, "error": f"Document '{name}' does not exist", "error_type": "not_found"}

        # Remove document file
        doc_path.unlink()

        # Remove metadata file if it exists
        metadata_path = get_metadata_path(doc_path)
        if metadata_path.exists():
            metadata_path.unlink()

        return {"success": True, "message": f"Document '{name}' deleted successfully"}

    except FileNotFoundError as e:
        return {"success": False, "error": f"Document not found: {str(e)}", "error_type": "not_found"}
    except PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "error_type": "permission"}
    except OSError as e:
        return {"success": False, "error": f"File system error: {str(e)}", "error_type": "filesystem"}
    except Exception as e:
        logger.exception("Unexpected error in delete_mcp_document")
        return {"success": False, "error": f"Unexpected error: {str(e)}", "error_type": "unexpected"}
