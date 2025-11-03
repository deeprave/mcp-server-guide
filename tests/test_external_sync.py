"""Tests for external sync service."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from mcp_server_guide.services.external_sync import (
    get_changes_cache,
    get_cleanup_tasks,
    validate_document_integrity,
    sync_document_metadata,
    _cleanup_category_documents,
    _cleanup_expired_cache_entries,
    get_recent_changes,
    CACHE_TTL,
)
from mcp_server_guide.models.document_metadata import DocumentMetadata


class TestGetChangesCache:
    """Test get_changes_cache function."""

    def test_get_changes_cache_returns_dict(self):
        """Test that get_changes_cache returns a dictionary."""
        cache = get_changes_cache()
        assert isinstance(cache, dict)

    def test_get_changes_cache_consistent(self):
        """Test that get_changes_cache returns the same cache instance."""
        cache1 = get_changes_cache()
        cache2 = get_changes_cache()
        assert cache1 is cache2


class TestGetCleanupTasks:
    """Test get_cleanup_tasks function."""

    def test_get_cleanup_tasks_returns_set(self):
        """Test that get_cleanup_tasks returns a set."""
        tasks = get_cleanup_tasks()
        assert isinstance(tasks, set)

    def test_get_cleanup_tasks_consistent(self):
        """Test that get_cleanup_tasks returns the same set instance."""
        tasks1 = get_cleanup_tasks()
        tasks2 = get_cleanup_tasks()
        assert tasks1 is tasks2


class TestValidateDocumentIntegrity:
    """Test validate_document_integrity function."""

    @pytest.mark.asyncio
    async def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        nonexistent_path = Path("/nonexistent/file.txt")

        result = await validate_document_integrity(nonexistent_path)

        assert result["success"] is False
        assert result["error_type"] == "not_found"
        assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    async def test_validate_missing_metadata(self, mock_read_metadata):
        """Test validation when metadata is missing."""
        mock_read_metadata.return_value = None

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await validate_document_integrity(Path(f.name))

            assert result["success"] is False
            assert result["error_type"] == "metadata_missing"

        Path(f.name).unlink()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    @patch("mcp_server_guide.services.external_sync.generate_content_hash")
    async def test_validate_matching_hash(self, mock_hash, mock_read_metadata):
        """Test validation when content hash matches."""
        mock_metadata = DocumentMetadata(source_type="manual", content_hash="test_hash", mime_type="text/plain")
        mock_read_metadata.return_value = mock_metadata
        mock_hash.return_value = "test_hash"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await validate_document_integrity(Path(f.name))

            assert result["success"] is True

        Path(f.name).unlink()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    @patch("mcp_server_guide.services.external_sync.generate_content_hash")
    async def test_validate_mismatched_hash(self, mock_hash, mock_read_metadata):
        """Test validation when content hash doesn't match."""
        mock_metadata = DocumentMetadata(source_type="manual", content_hash="old_hash", mime_type="text/plain")
        mock_read_metadata.return_value = mock_metadata
        mock_hash.return_value = "new_hash"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await validate_document_integrity(Path(f.name))

            assert result["success"] is False
            assert result["error_type"] == "integrity_mismatch"

        Path(f.name).unlink()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    async def test_validate_exception_handling(self, mock_read_metadata):
        """Test validation handles exceptions gracefully."""
        mock_read_metadata.side_effect = Exception("Test error")

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await validate_document_integrity(Path(f.name))

            assert result["success"] is False
            assert result["error_type"] == "unexpected"

        Path(f.name).unlink()


class TestSyncDocumentMetadata:
    """Test sync_document_metadata function."""

    @pytest.mark.asyncio
    async def test_sync_nonexistent_file(self):
        """Test syncing non-existent file."""
        nonexistent_path = Path("/nonexistent/file.txt")

        result = await sync_document_metadata(nonexistent_path)

        assert result["success"] is False
        assert result["error_type"] == "not_found"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    async def test_sync_missing_metadata(self, mock_read_metadata):
        """Test syncing when no existing metadata."""
        mock_read_metadata.return_value = None

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await sync_document_metadata(Path(f.name))

            assert result["success"] is False
            assert result["error_type"] == "metadata_missing"

        Path(f.name).unlink()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.read_sidecar_metadata")
    @patch("mcp_server_guide.services.external_sync.create_sidecar_metadata")
    @patch("mcp_server_guide.services.external_sync.generate_content_hash")
    @patch("mcp_server_guide.services.external_sync.detect_mime_type")
    async def test_sync_successful(self, mock_mime, mock_hash, mock_create, mock_read):
        """Test successful metadata sync."""
        mock_existing = DocumentMetadata(source_type="manual", content_hash="old_hash", mime_type="text/plain")
        mock_read.return_value = mock_existing
        mock_hash.return_value = "new_hash"
        mock_mime.return_value = "text/plain"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            result = await sync_document_metadata(Path(f.name))

            assert result["success"] is True
            mock_create.assert_called_once()

        Path(f.name).unlink()


