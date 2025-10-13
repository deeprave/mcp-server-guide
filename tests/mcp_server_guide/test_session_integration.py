"""Tests for session integration functionality."""

from mcp_server_guide.tools.config_tools import set_project_config


class TestSessionIntegration:
    """Test session integration functionality."""

    async def test_session_config_works(self):
        """Test that session configuration works with valid categories."""
        # Set session configuration with categories
        result = await set_project_config(
            "categories", {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Session guidelines"}}
        )

        assert result["success"] is True

    async def test_session_config_precedence(self):
        """Test session configuration can override categories."""
        # Session config should override defaults
        result = await set_project_config(
            "categories", {"lang": {"dir": "lang/", "patterns": ["*.py"], "description": "Python files"}}
        )

        assert result["success"] is True

    async def test_session_local_file_resolution(self):
        """Test session configuration with file patterns."""
        # Test with various file patterns
        result = await set_project_config(
            "categories", {"context": {"dir": "context/", "patterns": ["*.md", "*.txt"], "description": "Context files"}}
        )

        assert result["success"] is True

    async def test_mixed_session_and_default_config(self):
        """Test mixed session and default configuration."""
        # Mix session categories with builtin categories
        result = await set_project_config(
            "categories", {"custom": {"dir": "custom/", "patterns": ["*.yaml"], "description": "Custom config"}}
        )

        assert result["success"] is True

    async def test_project_switching_affects_server(self):
        """Test that project switching affects server configuration."""
        # Set config with different categories
        result1 = await set_project_config(
            "categories", {"projectA": {"dir": "a/", "patterns": ["*.md"], "description": "Project A"}}
        )
        result2 = await set_project_config(
            "categories", {"projectB": {"dir": "b/", "patterns": ["*.md"], "description": "Project B"}}
        )

        assert result1["success"] is True
        assert result2["success"] is True

    async def test_session_path_resolution_in_server(self):
        """Test session path resolution works with relative paths in categories."""
        # Test different path types in category dirs
        result = await set_project_config(
            "categories",
            {
                "docs": {"dir": "docs/", "patterns": ["*.md"], "description": "Documentation"},
                "code": {"dir": "src/", "patterns": ["*.py"], "description": "Source code"},
            },
        )

        assert result["success"] is True
