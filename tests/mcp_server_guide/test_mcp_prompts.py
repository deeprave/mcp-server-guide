"""Tests for MCP prompts functionality."""

import pytest
from mcp.types import GetPromptResult, PromptMessage
from mcp_server_guide.server import mcp


class TestMCPPrompts:
    """Test MCP prompts functionality."""

    async def test_list_prompts_returns_expected_prompts(self):
        """Test that list_prompts handler returns our defined prompts."""
        prompts = await mcp.list_prompts()
        assert len(prompts) == 4

        prompt_names = [p.name for p in prompts]
        assert "guide" in prompt_names
        assert "guide-category" in prompt_names
        assert "g-category" in prompt_names
        assert "daic" in prompt_names

    async def test_get_prompt_with_unknown_name_raises_error(self):
        """Test that get_prompt handler raises error for unknown prompt name."""
        # This should fail initially as we haven't implemented the handler yet
        with pytest.raises(Exception):
            await mcp.get_prompt("unknown-prompt", {})

    async def test_guide_prompt_without_arguments(self):
        """Test basic guide prompt without arguments."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt("guide", {})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

    async def test_guide_prompt_with_category_argument(self):
        """Test guide prompt with category argument."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt("guide", {"category": "lang"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_guide_category_prompt_with_new_action(self):
        """Test guide-category prompt with new action."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt(
            "guide-category", {"action": "new", "name": "test-category", "dir": "test/", "patterns": "*.md"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_guide_category_prompt_with_edit_action(self):
        """Test guide-category prompt with edit action."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt(
            "guide-category", {"action": "edit", "name": "test-category", "patterns": "*.md,*.txt"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_guide_category_prompt_with_del_action(self):
        """Test guide-category prompt with del action."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt("guide-category", {"action": "del", "name": "test-category"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0

    async def test_g_category_alias_prompt(self):
        """Test g-category alias prompt."""
        # This should fail initially as we haven't implemented the handler yet
        result = await mcp.get_prompt("g-category", {"action": "new", "name": "test-category"})
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
