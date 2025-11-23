"""Tests for category document discovery."""

import json
from pathlib import Path


def test_get_category_documents_finds_multiple_document_types(temp_project_dir):
    """Test get_category_documents finds managed documents of various types in DOCUMENT_SUBDIR."""
    from mcp_server_guide.models.category import Category
    from mcp_server_guide.services.document_discovery import get_category_documents

    category_dir = temp_project_dir
    docs_dir = category_dir / "__docs__"
    docs_dir.mkdir()

    # Create documents of different types with sidecars
    documents = [
        ("readme.md", "text/markdown", "# Readme"),
        ("config.yaml", "application/yaml", "key: value"),
        ("data.json", "application/json", '{"test": true}'),
        ("manual.pdf", "application/pdf", "PDF content"),
        ("notes.txt", "text/plain", "Some notes"),
    ]

    for filename, mime_type, content in documents:
        doc_path = docs_dir / filename
        sidecar_path = docs_dir / f"{filename}_.json"

        doc_path.write_text(content)
        sidecar_path.write_text(
            json.dumps({"source_type": "manual", "content_hash": f"sha256:{filename}", "mime_type": mime_type})
        )

    category = Category(name="test", dir=str(category_dir), patterns=["*"])

    documents_found = get_category_documents(category)

    # Should find all document types
    assert len(documents_found) == 5
    assert "readme" in documents_found
    assert "config" in documents_found
    assert "data" in documents_found
    assert "manual" in documents_found
    assert "notes" in documents_found

    # Check metadata is correct
    assert documents_found["readme"].metadata["mime_type"] == "text/markdown"
    assert documents_found["config"].metadata["mime_type"] == "application/yaml"
    assert documents_found["data"].metadata["mime_type"] == "application/json"
    assert documents_found["manual"].metadata["mime_type"] == "application/pdf"
    assert documents_found["notes"].metadata["mime_type"] == "text/plain"


def test_get_category_documents_finds_managed_documents(temp_project_dir):
    """Test get_category_documents finds managed documents in DOCUMENT_SUBDIR."""
    from mcp_server_guide.models.category import Category
    from mcp_server_guide.services.document_discovery import get_category_documents

    category_dir = temp_project_dir
    docs_dir = category_dir / "__docs__"
    docs_dir.mkdir()

    # Create a managed document with sidecar
    doc_path = docs_dir / "test.md"
    sidecar_path = docs_dir / "test.md_.json"

    doc_path.write_text("# Test Document")
    sidecar_path.write_text(
        json.dumps({"source_type": "manual", "content_hash": "sha256:abc123", "mime_type": "text/markdown"})
    )

    category = Category(name="test", dir=str(category_dir), patterns=["*.md"])

    documents = get_category_documents(category)

    assert len(documents) == 1
    assert "test" in documents

    doc_info = documents["test"]
    assert doc_info.path == Path("__docs__/test.md")  # Relative to category_dir
    assert doc_info.metadata_path == sidecar_path
    assert doc_info.metadata["source_type"] == "manual"


def test_get_category_documents_empty_directory(temp_project_dir):
    """Test get_category_documents with empty __docs__ directory."""
    from mcp_server_guide.models.category import Category
    from mcp_server_guide.services.document_discovery import get_category_documents

    category_dir = temp_project_dir
    docs_dir = category_dir / "__docs__"
    docs_dir.mkdir()

    category = Category(name="test", dir=str(category_dir), patterns=["*.md"])

    documents = get_category_documents(category)

    assert len(documents) == 0


def test_get_category_documents_no_docs_directory(temp_project_dir):
    """Test get_category_documents when __docs__ directory doesn't exist."""
    from mcp_server_guide.models.category import Category
    from mcp_server_guide.services.document_discovery import get_category_documents

    category_dir = temp_project_dir

    category = Category(name="test", dir=str(category_dir), patterns=["*.md"])

    documents = get_category_documents(category)

    assert len(documents) == 0
