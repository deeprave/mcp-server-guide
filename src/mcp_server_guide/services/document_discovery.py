"""Document discovery for managed documents."""

import json
from pathlib import Path
from typing import Dict, List
from ..project_config import Category
from ..models.document_info import DocumentInfo
from ..logging_config import get_logger
from .document_helpers import (
    get_docs_dir,
    is_document_file,
    get_metadata_path,
    DOCUMENT_EXTENSIONS,
)
from ..constants import DOCUMENT_SUBDIR

logger = get_logger()


def get_category_documents_by_path(category_dir: Path) -> List[DocumentInfo]:
    """Discover all managed documents in category directory's DOCUMENT_SUBDIR."""
    docs_dir = category_dir / DOCUMENT_SUBDIR

    if not docs_dir.exists():
        return []

    documents = []

    for file_path in docs_dir.rglob("*"):
        if file_path.is_file() and is_document_file(file_path):
            metadata_path = get_metadata_path(file_path)

            # Try to read metadata, use empty dict if not available
            metadata = {}
            if metadata_path.exists():
                try:
                    with open(metadata_path) as f:
                        metadata = json.load(f)
                except (json.JSONDecodeError, OSError):
                    logger.warning(f"Failed to read metadata for {file_path}")

            # Create DocumentInfo with correct fields
            doc_info = DocumentInfo(
                path=file_path,
                metadata_path=metadata_path,
                metadata=metadata,
            )
            documents.append(doc_info)

    return documents


def get_category_documents(category: Category) -> Dict[str, DocumentInfo]:
    """Discover all managed documents in category's DOCUMENT_SUBDIR."""
    if not category.dir or not isinstance(category.dir, str):
        return {}

    # Handle the case where category.dir is missing leading slash
    category_dir_str = category.dir
    if not category_dir_str.startswith("/"):
        category_dir_str = "/" + category_dir_str

    # Validate and normalize path
    try:
        category_path = Path(category_dir_str)
        # Test that the path is valid by attempting to resolve it
        category_path.resolve()
    except (OSError, ValueError):
        return {}

    docs_dir = get_docs_dir(category_path)
    documents: Dict[str, DocumentInfo] = {}

    if not docs_dir.exists():
        return documents

    # Find all document files with corresponding sidecar metadata
    for ext in DOCUMENT_EXTENSIONS:
        for doc_file in docs_dir.rglob(f"*{ext}"):
            if not is_document_file(doc_file):
                continue

            sidecar_path = get_metadata_path(doc_file)
            if sidecar_path.exists():
                try:
                    with open(sidecar_path) as f:
                        metadata = json.load(f)

                    documents[doc_file.stem] = DocumentInfo(
                        path=doc_file.relative_to(category_path), metadata_path=sidecar_path, metadata=metadata
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Corrupted JSON metadata file {sidecar_path}: {e}")
                    continue
                except OSError as e:
                    logger.warning(f"Failed to read metadata file {sidecar_path}: {e}")
                    continue

    return documents
