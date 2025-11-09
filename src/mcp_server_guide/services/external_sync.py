"""External change detection and async cleanup service."""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, Optional, Any
from ..constants import DOCUMENT_SUBDIR, METADATA_SUFFIX
from ..utils.sidecar_operations import read_sidecar_metadata, create_sidecar_metadata
from ..models.document_metadata import DocumentMetadata
from ..logging_config import get_logger
from ..utils.document_utils import generate_content_hash, detect_mime_type

logger = get_logger()

# TTL for cache entries (5 minutes)
CACHE_TTL = 300
VALID_SOURCE_TYPES = {"manual", "external", "template", "generated"}


def validate_existing_metadata(metadata: DocumentMetadata) -> bool:
    """Validate metadata fields are reasonable."""
    if not metadata.source_type or metadata.source_type not in VALID_SOURCE_TYPES:
        return False
    if metadata.content_hash and len(metadata.content_hash) != 64:  # SHA256 length
        return False
    return True


def create_metadata_with_checksum(metadata: DocumentMetadata) -> Dict[str, Any]:
    """Add checksum to metadata for integrity."""
    data = metadata.model_dump()
    checksum = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return {**data, "_checksum": checksum}


def verify_metadata_checksum(metadata_dict: Dict[str, Any]) -> bool:
    """Verify metadata checksum integrity."""
    if "_checksum" not in metadata_dict:
        return True  # No checksum to verify

    stored_checksum: str = metadata_dict.pop("_checksum")
    calculated_checksum = hashlib.sha256(json.dumps(metadata_dict, sort_keys=True).encode()).hexdigest()
    metadata_dict["_checksum"] = stored_checksum  # Restore for caller

    return stored_checksum == calculated_checksum


@dataclass
class ChangesCache:
    """Thread-safe changes cache with expiration."""

    _cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _ttl: int = CACHE_TTL

    async def add_change(self, key: str, entry: Dict[str, Any]) -> None:
        """Add a change entry with timestamp."""
        async with self._lock:
            self._cache[key] = {**entry, "timestamp": time.time()}

    async def get_changes(self, category_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get changes, cleaning expired entries first."""
        async with self._lock:
            current_time = time.time()
            # Remove expired entries
            expired = [k for k, v in self._cache.items() if current_time - v["timestamp"] > self._ttl]
            for k in expired:
                del self._cache[k]

            if category_dir:
                return {k: v.copy() for k, v in self._cache.items() if v.get("category") == category_dir}
            return {k: v.copy() for k, v in self._cache.items()}


# Module-level singleton
_cache = ChangesCache()
_cleanup_tasks: Set[asyncio.Task[None]] = set()
CACHE_TTL = 300


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
            # Validate existing metadata
            if not validate_existing_metadata(existing_metadata):
                logger.warning(f"Metadata for {doc_path} has invalid fields, resetting source_type")
                existing_metadata.source_type = "external"

            if existing_metadata.content_hash and existing_metadata.content_hash != current_hash:
                logger.warning(f"Content hash mismatch for {doc_path} - external modification detected")

            # Update hash and mime type
            updated_metadata = DocumentMetadata(
                source_type=existing_metadata.source_type, content_hash=current_hash, mime_type=current_mime
            )

            # Save updated metadata
            create_sidecar_metadata(doc_path, updated_metadata)

            return {"success": True, "modified": True}

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
                    logger.debug(f"Syncing modified document: {doc_path}")
                    await sync_document_metadata(doc_path)

                    # Log change in cache
                    cache_key = str(doc_path)
                    await _cache.add_change(
                        cache_key,
                        {
                            "action": "modified",
                            "category": category_dir,
                        },
                    )

    except Exception as e:
        logger.exception(f"Error during category cleanup for {category_dir}: {e}")


def schedule_cleanup_task(category_dir: str) -> None:
    """Schedule cleanup task for a category with proper lifecycle management."""
    task = asyncio.create_task(_cleanup_category_documents(category_dir))
    _cleanup_tasks.add(task)
    task.add_done_callback(lambda t: _cleanup_tasks.discard(t))


async def cancel_all_cleanup_tasks() -> None:
    """Cancel all running cleanup tasks."""
    for task in _cleanup_tasks.copy():
        task.cancel()

    if _cleanup_tasks:
        await asyncio.gather(*_cleanup_tasks, return_exceptions=True)
    _cleanup_tasks.clear()


async def get_recent_changes(category_dir: Optional[str] = None) -> Dict[str, Any]:
    """Get recent changes from cache, optionally filtered by category."""
    return await _cache.get_changes(category_dir)
