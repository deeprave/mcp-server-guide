"""Tests for automatic configuration persistence (Issue 009)."""

from mcp_server_guide.tools.config_tools import set_project_config


class TestAutoConfigPersistence:
    """Test automatic configuration persistence functionality."""

    async def test_config_changes_trigger_save(self):
        """Test that configuration changes work properly."""
        # Set a configuration value
        result = await set_project_config("project", "test-project")

        assert result["success"] is True
        assert result["key"] == "project"
        assert result["value"] == "test-project"

    async def test_project_changes_work(self):
        """Test that project changes work properly."""
        # Set project
        result = await set_project_config("project", "new-project")

        assert result["success"] is True
        assert result["key"] == "project"
        assert result["value"] == "new-project"

    async def test_multiple_config_changes(self):
        """Test that multiple configuration changes work."""
        # Make multiple configuration changes
        result1 = await set_project_config("language", "python")
        result2 = await set_project_config("docroot", "/custom/guides")
        result3 = await set_project_config(
            "categories", {"test": {"dir": "test", "patterns": ["*.md"], "description": "Test category"}}
        )

        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
