"""Tests for smart pattern matching with .md extension."""

import tempfile
from pathlib import Path
from mcp_server_guide.tools.category_tools import _safe_glob_search


async def test_pattern_matching_adds_md_when_needed():
    """Test that patterns without extension get .md added when no match found."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a .md file
        (temp_path / "guidelines.md").write_text("# Guidelines")

        # Pattern without extension should find .md file
        result = _safe_glob_search(temp_path, ["guidelines"])
        assert len(result) == 1
        assert result[0].name == "guidelines.md"


async def test_pattern_matching_prefers_exact_match():
    """Test that exact matches are preferred over .md extension."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create both files
        (temp_path / "guidelines").write_text("# Guidelines")
        (temp_path / "guidelines.md").write_text("# Guidelines MD")

        # Pattern should find exact match first
        result = _safe_glob_search(temp_path, ["guidelines"])
        assert len(result) == 1
        assert result[0].name == "guidelines"


async def test_pattern_with_extension_unchanged():
    """Test that patterns with extensions work as before."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create files
        (temp_path / "test.txt").write_text("# Test")
        (temp_path / "test.md").write_text("# Test MD")

        # Pattern with extension should work normally
        result = _safe_glob_search(temp_path, ["test.txt"])
        assert len(result) == 1
        assert result[0].name == "test.txt"
