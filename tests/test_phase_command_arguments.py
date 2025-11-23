"""Tests for phase command argument handling."""

import pytest

from mcp_server_guide.guide_integration import GuidePromptHandler


class TestPhaseCommandArguments:
    """Test phase commands properly capture additional text arguments."""

    @pytest.fixture
    def handler(self):
        return GuidePromptHandler()

    @pytest.mark.asyncio
    async def test_plan_command_with_quoted_text(self, handler):
        """Test that @guide -p 'quoted text' passes text to plan_prompt."""
        # This should capture the quoted text and pass it to plan_prompt
        args = ["-p", "Now let's work on document-specific-access-spec.md"]
        result = await handler.handle_guide_request(args)

        # The result should contain the additional text, not just the plan prompt
        assert "Now let's work on document-specific-access-spec.md" in result

    @pytest.mark.asyncio
    async def test_discuss_command_with_quoted_text(self, handler):
        """Test that @guide -d 'quoted text' passes text to discuss_prompt."""
        args = ["-d", "There is an issue with argument parsing"]
        result = await handler.handle_guide_request(args)

        # The result should contain the additional text
        assert "There is an issue with argument parsing" in result

    @pytest.mark.asyncio
    async def test_implement_command_with_quoted_text(self, handler):
        """Test that @guide -i 'quoted text' passes text to implement_prompt."""
        args = ["-i", "Fix the parsing logic"]
        result = await handler.handle_guide_request(args)

        # The result should contain the additional text
        assert "Fix the parsing logic" in result

    @pytest.mark.asyncio
    async def test_check_command_with_quoted_text(self, handler):
        """Test that @guide -c 'quoted text' passes text to check_prompt."""
        args = ["-c", "Verify the implementation works"]
        result = await handler.handle_guide_request(args)

        # The result should contain the additional text
        assert "Verify the implementation works" in result

    @pytest.mark.asyncio
    async def test_status_command_with_quoted_text(self, handler):
        """Test that @guide -s 'quoted text' passes text to status_prompt."""
        args = ["-s", "Check current progress"]
        result = await handler.handle_guide_request(args)

        # The result should contain the additional text
        assert "Check current progress" in result

    @pytest.mark.asyncio
    async def test_phase_command_without_additional_text(self, handler):
        """Test that phase commands work without additional text."""
        args = ["-p"]
        result = await handler.handle_guide_request(args)

        # Should still work, just without additional context
        assert result is not None
        assert len(result) > 0
