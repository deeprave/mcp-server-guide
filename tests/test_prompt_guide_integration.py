"""Tests for prompt guide integration system."""

import pytest
from pathlib import Path
from mcp.types import GetPromptResult, PromptMessage
from mcp_server_guide.server import mcp
from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.document_cache import CategoryDocumentCache


class TestPromptGuideIntegration:
    """Test prompt guide integration functionality."""

    @pytest.fixture(autouse=True)
    async def setup_cache(self):
        """Clear cache before each test."""
        await CategoryDocumentCache.clear_all()

    @pytest.mark.asyncio
    async def test_discuss_prompt_works_with_or_without_guide(self, isolated_config_file):
        """Test that @discuss works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @discuss prompt
        result = await mcp.get_prompt("discuss", {})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should be removed
        assert not consent_file.exists()

    @pytest.mark.asyncio
    async def test_implement_prompt_works_with_or_without_guide(self, isolated_config_file):
        """Test that @implement works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create .consent file with "implementation"
        consent_file = Path.cwd() / ".consent"
        consent_file.write_text("implementation")

        # Act: Call @implement prompt
        result = await mcp.get_prompt("implement", {})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should remain unchanged
        assert consent_file.exists()
        assert consent_file.read_text().strip() == "implementation"

    @pytest.mark.asyncio
    async def test_check_prompt_works_with_or_without_guide(self, isolated_config_file):
        """Test that @check works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create .consent file with "check"
        consent_file = Path.cwd() / ".consent"
        consent_file.write_text("check")

        # Act: Call @check prompt
        result = await mcp.get_prompt("check", {})

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
    async def test_status_prompt_works_with_or_without_guide(self, isolated_config_file):
        """Test that @status works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @status prompt
        result = await mcp.get_prompt("status", {})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # State check: .consent file should remain absent
        assert not consent_file.exists()

    @pytest.mark.asyncio
    async def test_plan_prompt_works_with_or_without_guide(self, isolated_config_file):
        """Test that @plan works regardless of guide content availability."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @plan prompt
        result = await mcp.get_prompt("plan", {})

        # Assert: Should work regardless of guide content
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) > 0
        assert isinstance(result.messages[0], PromptMessage)

        content = result.messages[0].content.text
        assert isinstance(content, str) and len(content) > 0

        # Check that plan prompt provides correct instructions
        assert "Remove `.consent` file" in content or "remove" in content.lower()
        assert "Create empty `.issue` file" in content or ".issue" in content

    @pytest.mark.asyncio
    async def test_prompt_guide_caching_works(self, isolated_config_file):
        """Test that prompt guide content caching works correctly."""
        # Arrange: Set up session manager with isolated config
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Ensure no .consent file exists (planning mode)
        consent_file = Path.cwd() / ".consent"
        if consent_file.exists():
            consent_file.unlink()

        # Act: Call @discuss prompt twice
        result1 = await mcp.get_prompt("discuss", {})
        result2 = await mcp.get_prompt("discuss", {})

        # Assert: Both calls should succeed (caching should work transparently)
        assert isinstance(result1, GetPromptResult)
        assert isinstance(result2, GetPromptResult)

        content1 = result1.messages[0].content.text
        content2 = result2.messages[0].content.text

        # Results should be consistent (cached properly)
        assert content1 == content2
        assert isinstance(content1, str) and len(content1) > 0
