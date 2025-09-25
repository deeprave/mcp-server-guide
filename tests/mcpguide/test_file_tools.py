"""Tests for file tools functionality."""

from unittest.mock import Mock, patch
from mcpguide.tools.file_tools import list_files, file_exists, get_file_content


def test_list_files_error_handling():
    """Test list_files with various error conditions."""
    # Test with non-existent directory
    with patch("pathlib.Path.exists", return_value=False):
        result = list_files("guide", "test_project")
        assert result == []

    # Test with path that's not a directory
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_dir", return_value=False):
            result = list_files("guide", "test_project")
            assert result == []

    # Test with exception during iteration
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_dir", return_value=True):
            with patch("pathlib.Path.iterdir", side_effect=Exception("Permission denied")):
                result = list_files("guide", "test_project")
                assert result == []


def test_file_exists_error_handling():
    """Test file_exists with error conditions."""
    # Test with exception
    with patch("pathlib.Path.exists", side_effect=Exception("Path error")):
        result = file_exists("test.txt")
        assert result is False

    # Test normal operation
    with patch("pathlib.Path.exists", return_value=True):
        result = file_exists("test.txt")
        assert result is True

    with patch("pathlib.Path.exists", return_value=False):
        result = file_exists("nonexistent.txt")
        assert result is False


def test_get_file_content_error_handling():
    """Test get_file_content with various error conditions."""
    # Test with non-existent file
    with patch("pathlib.Path.exists", return_value=False):
        result = get_file_content("nonexistent.txt")
        assert "File not found" in result

    # Test with path that exists but is not a file
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=False):
            result = get_file_content("directory")
            assert "File not found" in result

    # Test with read error
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("pathlib.Path.read_text", side_effect=Exception("Permission denied")):
                result = get_file_content("error.txt")
                assert "Error reading file" in result

    # Test successful read
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("pathlib.Path.read_text", return_value="file content"):
                result = get_file_content("test.txt")
                assert result == "file content"


def test_list_files_successful_operation():
    """Test list_files successful operation."""
    # Mock successful directory listing
    mock_file1 = Mock()
    mock_file1.name = "file1.md"
    mock_file1.is_file.return_value = True

    mock_file2 = Mock()
    mock_file2.name = "file2.md"
    mock_file2.is_file.return_value = True

    mock_dir = Mock()
    mock_dir.name = "subdir"
    mock_dir.is_file.return_value = False

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_dir", return_value=True):
            with patch("pathlib.Path.iterdir", return_value=[mock_file1, mock_file2, mock_dir]):
                result = list_files("guide", "test_project")
                assert "file1.md" in result
                assert "file2.md" in result
                assert "subdir" not in result  # Should only include files
