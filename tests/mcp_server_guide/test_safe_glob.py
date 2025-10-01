"""Tests for safe glob functionality with limits and symlink detection."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.mcp_server_guide.tools.category_tools import _safe_glob_search, MAX_GLOB_DEPTH, MAX_DOCUMENTS_PER_GLOB


async def test_safe_glob_depth_limit():
    """Test that safe glob respects maximum depth limit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create nested directories beyond MAX_GLOB_DEPTH
        deep_path = base_path
        for i in range(MAX_GLOB_DEPTH + 2):
            deep_path = deep_path / f"level{i}"
            deep_path.mkdir()

        # Create files at different depths
        (base_path / "shallow.md").write_text("shallow content")
        (base_path / "level0" / "medium.md").write_text("medium content")
        (deep_path / "deep.md").write_text("deep content")

        # Search with recursive pattern
        results = _safe_glob_search(base_path, ["**/*.md"])

        # Should find shallow and medium files, but not deep file
        result_names = [f.name for f in results]
        assert "shallow.md" in result_names
        assert "medium.md" in result_names
        assert "deep.md" not in result_names


async def test_safe_glob_document_count_limit():
    """Test that safe glob respects maximum document count limit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create more files than the limit
        for i in range(MAX_DOCUMENTS_PER_GLOB + 10):
            (base_path / f"file{i:03d}.md").write_text(f"content {i}")

        # Search for all files
        results = _safe_glob_search(base_path, ["*.md"])

        # Should be limited to MAX_DOCUMENTS_PER_GLOB
        assert len(results) == MAX_DOCUMENTS_PER_GLOB


async def test_safe_glob_symlink_detection():
    """Test that safe glob detects and handles symlinks safely."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create original file
        original_file = base_path / "original.md"
        original_file.write_text("original content")

        # Create symlink to the file
        symlink_file = base_path / "symlink.md"
        try:
            symlink_file.symlink_to(original_file)
        except OSError:
            # Skip test if symlinks not supported on this system
            pytest.skip("Symlinks not supported on this system")

        # Search for files
        results = _safe_glob_search(base_path, ["*.md"])

        # Should find both files but handle symlink safely
        assert len(results) >= 1
        result_names = [f.name for f in results]
        assert "original.md" in result_names


async def test_safe_glob_circular_symlink_prevention():
    """Test that safe glob prevents circular symlink issues."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create directories
        dir1 = base_path / "dir1"
        dir2 = base_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Create files
        (dir1 / "file1.md").write_text("content 1")
        (dir2 / "file2.md").write_text("content 2")

        try:
            # Create circular symlinks
            (dir1 / "link_to_dir2").symlink_to(dir2)
            (dir2 / "link_to_dir1").symlink_to(dir1)
        except OSError:
            # Skip test if symlinks not supported
            pytest.skip("Symlinks not supported on this system")

        # Search recursively - should not hang or crash
        results = _safe_glob_search(base_path, ["**/*.md"])

        # Should find files without infinite recursion
        assert len(results) >= 2
        result_names = [f.name for f in results]
        assert "file1.md" in result_names
        assert "file2.md" in result_names


async def test_safe_glob_deduplication():
    """Test that safe glob removes duplicate files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create file
        (base_path / "test.md").write_text("test content")

        # Search with overlapping patterns
        results = _safe_glob_search(base_path, ["*.md", "test.*", "**/*.md"])

        # Should deduplicate and return only one instance
        assert len(results) == 1
        assert results[0].name == "test.md"


async def test_safe_glob_memory_efficiency():
    """Test that safe glob uses iglob for memory efficiency."""
    with patch("src.mcp_server_guide.tools.category_tools.glob.iglob") as mock_iglob:
        mock_iglob.return_value = []

        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            _safe_glob_search(base_path, ["*.md"])

        # Should use iglob instead of glob.glob
        mock_iglob.assert_called()


async def test_safe_glob_error_handling():
    """Test that safe glob handles errors gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create a file
        (base_path / "good.md").write_text("good content")

        # Search with invalid pattern (should not crash)
        results = _safe_glob_search(base_path, ["*.md", "[invalid"])

        # Should still find the good file
        assert len(results) >= 1
        assert results[0].name == "good.md"


async def test_safe_glob_outside_search_directory():
    """Test that safe glob skips files outside search directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        outside_path = Path(temp_dir).parent

        # Create file in search directory
        (base_path / "inside.md").write_text("inside content")

        # Create symlink pointing outside search directory
        try:
            outside_file = outside_path / "outside.md"
            outside_file.write_text("outside content")
            (base_path / "link_outside.md").symlink_to(outside_file)
        except OSError:
            pytest.skip("Symlinks not supported on this system")

        # Search should only find files within search directory
        results = _safe_glob_search(base_path, ["*.md"])

        # Should find inside file but skip outside file
        result_names = [f.name for f in results]
        assert "inside.md" in result_names
        # outside.md should be skipped due to being outside search directory
