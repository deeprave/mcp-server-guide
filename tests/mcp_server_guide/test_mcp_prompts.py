"""Tests for MCP prompts functionality."""

import pytest
from mcp.types import GetPromptResult, PromptMessage
from mcp_server_guide.server import create_server
from mcp_server_guide.session_manager import SessionManager


class TestMCPPrompts:
    """Test MCP prompts functionality."""

    @pytest.fixture
    async def server(self, isolated_config_file):
        """Create a server instance for testing."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)
        return create_server(config_file=str(isolated_config_file))

    async def test_list_prompts_returns_expected_prompts(self, server):
        """Test that list_prompts handler returns our defined prompts."""
        prompts = await server.list_prompts()
        assert len(prompts) == 9  # Updated to include spec prompt

        prompt_names = [p.name for p in prompts]
        assert "guide" in prompt_names
        assert "category" in prompt_names
        assert "discuss" in prompt_names
        assert "plan" in prompt_names
        assert "status" in prompt_names
        assert "implement" in prompt_names
        assert "check" in prompt_names
        assert "debug" in prompt_names
        assert "spec" in prompt_names

    async def test_get_prompt_with_unknown_name_raises_error(self, server):
        """Test that get_prompt handler raises error for unknown prompt name."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await server.get_prompt("unknown-prompt", {})

    async def test_guide_prompt_without_arguments(self, server):
        """Test basic guide prompt without arguments."""
        result = await server.get_prompt("guide", {})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

    async def test_guide_prompt_with_category_argument(self, server):
        """Test guide prompt with category argument."""
        result = await server.get_prompt("guide", {"category": "lang"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_new_action(self, server):
        """Test category prompt with new action."""
        result = await server.get_prompt(
            "category", {"action": "new", "name": "test-category", "dir": "test/", "patterns": "*.md,*.txt"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_edit_action(self, server):
        """Test category prompt with edit action."""
        result = await server.get_prompt(
            "category", {"action": "edit", "name": "test-category", "patterns": "*.md,*.txt"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_del_action(self, server):
        """Test category prompt with del action."""
        result = await server.get_prompt("category", {"action": "del", "name": "test-category"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
