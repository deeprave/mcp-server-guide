"""Tests for prompt guide integration system."""

import pytest
from mcp.types import GetPromptResult, PromptMessage

from mcp_server_guide.document_cache import CategoryDocumentCache
from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.session_manager import SessionManager


class TestPromptGuideIntegration:
    """Test prompt guide integration functionality."""

    @pytest.fixture(autouse=True)
    async def setup_cache(self):
        """Clear cache before each test."""
        await CategoryDocumentCache.clear_all()

    @pytest.fixture
    async def server(self):
        """Create a server instance for testing."""
        config = {"docroot": ".", "project": "test"}
        server = await create_server_with_config(config)

        # Register prompts for testing
        from mcp_server_guide.prompts import register_prompts

        register_prompts(server)

        return server

    @pytest.mark.asyncio
    async def test_discuss_prompt_returns_valid_result(self, isolated_config_file, server):
        """Test that @guide -d returns valid result."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await server.get_prompt("guide", {"arg1": "-d test topic"})

        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_implement_prompt_returns_valid_result(self, isolated_config_file, server):
        """Test that @guide -i returns valid result."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await server.get_prompt("guide", {"arg1": "-i test implementation"})

        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_check_prompt_returns_valid_result(self, isolated_config_file, server):
        """Test that @guide -c returns valid result."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await server.get_prompt("guide", {"arg1": "-c"})

        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_status_prompt_returns_valid_result(self, isolated_config_file, server):
        """Test that @guide :status returns valid result."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await server.get_prompt("guide", {"arg1": ":status"})

        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_plan_prompt_returns_valid_result(self, isolated_config_file, server):
        """Test that @guide :plan returns valid result."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        result = await server.get_prompt("guide", {"arg1": ":plan", "arg2": "test planning"})

        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_prompt_guide_caching_works(self, isolated_config_file, server):
        """Test that prompt guide content is cached properly."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Call same prompt twice
        result1 = await server.get_prompt("guide", {"arg1": "-d test"})
        result2 = await server.get_prompt("guide", {"arg1": "-d test"})

        # Both should succeed
        assert isinstance(result1, GetPromptResult)
        assert isinstance(result2, GetPromptResult)

        # Content should be consistent
        content1 = result1.messages[0].content.text
        content2 = result2.messages[0].content.text

        assert content1 == content2
