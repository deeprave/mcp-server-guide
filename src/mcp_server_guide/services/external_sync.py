"""External change detection and async cleanup service."""

import asyncio
import time
from pathlib import Path
from typing import Dict, Set, Optional, Any
from ..constants import DOCUMENT_SUBDIR, METADATA_SUFFIX
from ..utils.sidecar_operations import read_sidecar_metadata, create_sidecar_metadata
from ..models.document_metadata import DocumentMetadata
from ..logging_config import get_logger
from ..utils.document_utils import generate_content_hash, detect_mime_type

logger = get_logger()

# Global cache state (shared across all contexts)
_changes_cache: Optional[Dict[str, Dict]] = None
_cleanup_tasks: Optional[Set[asyncio.Task]] = None
_cache_lock = asyncio.Lock()

# TTL for cache entries (5 minutes)
CACHE_TTL = 300


def get_changes_cache() -> Dict[str, Dict]:
    """Get or create the changes cache."""
    global _changes_cache
    if _changes_cache is None:
        _changes_cache = {}
    return _changes_cache


def get_cleanup_tasks() -> Set[asyncio.Task]:
    """Get or create the cleanup tasks set."""
    global _cleanup_tasks
    if _cleanup_tasks is None:
        _cleanup_tasks = set()
    return _cleanup_tasks


async def validate_document_integrity(doc_path: Path) -> Dict[str, Any]:
    """Validate document content hash matches metadata.

    Returns:
        Dict with success status and error details if validation fails
    """
    try:
        if not doc_path.exists():
            return {"success": False, "error": "Document file does not exist", "error_type": "not_found"}

        metadata = read_sidecar_metadata(doc_path)
        if not metadata:
            return {"success": False, "error": "Metadata file missing or invalid", "error_type": "metadata_missing"}

        current_content = doc_path.read_text(encoding="utf-8")
        current_hash = generate_content_hash(current_content)

        if current_hash == metadata.content_hash:
            return {"success": True}
        else:
            return {"success": False, "error": "Content hash mismatch", "error_type": "integrity_mismatch"}

    except Exception as e:
        logger.exception(f"Error validating document integrity for {doc_path}: {e}")
        return {"success": False, "error": str(e), "error_type": "unexpected"}


async def sync_document_metadata(doc_path: Path) -> Dict[str, Any]:
    """Sync document metadata with current content.

    Returns:
        Dict with success status and error details if sync fails
    """
    try:
        if not doc_path.exists():
            return {"success": False, "error": "Document file does not exist", "error_type": "not_found"}

        current_content = doc_path.read_text(encoding="utf-8")
        current_hash = generate_content_hash(current_content)
        current_mime = detect_mime_type(doc_path.name)

        if existing_metadata := read_sidecar_metadata(doc_path):
            # Update hash and mime type
            updated_metadata = DocumentMetadata(
                source_type=existing_metadata.source_type, content_hash=current_hash, mime_type=current_mime
            )

            # Save updated metadata
            create_sidecar_metadata(doc_path, updated_metadata)

            return {"success": True}

        return {"success": False, "error": "No existing metadata to sync", "error_type": "metadata_missing"}

    except Exception as e:
        logger.exception(f"Error syncing document metadata for {doc_path}: {e}")
        return {"success": False, "error": str(e), "error_type": "unexpected"}


async def _cleanup_category_documents(category_dir: str) -> None:
    """Clean up documents in a category directory."""
    try:
        category_path = Path(category_dir)
        docs_dir = category_path / DOCUMENT_SUBDIR

        if not docs_dir.exists():
            return

        for doc_path in docs_dir.iterdir():
            if doc_path.is_file() and not doc_path.name.endswith(METADATA_SUFFIX):
                # Check if document needs sync
                validation_result = await validate_document_integrity(doc_path)
                if not validation_result["success"]:
                    logger.info(f"Syncing modified document: {doc_path}")
                    await sync_document_metadata(doc_path)

                    # Log change in cache
                    async with _cache_lock:
                        cache_key = str(doc_path)
                        cache = get_changes_cache()
                        cache[cache_key] = {
                            "timestamp": time.time(),
                            "action": "modified",
                            "category": category_dir,
                        }

    except Exception as e:
        logger.exception(f"Error during category cleanup for {category_dir}: {e}")


async def _cleanup_expired_cache_entries() -> None:
    """Remove expired entries from changes cache."""
    async with _cache_lock:
        current_time = time.time()
        cache = get_changes_cache()
        expired_keys = [key for key, entry in cache.items() if current_time - entry["timestamp"] > CACHE_TTL]
        for key in expired_keys:
            del cache[key]


async def get_recent_changes(category_dir: Optional[str] = None) -> Dict:
    """Get recent changes from cache, optionally filtered by category."""
    await _cleanup_expired_cache_entries()

    async with _cache_lock:
        cache = get_changes_cache()
        if category_dir:
            return {key: entry for key, entry in cache.items() if entry["category"] == category_dir}
        return cache.copy()
