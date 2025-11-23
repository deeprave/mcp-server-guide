"""Document discovery utilities."""

from pathlib import Path
from typing import List

from ..constants import DOCUMENT_SUBDIR
from ..models.document_info import DocumentInfo
from ..utils.document_helpers import get_metadata_path, is_document_file
from ..utils.sidecar_operations import read_sidecar_metadata


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
                    metadata_obj = read_sidecar_metadata(file_path)
                    if metadata_obj:
                        metadata = metadata_obj.model_dump()
                except Exception:
                    # If metadata is corrupted, continue with empty metadata
                    pass

            documents.append(
                DocumentInfo(
                    path=file_path,
                    metadata_path=metadata_path,
                    metadata=metadata,
                )
            )

    return documents
