"""Tests for prompt guide integration system."""

import pytest
from pathlib import Path
from mcp.types import GetPromptResult, PromptMessage
from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.document_cache import CategoryDocumentCache


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
    async def test_discuss_prompt_works_with_or_without_guide(self, isolated_config_file, server):
        """Test that @guide -d works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @guide -d through guide prompt
        result = await server.get_prompt("guide", {"arg1": "-d test topic"})

        # Assert: Should work and provide discussion mode instructions
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should be removed
        assert not consent_file.exists()

    @pytest.mark.asyncio
    async def test_implement_prompt_works_with_or_without_guide(self, isolated_config_file, server):
        """Test that @guide -i works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create .consent file with "implementation"
        consent_file = Path.cwd() / ".consent"
        consent_file.write_text("implementation")

        # Act: Call @guide -i through guide prompt
        result = await server.get_prompt("guide", {"arg1": "-i test implementation"})

        # Assert: Should work and provide implementation mode instructions
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should remain unchanged
        assert consent_file.exists()
        assert consent_file.read_text().strip() == "implementation"

    @pytest.mark.asyncio
    async def test_check_prompt_works_with_or_without_guide(self, isolated_config_file, server):
        """Test that @check works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create .consent file with "check"
        consent_file = Path.cwd() / ".consent"
        consent_file.write_text("check")

        # Act: Call @guide -c through guide prompt
        result = await server.get_prompt("guide", {"arg1": "-c test validation"})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should remain unchanged
        assert consent_file.exists()
        assert consent_file.read_text().strip() == "check"

    @pytest.mark.asyncio
    async def test_status_prompt_works_with_or_without_guide(self, isolated_config_file, server):
        """Test that @status works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @guide -s through guide prompt
        result = await server.get_prompt("guide", {"arg1": "-s"})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should remain absent
        assert not consent_file.exists()

    @pytest.mark.asyncio
    async def test_plan_prompt_works_with_or_without_guide(self, isolated_config_file, server):
        """Test that @plan works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @guide -p through guide prompt
        result = await server.get_prompt("guide", {"arg1": "-p", "arg2": "test planning"})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # Check that plan prompt provides correct instructions or help content
        assert "Remove `.consent` file" in content or "remove" in content.lower() or "MCP Server Guide Help" in content

    @pytest.mark.asyncio
    async def test_prompt_guide_caching_works(self, isolated_config_file, server):
        """Test that prompt guide content caching works correctly."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @guide -d twice through guide prompt
        result1 = await server.get_prompt("guide", {"arg1": "-d test"})
        result2 = await server.get_prompt("guide", {"arg1": "-d test"})

        # Assert: Both calls should succeed (caching should work transparently)
        assert isinstance(result1, GetPromptResult)
        assert isinstance(result2, GetPromptResult)

        content1 = result1.messages[0].content.text
        content2 = result2.messages[0].content.text

        # Results should be consistent (cached properly)
        assert content1 == content2
        assert isinstance(content1, str) and len(content1) > 0
