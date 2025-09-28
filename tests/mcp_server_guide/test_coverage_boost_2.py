"""Additional tests to boost coverage for low-hanging fruit."""

import tempfile
from pathlib import Path
from unittest.mock import patch
from src.mcp_server_guide.tools.session_management import save_session
from src.mcp_server_guide.tools.category_tools import _safe_glob_search


def test_save_session_failure():
    """Test save session failure handling."""
    with patch("src.mcp_server_guide.tools.session_management.SessionManager") as mock_session:
        mock_session.return_value.save_to_file.side_effect = Exception("Save error")

        result = save_session("test.json")

        assert result["success"] is False
        assert "Save error" in result["error"]


def test_safe_glob_non_file_skip():
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


def test_safe_glob_symlink_resolution_error():
    """Test safe glob handles symlink resolution errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create a regular file
        (base_path / "regular.md").write_text("content")

        # Mock Path.resolve to raise an error for symlink handling
        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_resolve.side_effect = [
                base_path.resolve(),  # First call for search_dir
                OSError("Symlink error"),  # Second call for match_path
            ]

            with patch("src.mcp_server_guide.tools.category_tools.logger") as mock_logger:
                results = _safe_glob_search(base_path, ["*.md"])

                # Should handle error gracefully and log warning
                assert len(results) == 0  # File skipped due to resolution error
                mock_logger.warning.assert_called()
