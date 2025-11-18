"""Integration test for document creation without extension (original bug)."""

import pytest
from src.mcp_server_guide.tools.document_tools import create_mcp_document


@pytest.mark.asyncio
async def test_create_document_without_extension(tmp_path):
    """Test that creating a document without extension works (original bug fix).

    Now with Phase 3: extension is automatically added based on CONTENT detection.
    """
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="gradle-plugin",
        content="# Instructions for Kotlin Gradle Plugin Project",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/markdown",
    )

    assert result["success"] is True
    # Content is detected as text/plain by magic, so gets .txt
    assert "gradle-plugin.txt" in result["message"]

    # Verify document was created with extension
    doc_path = category_dir / "__docs__" / "gradle-plugin.txt"
    assert doc_path.exists()

    # Verify metadata was created with correct name (no "Invalid suffix" error)
    metadata_path = category_dir / "__docs__" / "gradle-plugin.txt_.json"
    assert metadata_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_extension(tmp_path):
    """Test that creating a document with extension still works."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="test.md",
        content="# Test Document",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/markdown",
    )

    assert result["success"] is True

    # .md is not valid for text/plain content, so .txt is appended
    doc_path = category_dir / "__docs__"
    created_files = [f for f in doc_path.glob("test.md*") if not f.name.endswith("_.json")]
    assert len(created_files) > 0


@pytest.mark.asyncio
async def test_create_document_with_multiple_dots(tmp_path):
    """Test that creating a document with multiple dots in name works."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="file.name.txt",
        content="Test content",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/plain",
    )

    assert result["success"] is True

    # Verify document was created
    doc_path = category_dir / "__docs__" / "file.name.txt"
    assert doc_path.exists()

    # Verify metadata was created
    metadata_path = category_dir / "__docs__" / "file.name.txt_.json"
    assert metadata_path.exists()
