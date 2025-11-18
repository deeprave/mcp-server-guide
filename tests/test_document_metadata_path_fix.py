"""Test for document metadata path generation fix."""

from pathlib import Path
from src.mcp_server_guide.utils.document_helpers import get_metadata_path


def test_metadata_path_for_file_without_extension():
    """Test that metadata path is generated correctly for files without extension."""
    doc_path = Path("gradle-plugin")
    metadata_path = get_metadata_path(doc_path)
    assert metadata_path == Path("gradle-plugin_.json")


def test_metadata_path_for_file_with_extension():
    """Test that metadata path is generated correctly for files with extension."""
    doc_path = Path("file.md")
    metadata_path = get_metadata_path(doc_path)
    assert metadata_path == Path("file.md_.json")


def test_metadata_path_for_file_with_multiple_dots():
    """Test that metadata path is generated correctly for files with multiple dots."""
    doc_path = Path("file.name.txt")
    metadata_path = get_metadata_path(doc_path)
    assert metadata_path == Path("file.name.txt_.json")


def test_metadata_path_preserves_directory():
    """Test that metadata path preserves the directory structure."""
    doc_path = Path("context/__docs__/gradle-plugin")
    metadata_path = get_metadata_path(doc_path)
    assert metadata_path == Path("context/__docs__/gradle-plugin_.json")
