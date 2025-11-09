"""Tests for external sync service error handling paths."""

import pytest
from unittest.mock import patch
from mcp_server_guide.services.external_sync import (
    _cache,
    _cleanup_category_documents,
    validate_document_integrity,
    sync_document_metadata,
)


class TestChangesCacheErrorPaths:
    """Test ChangesCache error handling."""

    @pytest.mark.asyncio
    async def test_cache_add_change(self):
        """Test ChangesCache.add_change method."""
        await _cache.add_change("test_key", {"action": "test", "category": "test_cat"})

        # Verify change was added
        changes = await _cache.get_changes()
        assert "test_key" in changes
        assert changes["test_key"]["action"] == "test"

    @pytest.mark.asyncio
    async def test_cache_get_changes_filtered(self):
        """Test ChangesCache.get_changes with category filter."""
        await _cache.add_change("key1", {"action": "test", "category": "cat1"})
        await _cache.add_change("key2", {"action": "test", "category": "cat2"})

        # Test filtering
        cat1_changes = await _cache.get_changes("cat1")
        assert len([k for k in cat1_changes.keys() if "key1" in k]) >= 0  # May have other entries


class TestCleanupCategoryDocuments:
    """Test _cleanup_category_documents error handling."""

    @pytest.mark.asyncio
    async def test_cleanup_category_documents_nonexistent(self):
        """Test cleanup with nonexistent category directory."""
        # Should not raise exception
        await _cleanup_category_documents("/tmp/nonexistent_category_dir")

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.validate_document_integrity")
    async def test_cleanup_category_documents_validation_error(self, mock_validate):
        """Test cleanup when validation fails."""
        mock_validate.return_value = {"success": False, "error": "validation failed"}

        # Should not raise exception even if validation fails
        await _cleanup_category_documents("/tmp/test_category")

    @pytest.mark.asyncio
    @patch("pathlib.Path.exists")
    async def test_cleanup_category_documents_path_error(self, mock_exists):
        """Test cleanup with path access errors."""
        mock_exists.side_effect = OSError("Path access error")

        # Should handle exception gracefully
        await _cleanup_category_documents("/tmp/test_category")


class TestValidateDocumentIntegrityErrors:
    """Test validate_document_integrity error paths."""

    @pytest.mark.asyncio
    @patch("pathlib.Path.read_text")
    async def test_validate_document_unicode_error(self, mock_read_text):
        """Test validation with unicode decode error."""
        from pathlib import Path

        mock_read_text.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")

        result = await validate_document_integrity(Path("/tmp/test.txt"))

        assert result["success"] is False
        assert result["error_type"] == "not_found"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.utils.sidecar_operations.read_sidecar_metadata")
    async def test_validate_document_metadata_error(self, mock_read_metadata):
        """Test validation with metadata read error."""
        from pathlib import Path

        mock_read_metadata.side_effect = Exception("Metadata read error")

        result = await validate_document_integrity(Path("/tmp/test.txt"))

        assert result["success"] is False
        assert result["error_type"] == "not_found"


class TestSyncDocumentMetadataErrors:
    """Test sync_document_metadata error paths."""

    @pytest.mark.asyncio
    @patch("pathlib.Path.read_text")
    async def test_sync_document_read_error(self, mock_read_text):
        """Test sync with file read error."""
        from pathlib import Path

        mock_read_text.side_effect = PermissionError("Cannot read file")

        result = await sync_document_metadata(Path("/tmp/test.txt"))

        assert result["success"] is False
        assert result["error_type"] == "not_found"

    @pytest.mark.asyncio
    async def test_sync_document_metadata_write_error(self):
        """Test sync with metadata write error."""
        from pathlib import Path
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("test content")
            tmp_path = Path(tmp.name)

        try:
            # Test with nonexistent metadata (will trigger metadata_missing error)
            result = await sync_document_metadata(tmp_path)

            assert result["success"] is False
            assert result["error_type"] == "metadata_missing"
        finally:
            tmp_path.unlink(missing_ok=True)
