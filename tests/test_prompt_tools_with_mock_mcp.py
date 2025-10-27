"""Tests for prompt_tools using MockMCP."""

import pytest
from unittest.mock import patch, Mock
from mcp_server_guide.tools.prompt_tools import list_prompts, list_resources
from .mock_mcp import MockMCP


class TestPromptToolsWithMockMCP:
    """Tests for prompt_tools using MockMCP."""

    @pytest.mark.asyncio
    async def test_list_prompts_fallback_to_private_resource_manager(self):
        """Test list_prompts fallback to private resource manager."""
        mock_mcp = MockMCP()
        mock_mcp.add_prompt("test_prompt", "Test description")

        # Create mock with _prompt_manager but no list_prompts method
        mock_mcp._prompt_manager = Mock()
        mock_mcp._prompt_manager.list_prompts.return_value = mock_mcp.prompts

        with patch("mcp_server_guide.server.mcp", mock_mcp):
            result = await list_prompts()
            assert result["success"]
            assert len(result["prompts"]) == 1
            assert result["prompts"][0]["name"] == "test_prompt"

    @pytest.mark.asyncio
    async def test_list_resources_exception_handling(self):
        """Test list_resources exception handling."""
        mock_mcp = MockMCP()
        mock_mcp.set_failure(True, "Resource access failed")

        with patch("mcp_server_guide.server.mcp", mock_mcp):
            result = await list_resources()
            assert not result["success"]
            assert "error" in result

    @pytest.mark.asyncio
    async def test_list_resources_private_resource_manager_sync(self):
        """Test list_resources with private resource manager (sync)."""
        mock_mcp = Mock()
        # Remove public method, keep private resource manager
        del mock_mcp.list_resources
        mock_mcp._resource_manager = Mock()
        mock_mcp._resource_manager.list_resources.return_value = [
            Mock(name="test_resource", description="Test description")
        ]

        with patch("mcp_server_guide.server.mcp", mock_mcp):
            result = await list_resources()
            assert result["success"]
            assert len(result["resources"]) == 1

    @pytest.mark.asyncio
    async def test_list_resources_private_resource_manager_async(self):
        """Test list_resources with private resource manager (async)."""
        mock_mcp = Mock()
        # Remove public method, keep private resource manager
        del mock_mcp.list_resources
        mock_mcp._resource_manager = Mock()

        # Create async function
        async def async_list_resources():
            return [Mock(name="async_resource", description="Async description")]

        mock_mcp._resource_manager.list_resources = async_list_resources

        with patch("mcp_server_guide.server.mcp", mock_mcp):
            result = await list_resources()
            assert result["success"]
            assert len(result["resources"]) == 1
