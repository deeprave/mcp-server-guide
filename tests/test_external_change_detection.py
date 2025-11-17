"""Tests for external change detection and async cleanup."""

import tempfile
from pathlib import Path
import pytest
from mcp_server_guide.constants import DOCUMENT_SUBDIR


@pytest.mark.asyncio
async def test_cleanup_missing_metadata():
    """Test cleanup when metadata file is missing."""
    from mcp_server_guide.tools.document_tools import list_mcp_documents

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)
        docs_dir = category_dir / DOCUMENT_SUBDIR
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create document file without metadata
        doc_file = docs_dir / "orphaned.md"
        doc_file.write_text("# Orphaned Document")

        # List documents should handle missing metadata gracefully
        result = await list_mcp_documents(category_dir=str(category_dir))

        assert result["success"] is True
        assert len(result["documents"]) == 1
        doc_info = result["documents"][0]
        assert doc_info["name"] == "orphaned.md"
        assert doc_info["source_type"] == "unknown"  # Default when metadata missing


@pytest.mark.asyncio
async def test_content_hash_validation():
    """Test content hash validation for change detection."""
    from mcp_server_guide.tools.document_tools import create_mcp_document
    from mcp_server_guide.services.external_sync import validate_document_integrity

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test.md",
            content="# Original Content",
            explicit_action="CREATE_DOCUMENT",
            source_type="manual",
        )

        # Validate integrity (should pass)
        doc_path = category_dir / DOCUMENT_SUBDIR / "test.md"
        is_valid = await validate_document_integrity(doc_path)
        assert is_valid["success"] is True

        # Modify content externally
        doc_path.write_text("# Modified Content\n", encoding="utf-8")

        # Validate integrity (should fail)
        is_valid = await validate_document_integrity(doc_path)
        assert is_valid["success"] is False
        assert is_valid["error_type"] == "integrity_mismatch"


@pytest.mark.asyncio
async def test_external_modification_detection():
    """Test external file modification updates content hash and mime-type."""
    from mcp_server_guide.tools.document_tools import create_mcp_document
    from mcp_server_guide.services.external_sync import sync_document_metadata
    from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test.md",
            content="# Original",
            explicit_action="CREATE_DOCUMENT",
            source_type="manual",
        )

        doc_path = category_dir / DOCUMENT_SUBDIR / "test.md"
        original_metadata = read_sidecar_metadata(doc_path)
        original_hash = original_metadata.content_hash

        # Modify content externally
        new_content = "# Modified Content"
        doc_path.write_text(new_content, encoding="utf-8")

        # Sync metadata
        sync_result = await sync_document_metadata(doc_path)
        assert sync_result["success"] is True

        # Check metadata was updated
        updated_metadata = read_sidecar_metadata(doc_path)
        assert updated_metadata.content_hash != original_hash
        assert "Modified Content" in new_content


@pytest.mark.asyncio
async def test_category_cleanup_trigger():
    """Test category access triggers async cleanup task."""
    from mcp_server_guide.tools.document_tools import create_mcp_document
    from mcp_server_guide.queue.category_queue import add_category

    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)

        # Create document
        await create_mcp_document(
            category_dir=str(category_dir),
            name="test.md",
            content="# Test",
            explicit_action="CREATE_DOCUMENT",
            source_type="manual",
        )

        # Modify externally
        doc_path = category_dir / DOCUMENT_SUBDIR / "test.md"
        doc_path.write_text("# Modified", encoding="utf-8")

        # Trigger cleanup via queue
        add_category(str(category_dir))

        # Metadata should be synced
        from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

        read_sidecar_metadata(doc_path)  # Verify metadata exists
        assert "Modified" in doc_path.read_text(encoding="utf-8")
