"""Tests for document management helper functions."""

from pathlib import Path

import pytest


def test_get_metadata_path():
    """Test get_metadata_path converts document path to metadata path."""
    from mcp_server_guide.utils.document_helpers import get_metadata_path

    # Test different document types
    assert get_metadata_path(Path("test.md")) == Path("test.md_.json")
    assert get_metadata_path(Path("config.yaml")) == Path("config.yaml_.json")
    assert get_metadata_path(Path("data.json")) == Path("data.json_.json")
    assert get_metadata_path(Path("manual.pdf")) == Path("manual.pdf_.json")


def test_get_document_path():
    """Test get_document_path converts metadata path to document path."""
    from mcp_server_guide.utils.document_helpers import get_document_path

    # Test different document types
    assert get_document_path(Path("test.md_.json")) == Path("test.md")
    assert get_document_path(Path("config.yaml_.json")) == Path("config.yaml")
    assert get_document_path(Path("data.json_.json")) == Path("data.json")
    assert get_document_path(Path("manual.pdf_.json")) == Path("manual.pdf")


def test_get_document_path_invalid():
    """Test get_document_path raises error for invalid metadata path."""
    from mcp_server_guide.utils.document_helpers import get_document_path

    with pytest.raises(ValueError, match="Not a metadata file"):
        get_document_path(Path("invalid.json"))


def test_get_document_path_path_traversal():
    """Test get_document_path raises error for path traversal in metadata path."""
    from mcp_server_guide.utils.document_helpers import get_document_path

    # Attempt to traverse directories
    with pytest.raises(ValueError, match="Not a metadata file"):
        get_document_path(Path("../secret.txt_.json"))
    with pytest.raises(ValueError, match="Not a metadata file"):
        get_document_path(Path("/etc/passwd_.json"))


def test_get_docs_dir():
    """Test get_docs_dir returns __docs__ subdirectory path."""
    from mcp_server_guide.utils.document_helpers import get_docs_dir

    category_dir = Path("/path/to/category")
    docs_dir = get_docs_dir(category_dir)

    assert docs_dir == Path("/path/to/category/__docs__")


def test_is_document_file():
    """Test is_document_file supports multiple document types and excludes metadata files."""
    from mcp_server_guide.utils.document_helpers import is_document_file

    # Supported document types
    assert is_document_file(Path("document.md")) is True
    assert is_document_file(Path("config.yaml")) is True
    assert is_document_file(Path("config.yml")) is True
    assert is_document_file(Path("data.json")) is True
    assert is_document_file(Path("manual.pdf")) is True
    assert is_document_file(Path("readme.txt")) is True
    assert is_document_file(Path("guide.rst")) is True
    assert is_document_file(Path("spec.adoc")) is True

    # Metadata files should be excluded
    assert is_document_file(Path("document.md_.json")) is False
    assert is_document_file(Path("config.yaml_.json")) is False

    # Unsupported types should be excluded
    assert is_document_file(Path("script.py")) is False
    assert is_document_file(Path("image.png")) is False

    # Hidden files should be excluded
    assert is_document_file(Path(".hidden.md")) is False
