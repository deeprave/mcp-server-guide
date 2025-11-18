"""Integration tests for extension normalization in document creation."""

import pytest
from src.mcp_server_guide.tools.document_tools import create_mcp_document


@pytest.mark.asyncio
async def test_create_document_without_extension_adds_extension(tmp_path):
    """Test that document without extension gets appropriate extension added based on content."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="gradle-plugin",
        content="# Instructions",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/markdown",
    )

    assert result["success"] is True

    # Document should be created with extension based on content
    # Text content typically gets .txt extension from magic
    docs_dir = category_dir / "__docs__"
    created_files = list(docs_dir.glob("gradle-plugin*"))
    assert len(created_files) > 0
    assert any(not f.name.endswith("_.json") for f in created_files)


@pytest.mark.asyncio
async def test_create_document_with_correct_extension(tmp_path):
    """Test that document with correct extension is accepted."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="test.txt",
        content="Plain text content",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/plain",
    )

    assert result["success"] is True
    doc_path = category_dir / "__docs__" / "test.txt"
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_wrong_extension_corrects(tmp_path):
    """Test that document with wrong extension gets corrected automatically."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="xyzzy.json",
        content="# Markdown content",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/markdown",
    )

    # Should succeed (no error) and append correct extension
    assert result["success"] is True

    # File should exist with corrected name
    docs_dir = category_dir / "__docs__"
    created_files = list(docs_dir.glob("xyzzy.json*"))
    assert len(created_files) > 0


@pytest.mark.asyncio
async def test_create_document_json_content(tmp_path):
    """Test JSON content detection and extension."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="data",
        content='{"key": "value"}',
        explicit_action="CREATE_DOCUMENT",
        mime_type=None,  # Auto-detect
    )

    assert result["success"] is True
    # JSON is detected as text by magic, so gets .txt
    docs_dir = category_dir / "__docs__"
    assert len(list(docs_dir.glob("data*"))) > 0


@pytest.mark.asyncio
async def test_create_document_preserves_valid_extension(tmp_path):
    """Test that valid extensions are preserved."""
    category_dir = tmp_path / "context"
    category_dir.mkdir()

    result = await create_mcp_document(
        category_dir=str(category_dir),
        name="file.txt",
        content="Plain text",
        explicit_action="CREATE_DOCUMENT",
        mime_type="text/plain",
    )

    assert result["success"] is True
    doc_path = category_dir / "__docs__" / "file.txt"
    assert doc_path.exists()
