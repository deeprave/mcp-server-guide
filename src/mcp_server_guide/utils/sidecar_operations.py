"""Sidecar metadata file operations."""

import json
from pathlib import Path
from typing import Optional

from ..logging_config import get_logger
from ..models.document_metadata import DocumentMetadata
from .document_helpers import get_metadata_path

logger = get_logger()


def create_sidecar_metadata(document_path: Path, metadata: DocumentMetadata) -> None:
    """Create sidecar metadata file for a document."""
    sidecar_path = get_metadata_path(document_path)

    with open(sidecar_path, "w") as f:
        json.dump(metadata.model_dump(), f, indent=2)


def read_sidecar_metadata(document_path: Path) -> Optional[DocumentMetadata]:
    """Read sidecar metadata file for a document. Returns None if missing or invalid."""
    sidecar_path = get_metadata_path(document_path)

    try:
        with open(sidecar_path) as f:
            data = json.load(f)
        return DocumentMetadata(**data)
    except FileNotFoundError:
        logger.debug(f"Metadata file not found: {sidecar_path}")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Corrupted JSON metadata file {sidecar_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading metadata file {sidecar_path}: {e}")
        return None
