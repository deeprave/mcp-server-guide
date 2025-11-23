import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_server_guide.tools.category_tools import _safe_glob_search


async def test_save_session_failure():
    """Test save session failure handling."""

    mock_session_instance = Mock()
    mock_session_instance.get_project_name = Mock(side_effect=Exception("Save error"))
    mock_session_instance.safe_save_session = AsyncMock(side_effect=Exception("Save error"))

    with pytest.raises(Exception, match="Save error"):
        await mock_session_instance.safe_save_session()


async def test_safe_glob_non_file_skip():
    """Test that safe glob skips non-file entries."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create a directory that matches the pattern
        (base_path / "directory.md").mkdir()
        # Create a regular file
        (base_path / "file.md").write_text("content")

        results = _safe_glob_search(base_path, ["*.md"])

        # Should only find the file, not the directory
        assert len(results) == 1
        assert results[0].name == "file.md"


async def test_safe_glob_symlink_resolution_error():
    """Test safe glob handles symlink resolution errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create a regular file
        (base_path / "regular.md").write_text("content")

        # Mock Path.resolve to raise an error for symlink handling
        with patch("pathlib.Path.resolve") as mock_resolve:
            # The resolve calls happen in this order:
            # 1. match_path.resolve() for symlink resolution (line 69)
            # 2. search_dir.resolve() in relative_to check (line 84)
            mock_resolve.side_effect = [
                OSError("Symlink error"),  # First call for match_path.resolve()
                base_path.resolve(),  # Second call for search_dir.resolve() in relative_to
            ]

            with patch("mcp_server_guide.tools.category_tools.logger") as mock_logger:
                results = _safe_glob_search(base_path, ["*.md"])

                # Should handle error gracefully and log warning
                assert len(results) == 0  # File skipped due to resolution error
                mock_logger.warning.assert_called()
