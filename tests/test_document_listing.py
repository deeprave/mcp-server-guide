"""Tests for document listing functionality."""

import tempfile
from pathlib import Path
import pytest


@pytest.mark.asyncio
async def test_list_mcp_documents_basic():
    """Test basic document listing with filesystem timestamps."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, list_mcp_documents

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create test documents
        await create_mcp_document(
            category_dir=str(category_dir), name="doc1.md", content="# Document 1", source_type="manual"
        )

        await create_mcp_document(
            category_dir=str(category_dir), name="doc2.yaml", content="key: value", source_type="imported"
        )

        # List documents
        result = await list_mcp_documents(category_dir=str(category_dir))

        assert result["success"] is True
        assert len(result["documents"]) == 2

        # Check document structure
        doc1 = next(d for d in result["documents"] if d["name"] == "doc1.md")
        assert doc1["path"].endswith("__docs__/doc1.md")
        assert doc1["source_type"] == "manual"
        assert doc1["mime_type"] == "text/markdown"
        assert "created_at" in doc1
        assert "updated_at" in doc1
        assert "size" in doc1


@pytest.mark.asyncio
async def test_list_mcp_documents_empty():
    """Test listing documents in empty category."""
    from mcp_server_guide.tools.document_tools import list_mcp_documents

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        result = await list_mcp_documents(category_dir=str(category_dir))

        assert result["success"] is True
        assert result["documents"] == []


@pytest.mark.asyncio
async def test_list_mcp_documents_with_filtering():
    """Test document listing with filtering capabilities."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, list_mcp_documents

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create documents with different types
        await create_mcp_document(
            category_dir=str(category_dir), name="manual.md", content="# Manual", source_type="manual"
        )

        await create_mcp_document(
            category_dir=str(category_dir),
            name="imported.json",
            content='{"imported": true}',
            source_type="imported",
            mime_type="application/json",
        )

        # Filter by source_type
        result = await list_mcp_documents(category_dir=str(category_dir), source_type="manual")

        assert result["success"] is True
        assert len(result["documents"]) == 1
        assert result["documents"][0]["name"] == "manual.md"

        # Filter by mime_type
        result = await list_mcp_documents(category_dir=str(category_dir), mime_type="application/json")

        assert result["success"] is True
        assert len(result["documents"]) == 1
        assert result["documents"][0]["name"] == "imported.json"


@pytest.mark.asyncio
async def test_list_mcp_documents_mixed_with_pattern_files():
    """Test document listing handles mixed managed/pattern documents."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, list_mcp_documents

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create pattern files (outside __docs__)
        pattern_file = category_dir / "pattern.md"
        pattern_file.write_text("# Pattern File")

        # Create managed documents (inside __docs__)
        await create_mcp_document(
            category_dir=str(category_dir), name="managed.md", content="# Managed Document", source_type="manual"
        )

        # List documents should only return managed documents
        result = await list_mcp_documents(category_dir=str(category_dir))

        assert result["success"] is True
        assert len(result["documents"]) == 1
        assert result["documents"][0]["name"] == "managed.md"
        assert result["documents"][0]["source_type"] == "manual"


@pytest.mark.asyncio
async def test_list_mcp_documents_corrupted_metadata():
    """Test document listing with corrupted metadata files."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, list_mcp_documents
    from mcp_server_guide.constants import DOCUMENT_SUBDIR, METADATA_SUFFIX

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)
        docs_dir = category_dir / DOCUMENT_SUBDIR
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create a document with valid metadata
        await create_mcp_document(
            category_dir=str(category_dir), name="valid.md", content="# Valid Document", source_type="manual"
        )

        # Create a document file with corrupted metadata
        corrupted_doc = docs_dir / "corrupted.md"
        corrupted_doc.write_text("# Corrupted Document")

        corrupted_metadata = docs_dir / f"corrupted.md{METADATA_SUFFIX}"
        corrupted_metadata.write_text("invalid json content")

        # List documents should handle corrupted metadata gracefully
        result = await list_mcp_documents(category_dir=str(category_dir))

        assert result["success"] is True
        assert len(result["documents"]) == 2

        # Find the corrupted document
        corrupted_doc_info = next(doc for doc in result["documents"] if doc["name"] == "corrupted.md")
        assert corrupted_doc_info["source_type"] == "unknown"  # Should default when metadata is corrupted
