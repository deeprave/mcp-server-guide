"""Tests for document CRUD operations."""

import pytest
import tempfile
import json
import hashlib
from pathlib import Path
from mcp_server_guide.constants import DOCUMENT_SUBDIR, METADATA_SUFFIX


@pytest.mark.asyncio
async def test_create_mcp_document():
    """Test creating a new managed document with metadata."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)
        docs_dir = category_dir / DOCUMENT_SUBDIR

        # Create document
        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md",
            content="# Test Document\n\nThis is a test.",
            source_type="manual"
        )

        # Should return success with URI
        assert result["success"] is True
        assert "guide://" in result["uri"]
        assert "test-doc.md" in result["uri"]

        # Document file should exist
        doc_path = docs_dir / "test-doc.md"
        assert doc_path.exists()
        assert doc_path.read_text() == "# Test Document\n\nThis is a test."

        # Metadata file should exist with correct content
        metadata_path = docs_dir / f"test-doc.md{METADATA_SUFFIX}"
        assert metadata_path.exists()

        metadata = json.loads(metadata_path.read_text())
        assert metadata["source_type"] == "manual"
        assert metadata["mime_type"] == "text/markdown"
        assert "content_hash" in metadata

        # Content hash should be correct
        expected_hash = hashlib.sha256("# Test Document\n\nThis is a test.".encode()).hexdigest()
        assert metadata["content_hash"] == f"sha256:{expected_hash}"


@pytest.mark.asyncio
async def test_create_mcp_document_auto_mime_type():
    """Test document creation with automatic mime-type detection."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create YAML document
        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="config.yaml",
            content="key: value\n",
            source_type="manual"
        )

        assert result["success"] is True

        # Check metadata has correct mime-type
        metadata_path = Path(temp_dir) / DOCUMENT_SUBDIR / f"config.yaml{METADATA_SUFFIX}"
        metadata = json.loads(metadata_path.read_text())
        assert metadata["mime_type"] == "text/yaml"


@pytest.mark.asyncio
async def test_create_mcp_document_explicit_mime_type():
    """Test document creation with explicit mime-type override."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document with explicit mime-type
        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="data.txt",
            content='{"key": "value"}',
            source_type="manual",
            mime_type="application/json"
        )

        assert result["success"] is True

        # Check metadata uses explicit mime-type
        metadata_path = Path(temp_dir) / DOCUMENT_SUBDIR / f"data.txt{METADATA_SUFFIX}"
        metadata = json.loads(metadata_path.read_text())
        assert metadata["mime_type"] == "application/json"
@pytest.mark.asyncio
async def test_update_mcp_document():
    """Test updating an existing managed document."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, update_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create initial document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md",
            content="# Original Content",
            source_type="manual"
        )

        # Update the document
        result = await update_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md",
            content="# Updated Content\n\nThis is updated."
        )

        # Should return success
        assert result["success"] is True
        assert "guide://" in result["uri"]

        # Document content should be updated
        doc_path = category_dir / DOCUMENT_SUBDIR / "test-doc.md"
        assert doc_path.read_text() == "# Updated Content\n\nThis is updated."

        # Metadata should be updated with new content hash
        metadata_path = category_dir / DOCUMENT_SUBDIR / f"test-doc.md{METADATA_SUFFIX}"
        metadata = json.loads(metadata_path.read_text())

        expected_hash = hashlib.sha256("# Updated Content\n\nThis is updated.".encode()).hexdigest()
        assert metadata["content_hash"] == f"sha256:{expected_hash}"


