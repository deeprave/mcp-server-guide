"""Tests for utility functions."""

from mcp_server_guide.utils import normalize_patterns


class TestNormalizePatterns:
    """Test normalize_patterns function."""

    def test_basic_patterns(self):
        """Test basic space-separated patterns."""
        result = normalize_patterns("*.py *.js")
        assert result == ["*.py", "*.js"]

    def test_comma_separated_patterns(self):
        """Test comma-separated patterns."""
        result = normalize_patterns("*.py, *.js, *.md")
        assert result == ["*.py", "*.js", "*.md"]

    def test_quoted_patterns_with_spaces(self):
        """Test quoted patterns containing spaces."""
        result = normalize_patterns('"foo bar.md" *.py')
        assert result == ["foo bar.md", "*.py"]

    def test_mixed_patterns(self):
        """Test mixed comma and space separated with quotes."""
        result = normalize_patterns('*.py, "file with spaces.txt", *.js')
        assert result == ["*.py", "file with spaces.txt", "*.js"]

    def test_list_input(self):
        """Test list input with patterns containing spaces."""
        result = normalize_patterns(["*.py", "file with spaces.txt", "*.js"])
        assert result == ["*.py", "file with spaces.txt", "*.js"]

    def test_deduplication(self):
        """Test that duplicate patterns are removed while preserving order."""
        result = normalize_patterns("*.py *.js *.py *.md")
        assert result == ["*.py", "*.js", "*.md"]

    def test_empty_input(self):
        """Test empty input handling."""
        assert normalize_patterns("") == []
        assert normalize_patterns([]) == []
        assert normalize_patterns(None) == []

    def test_unmatched_quotes(self):
        """Test handling of unmatched quotes (fallback to simple split)."""
        result = normalize_patterns('*.py "unmatched quote *.js')
        # Should fall back to simple split when shlex fails
        assert "*.py" in result
        assert "*.js" in result

    def test_empty_and_whitespace_patterns(self):
        """Test filtering of empty and whitespace-only patterns."""
        result = normalize_patterns(["*.py", "", "  ", "*.js", "\t"])
        assert result == ["*.py", "*.js"]

    def test_case_sensitivity_preservation(self):
        """Test that original case is preserved in results."""
        result = normalize_patterns("*.MD *.js *.Py")
        assert result == ["*.MD", "*.js", "*.Py"]

    def test_string_whitespace_normalization(self):
        """Test normalization of string input with leading/trailing whitespace."""
        result = normalize_patterns("  *.py  ,  *.js  ")
        assert result == ["*.py", "*.js"]
