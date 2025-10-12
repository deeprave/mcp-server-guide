"""Tests for MCP prompts functionality."""

import pytest
from mcp.types import GetPromptResult, PromptMessage
from mcp_server_guide.server import mcp
from mcp_server_guide.session_manager import SessionManager


class TestMCPPrompts:
    """Test MCP prompts functionality."""

    async def test_list_prompts_returns_expected_prompts(self, isolated_config_file):
        """Test that list_prompts handler returns our defined prompts."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        prompts = await mcp.list_prompts()
        assert len(prompts) == 3

        prompt_names = [p.name for p in prompts]
        assert "guide" in prompt_names
        assert "category" in prompt_names
        assert "daic" in prompt_names

    async def test_get_prompt_with_unknown_name_raises_error(self, isolated_config_file):
        """Test that get_prompt handler raises error for unknown prompt name."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        with pytest.raises(Exception):
            await mcp.get_prompt("unknown-prompt", {})

    async def test_guide_prompt_without_arguments(self, isolated_config_file):
        """Test basic guide prompt without arguments."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await mcp.get_prompt("guide", {})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

    async def test_guide_prompt_with_category_argument(self, isolated_config_file):
        """Test guide prompt with category argument."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await mcp.get_prompt("guide", {"category": "lang"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_new_action(self, isolated_config_file):
        """Test category prompt with new action."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await mcp.get_prompt(
            "category", {"action": "new", "name": "test-category", "dir": "test/", "patterns": "*.md"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_edit_action(self, isolated_config_file):
        """Test category prompt with edit action."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await mcp.get_prompt("category", {"action": "edit", "name": "test-category", "patterns": "*.md,*.txt"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_category_prompt_with_del_action(self, isolated_config_file):
        """Test category prompt with del action."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await mcp.get_prompt("category", {"action": "del", "name": "test-category"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
