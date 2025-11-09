"""Test CLI parsing regression fix."""

import pytest
from mcp_server_guide.guide_integration import GuidePromptHandler


class TestCLIRegressionFix:
    """Test that CLI flag parsing works correctly."""

    @pytest.fixture
    def handler(self):
        return GuidePromptHandler()

    @pytest.mark.asyncio
    async def test_implement_flag_with_text(self, handler):
        """Test that @guide -i 'text' calls implement_prompt."""
        args = ["-i", "Fix the parsing logic"]
        result = await handler.handle_guide_request(args)

        # Should contain implement prompt content and the additional text
        assert "Implementation Mode Instructions" in result
        assert "Fix the parsing logic" in result

    @pytest.mark.asyncio
    async def test_implement_flag_without_text(self, handler):
        """Test that @guide -i calls implement_prompt without additional text."""
        args = ["-i"]
        result = await handler.handle_guide_request(args)

        # Should contain implement prompt content
        assert "Implementation Mode Instructions" in result

    @pytest.mark.asyncio
    async def test_unknown_flag_error(self, handler):
        """Test that unknown flags throw proper errors."""
        args = ["-x", "unknown flag"]
        result = await handler.handle_guide_request(args)

        # Should contain error message
        assert "Error" in result or "Unknown" in result
