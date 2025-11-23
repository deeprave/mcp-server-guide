"""Tests for external sync service."""

import tempfile
from pathlib import Path

import pytest

from mcp_server_guide.services.external_sync import (
    get_recent_changes,
    sync_document_metadata,
    validate_document_integrity,
)


class TestValidateDocumentIntegrity:
    """Test validate_document_integrity function."""

    @pytest.mark.asyncio
    async def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        nonexistent_path = Path("/tmp/nonexistent_file.txt")
        result = await validate_document_integrity(nonexistent_path)

        assert result["success"] is False
        assert "not_found" in result["error_type"]

    @pytest.mark.asyncio
    async def test_validate_missing_metadata(self):
        """Test validation of file without metadata."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("test content")
            tmp_path = Path(tmp.name)

        try:
            result = await validate_document_integrity(tmp_path)
            assert result["success"] is False
            assert "metadata_missing" in result["error_type"]
        finally:
            tmp_path.unlink(missing_ok=True)


class TestSyncDocumentMetadata:
    """Test sync_document_metadata function."""

    @pytest.mark.asyncio
    async def test_sync_nonexistent_file(self):
        """Test syncing metadata for nonexistent file."""
        nonexistent_path = Path("/tmp/nonexistent_sync_file.txt")
        result = await sync_document_metadata(nonexistent_path)

        assert result["success"] is False
        assert "not_found" in result["error_type"]

    @pytest.mark.asyncio
    async def test_sync_missing_metadata(self):
        """Test syncing file without existing metadata."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("test content for sync")
            tmp_path = Path(tmp.name)

        try:
            result = await sync_document_metadata(tmp_path)
            assert result["success"] is False
            assert "metadata_missing" in result["error_type"]
        finally:
            tmp_path.unlink(missing_ok=True)


class TestGetRecentChanges:
    """Test get_recent_changes function."""

    @pytest.mark.asyncio
    async def test_get_recent_changes_all(self):
        """Test getting all recent changes."""
        result = await get_recent_changes()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_recent_changes_filtered(self):
        """Test getting recent changes filtered by category."""
        result = await get_recent_changes("test_category")
        assert isinstance(result, dict)
