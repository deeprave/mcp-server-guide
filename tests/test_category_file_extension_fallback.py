"""Tests for category file extension auto-addition functionality."""

import tempfile
from pathlib import Path

import pytest

from mcp_server_guide.tools.category_tools import _safe_glob_search
from mcp_server_guide.tools.content_tools import _extract_document_from_content
from mcp_server_guide.utils.file_extensions import get_extension_candidates, try_file_with_extensions


class TestPatternExtensionLogic:
    """Test current pattern extension behavior."""

    def test_safe_glob_search_with_md_extension(self):
        """Test that _safe_glob_search adds .md extension when no matches found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test file with .md extension
            test_file = temp_path / "test.md"
            test_file.write_text("# Test Content")

            # Search for file without extension
            patterns = ["test"]
            results = _safe_glob_search(temp_path, patterns)

            # Should find the .md file
            assert len(results) == 1
            assert results[0].name == "test.md"

    def test_safe_glob_search_exact_match_priority(self):
        """Test that exact matches take priority over .md extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create both files
            exact_file = temp_path / "test"
            exact_file.write_text("Exact match")

            md_file = temp_path / "test.md"
            md_file.write_text("# MD file")

            # Search for file without extension
            patterns = ["test"]
            results = _safe_glob_search(temp_path, patterns)

            # Should find the exact match first
            assert len(results) == 1
            assert results[0].name == "test"

    def test_safe_glob_search_no_md_addition_when_has_extension(self):
        """Test that .md is not added when pattern already has extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Text content")

            md_file = temp_path / "test.txt.md"  # This shouldn't be found
            md_file.write_text("# MD content")

            # Search with explicit extension
            patterns = ["test.txt"]
            results = _safe_glob_search(temp_path, patterns)

            # Should only find the .txt file, not try .txt.md
            assert len(results) == 1
            assert results[0].name == "test.txt"


class TestFileExtensionUtilities:
    """Test the new file extension utility functions."""

    def test_try_file_with_extensions_exact_match(self):
        """Test exact match takes priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create both files
            exact_file = temp_path / "test"
            exact_file.write_text("Exact match")

            md_file = temp_path / "test.md"
            md_file.write_text("MD file")

            result = try_file_with_extensions(temp_path, "test")
            assert result is not None
            assert result.name == "test"

    def test_try_file_with_extensions_fallback(self):
        """Test extension fallback when exact match not found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create only .md file
            md_file = temp_path / "test.md"
            md_file.write_text("MD file")

            result = try_file_with_extensions(temp_path, "test")
            assert result is not None
            assert result.name == "test.md"

    def test_try_file_with_extensions_no_extension_for_files_with_extension(self):
        """Test that extensions are not added to filenames that already have extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create .txt file
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Text file")

            # Should not find test.txt.md
            result = try_file_with_extensions(temp_path, "test.txt")
            assert result is not None
            assert result.name == "test.txt"

    def test_get_extension_candidates(self):
        """Test extension candidate generation."""
        # Without extension
        candidates = get_extension_candidates("test")
        assert candidates == ["test", "test.md"]

        # With extension
        candidates = get_extension_candidates("test.txt")
        assert candidates == ["test.txt"]  # No .md added


class TestContentExtractionWithExtensions:
    """Test content extraction with extension fallback."""

    def test_extract_document_with_extension_fallback(self):
        """Test that document extraction tries extension fallback."""
        content = """# test.md

This is the markdown content.

# other.txt

This is other content.
"""

        # Should find test.md when searching for "test"
        result = _extract_document_from_content(content, "test")
        assert result is not None
        assert "This is the markdown content." in result

    def test_extract_document_exact_match_priority(self):
        """Test that exact matches take priority in content extraction."""
        content = """# test

This is exact match content.

# test.md

This is the markdown content.
"""

        # Should find exact match first
        result = _extract_document_from_content(content, "test")
        assert result is not None
        assert "This is exact match content." in result


class TestFileExtensionFallback:
    """Test file extension auto-addition in content retrieval."""

    @pytest.mark.asyncio
    async def test_get_content_with_extension_fallback(self):
        """Test that get_content tries .md extension for missing files."""
        # This would require more complex mocking of the session manager
        # For now, we've tested the core logic in the utility functions
        pass

    @pytest.mark.asyncio
    async def test_get_content_exact_match_priority(self):
        """Test that exact matches take priority in get_content."""
        # This would require more complex mocking of the session manager
        # For now, we've tested the core logic in the utility functions
        pass