@pytest.mark.asyncio
async def test_update_mcp_document_nonexistent():
    """Test updating a document that doesn't exist."""
    from mcp_server_guide.tools.document_tools import update_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Try to update non-existent document
        result = await update_mcp_document(
            category_dir=str(category_dir),
            name="nonexistent.md",
            content="# New Content"
        )

        # Should return error
        assert result["success"] is False
        assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_delete_mcp_document():
    """Test deleting an existing managed document."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, delete_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md",
            content="# Test Document",
            source_type="manual"
        )

        # Verify files exist
        doc_path = category_dir / DOCUMENT_SUBDIR / "test-doc.md"
        metadata_path = category_dir / DOCUMENT_SUBDIR / f"test-doc.md{METADATA_SUFFIX}"
        assert doc_path.exists()
        assert metadata_path.exists()

        # Delete the document
        result = await delete_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md"
        )

        # Should return success
        assert result["success"] is True
        assert "deleted successfully" in result["message"]

        # Files should be removed
        assert not doc_path.exists()
        assert not metadata_path.exists()


@pytest.mark.asyncio
async def test_delete_mcp_document_nonexistent():
    """Test deleting a document that doesn't exist."""
    from mcp_server_guide.tools.document_tools import delete_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Try to delete non-existent document
        result = await delete_mcp_document(
            category_dir=str(category_dir),
            name="nonexistent.md"
        )

        # Should return error
        assert result["success"] is False
        assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_delete_mcp_document_missing_metadata():
    """Test deleting a document with missing metadata file."""
    from mcp_server_guide.tools.document_tools import create_mcp_document, delete_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md",
            content="# Test Document",
            source_type="manual"
        )

        # Remove metadata file manually
        metadata_path = category_dir / DOCUMENT_SUBDIR / f"test-doc.md{METADATA_SUFFIX}"
        metadata_path.unlink()

        # Delete should still work
        result = await delete_mcp_document(
            category_dir=str(category_dir),
            name="test-doc.md"
        )

        # Should return success
        assert result["success"] is True

        # Document should be removed
        doc_path = category_dir / DOCUMENT_SUBDIR / "test-doc.md"
        assert not doc_path.exists()


@pytest.mark.asyncio
async def test_create_mcp_document_with_dots_in_name():
    """Test that document names with dots are allowed after code review fix."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Test filename with dots (should be allowed)
        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="my.config.file.yaml",
            content="key: value",
            source_type="manual"
        )

        assert result["success"] is True
        assert "my.config.file.yaml" in result["message"]

        # Verify file was created
        doc_path = category_dir / "__docs__" / "my.config.file.yaml"
        assert doc_path.exists()
        assert doc_path.read_text(encoding='utf-8') == "key: value"


@pytest.mark.asyncio
async def test_create_mcp_document_invalid_name():
    """Test document creation with invalid names."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Test path traversal
        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="../evil.md",
            content="# Evil Content",
            source_type="manual"
        )

        assert result["success"] is False
        assert result["error_type"] == "validation"
        assert "Invalid document name" in result["error"]


@pytest.mark.asyncio
async def test_create_mcp_document_large_content():
    """Test document creation with content too large."""
    from mcp_server_guide.tools.document_tools import create_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create content larger than 10MB
        large_content = "x" * (11 * 1024 * 1024)

        result = await create_mcp_document(
            category_dir=str(category_dir),
            name="large.md",
            content=large_content,
            source_type="manual"
        )

        assert result["success"] is False
        assert result["error_type"] == "validation"
        assert "too large" in result["error"]


@pytest.mark.asyncio
async def test_update_mcp_document_invalid_name():
    """Test document update with invalid name."""
    from mcp_server_guide.tools.document_tools import update_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        result = await update_mcp_document(
            category_dir=str(category_dir),
            name="../evil.md",
            content="# Updated Content"
        )

        assert result["success"] is False
        assert result["error_type"] == "validation"


@pytest.mark.asyncio
async def test_delete_mcp_document_invalid_name():
    """Test document deletion with invalid name."""
    from mcp_server_guide.tools.document_tools import delete_mcp_document

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        result = await delete_mcp_document(
            category_dir=str(category_dir),
            name="../evil.md"
        )

        assert result["success"] is False
        assert result["error_type"] == "validation"