class TestCleanupCategoryDocuments:
    """Test _cleanup_category_documents function."""

    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_directory(self):
        """Test cleanup of non-existent category directory."""
        # Should not raise exception
        await _cleanup_category_documents("/nonexistent/category")

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.validate_document_integrity")
    @patch("mcp_server_guide.services.external_sync.sync_document_metadata")
    async def test_cleanup_processes_documents(self, mock_sync, mock_validate):
        """Test cleanup processes documents in category."""
        mock_validate.return_value = {"success": False}  # Needs sync
        mock_sync.return_value = {"success": True}

        with tempfile.TemporaryDirectory() as temp_dir:
            category_path = Path(temp_dir)
            docs_dir = category_path / "__docs__"
            docs_dir.mkdir()

            # Create test document
            test_doc = docs_dir / "test.txt"
            test_doc.write_text("test content")

            await _cleanup_category_documents(str(category_path))

            mock_validate.assert_called_once()
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.validate_document_integrity")
    async def test_cleanup_skips_valid_documents(self, mock_validate):
        """Test cleanup skips documents that don't need sync."""
        mock_validate.return_value = {"success": True}  # Valid, no sync needed

        with tempfile.TemporaryDirectory() as temp_dir:
            category_path = Path(temp_dir)
            docs_dir = category_path / "__docs__"
            docs_dir.mkdir()

            # Create test document
            test_doc = docs_dir / "test.txt"
            test_doc.write_text("test content")

            with patch("mcp_server_guide.services.external_sync.sync_document_metadata") as mock_sync:
                await _cleanup_category_documents(str(category_path))

                mock_validate.assert_called_once()
                mock_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_cleanup_handles_exceptions(self):
        """Test cleanup handles exceptions gracefully."""
        with patch("mcp_server_guide.services.external_sync.Path") as mock_path:
            mock_path.side_effect = Exception("Test error")

            # Should not raise exception
            await _cleanup_category_documents("test_category")


class TestCleanupExpiredCacheEntries:
    """Test _cleanup_expired_cache_entries function."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.get_changes_cache")
    @patch("mcp_server_guide.services.external_sync._changes_cache")
    @patch("mcp_server_guide.services.external_sync.time.time")
    async def test_cleanup_removes_expired_entries(self, mock_time, mock_cache_var, mock_get_cache):
        """Test cleanup removes expired cache entries."""
        current_time = 1000.0
        mock_time.return_value = current_time

        # Mock cache with expired and valid entries
        mock_cache = {
            "expired_key": {"timestamp": current_time - CACHE_TTL - 1, "action": "modified"},
            "valid_key": {"timestamp": current_time - 100, "action": "modified"},
        }
        mock_get_cache.return_value = mock_cache

        await _cleanup_expired_cache_entries()

        # Should remove expired entry
        assert "expired_key" not in mock_cache
        assert "valid_key" in mock_cache

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync.get_changes_cache")
    @patch("mcp_server_guide.services.external_sync.time.time")
    async def test_cleanup_empty_cache(self, mock_time, mock_get_cache):
        """Test cleanup with empty cache."""
        mock_time.return_value = 1000.0
        mock_get_cache.return_value = {}

        # Should not raise exception
        await _cleanup_expired_cache_entries()


class TestGetRecentChanges:
    """Test get_recent_changes function."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync._cleanup_expired_cache_entries")
    @patch("mcp_server_guide.services.external_sync.get_changes_cache")
    async def test_get_recent_changes_all(self, mock_get_cache, mock_cleanup):
        """Test getting all recent changes."""
        mock_cache = {
            "file1": {"category": "cat1", "action": "modified"},
            "file2": {"category": "cat2", "action": "modified"},
        }
        mock_get_cache.return_value = mock_cache

        result = await get_recent_changes()

        assert result == mock_cache
        mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    @patch("mcp_server_guide.services.external_sync._cleanup_expired_cache_entries")
    @patch("mcp_server_guide.services.external_sync.get_changes_cache")
    async def test_get_recent_changes_filtered(self, mock_get_cache, mock_cleanup):
        """Test getting recent changes filtered by category."""
        mock_cache = {
            "file1": {"category": "cat1", "action": "modified"},
            "file2": {"category": "cat2", "action": "modified"},
            "file3": {"category": "cat1", "action": "modified"},
        }
        mock_get_cache.return_value = mock_cache

        result = await get_recent_changes("cat1")

        assert len(result) == 2
        assert "file1" in result
        assert "file3" in result
        assert "file2" not in result
