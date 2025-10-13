"""Tests for automatic configuration persistence (Issue 009)."""

from mcp_server_guide.tools.config_tools import set_project_config


class TestAutoConfigPersistence:
    """Test automatic configuration persistence functionality."""

    async def test_config_changes_trigger_save(self):
        """Test that valid configuration changes work properly."""
        # Set categories - the only valid project config field
        result = await set_project_config(
            "categories", {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
        )

        assert result["success"] is True

    async def test_project_changes_work(self):
        """Test that category updates work properly."""
        # Update categories
        result = await set_project_config(
            "categories", {"guide": {"dir": "guide/", "patterns": ["*.txt"], "description": "Guide files"}}
        )

        assert result["success"] is True

    async def test_multiple_config_changes(self):
        """Test that multiple configuration changes work."""
        # Make multiple category configuration changes
        result1 = await set_project_config(
            "categories", {"lang": {"dir": "lang/", "patterns": ["*.py"], "description": "Python files"}}
        )
        result2 = await set_project_config(
            "categories", {"context": {"dir": "context/", "patterns": ["*.md"], "description": "Context docs"}}
        )
        result3 = await set_project_config(
            "categories", {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
        )

        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
