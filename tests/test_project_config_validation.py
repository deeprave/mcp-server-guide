"""Tests for project configuration validation edge cases."""

import pytest
from unittest.mock import patch
from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.category import Category
from mcp_server_guide.tools.content_tools import _extract_document_from_content


class TestProjectConfigValidation:
    """Tests for project configuration validation scenarios."""

    def test_category_url_validation_empty(self):
        """Test Category with empty URL."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Category(url="   ")

    def test_category_url_validation_invalid_scheme(self):
        """Test Category with invalid URL scheme."""
        with pytest.raises(ValueError, match="must start with http"):
            Category(url="ftp://example.com")

    def test_category_validation_conflict(self):
        """Test Category with both URL and dir."""
        with pytest.raises(ValueError, match="cannot have both"):
            Category(url="http://example.com", dir="/path", patterns=["*.py"])

    def test_category_validation_missing_both(self):
        """Test Category with neither URL nor dir."""
        with pytest.raises(ValueError, match="must have either"):
            Category(description="test")

    def test_extract_document_no_match(self):
        """Test document extraction with no match."""
        content = "Some content without target"
        result = _extract_document_from_content(content, "missing.md")
        assert result is None

    def test_extract_document_with_match(self):
        """Test document extraction with match."""
        content = "# test.md\nContent here\n\n# other.md\nOther"
        result = _extract_document_from_content(content, "test.md")
        assert result == "Content here"

    def test_project_config_validation(self):
        """Test ProjectConfig validation."""
        # Test valid config
        config = ProjectConfig(
            categories={"test": Category(dir="/test", patterns=["*.py"])},
            collections={"coll": Collection(categories=["test"])},
        )
        assert "test" in config.categories
        assert "coll" in config.collections

    def test_project_config_manager_basic(self):
        """Test ProjectConfigManager basic functionality."""
        from mcp_server_guide.project_config import ProjectConfigManager

        manager = ProjectConfigManager()
        # Test that it initializes without error
        assert manager is not None

        # Test load_config with string instead of Path
        with patch("pathlib.Path.exists", return_value=False):
            result = manager.load_config("nonexistent")
            assert result is None
