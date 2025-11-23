"""Helper functions for document management."""

from pathlib import Path

from ..constants import DOCUMENT_SUBDIR, METADATA_SUFFIX

# Supported document file extensions
DOCUMENT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".pdf", ".txt", ".rst", ".adoc"}


def get_metadata_path(document_path: Path) -> Path:
    """Get corresponding metadata file path for a document.

    Metadata files use the pattern: {document_name}{METADATA_SUFFIX}
    Examples:
        - file.md -> file.md_.json
        - file -> file_.json
        - file.name.txt -> file.name.txt_.json

    Note: We don't use Path.with_suffix() because it validates that suffixes
    must start with a dot, which fails for files without extensions.
    """
    return document_path.parent / f"{document_path.name}{METADATA_SUFFIX}"


def get_document_path(metadata_path: Path) -> Path:
    """Get corresponding document file path from metadata file."""
    if not metadata_path.name.endswith(METADATA_SUFFIX):
        raise ValueError(f"Not a metadata file: {metadata_path}")

    # Check for path traversal attempts
    if ".." in str(metadata_path) or metadata_path.is_absolute():
        raise ValueError(f"Not a metadata file: {metadata_path}")

    # Remove the METADATA_SUFFIX to get the original filename
    base_name = metadata_path.name[: -len(METADATA_SUFFIX)]
    return metadata_path.parent / base_name


def get_docs_dir(category_dir: Path) -> Path:
    """Get the __docs__ subdirectory path for a category."""
    # Validate input path
    if not category_dir.is_absolute():
        category_dir = category_dir.resolve()

    docs_path = category_dir / DOCUMENT_SUBDIR

    # Ensure the path is within the category directory (prevent path traversal)
    try:
        docs_path.resolve().relative_to(category_dir.resolve())
    except ValueError as e:
        raise ValueError(f"Invalid docs path: {docs_path} is outside category directory {category_dir}") from e

    return docs_path


def is_document_file(path: Path) -> bool:
    """Check if file is a document (supported extension, not metadata, not hidden)."""
    return (
        path.suffix.lower() in DOCUMENT_EXTENSIONS
        and not path.name.endswith(METADATA_SUFFIX)
        and not path.name.startswith(".")
    )
