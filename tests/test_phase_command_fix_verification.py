"""Test to verify the phase command argument handling fix."""

import pytest

from mcp_server_guide.guide_integration import GuidePromptHandler


class TestPhaseCommandFixVerification:
    """Verify that the phase command argument handling fix works correctly."""

    @pytest.fixture
    def handler(self):
        return GuidePromptHandler()

    @pytest.mark.asyncio
    async def test_plan_command_with_quoted_text_end_to_end(self, handler):
        """Test the complete flow from MCP prompt to phase handler."""
        # Simulate the MCP prompt call: @guide -p "Now let's work on document-specific-access-spec.md"
        # This is what gets passed to _guide_prompt as the category parameter
        category_arg = '-p "Now let\'s work on document-specific-access-spec.md"'

        # Simulate what _guide_prompt does with shlex parsing
        import shlex

        args = shlex.split(category_arg)

        # Verify shlex parsing works correctly
        assert args == ["-p", "Now let's work on document-specific-access-spec.md"]

        # Call the handler with the properly parsed arguments
        result = await handler.handle_guide_request(args)

        # Verify the full quoted text is preserved in the result
        assert "Now let's work on document-specific-access-spec.md" in result

        # Verify it's a plan prompt response (contains plan-specific content)
        assert "Plan Mode Instructions" in result or "PLANNING" in result

    @pytest.mark.asyncio
    async def test_all_phase_commands_with_quoted_text(self, handler):
        """Test all phase commands preserve quoted text."""
        test_cases = [
            ('-d "Discussion about the issue"', "Discussion about the issue"),
            ('-p "Planning the implementation"', "Planning the implementation"),
            ('-i "Implementing the solution"', "Implementing the solution"),
            ('-c "Checking the results"', "Checking the results"),
            ('-s "Status of the project"', "Status of the project"),
        ]

        for category_arg, expected_text in test_cases:
            import shlex

            args = shlex.split(category_arg)
            result = await handler.handle_guide_request(args)

            # Each phase command should preserve the quoted text
            assert expected_text in result, f"Failed for {category_arg}: {result}"

    @pytest.mark.asyncio
    async def test_malformed_quotes_fallback(self, handler):
        """Test that malformed quotes fall back to simple split."""
        # Test with unmatched quotes
        category_arg = '-p "unmatched quote'

        # This should not crash and should fall back to simple split
        import shlex

        try:
            args = shlex.split(category_arg)
        except ValueError:
            # This is expected for malformed quotes
            args = category_arg.split()

        result = await handler.handle_guide_request(args)

        # Should still work, even if not perfectly parsed
        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_single_word_arguments_still_work(self, handler):
        """Test that single word arguments still work without quotes."""
        import shlex

        category_arg = "-p topic"
        args = shlex.split(category_arg)

        assert args == ["-p", "topic"]

        result = await handler.handle_guide_request(args)
        assert "topic" in result

    @pytest.mark.asyncio
    async def test_empty_phase_commands_still_work(self, handler):
        """Test that phase commands without additional text still work."""
        import shlex

        category_arg = "-p"
        args = shlex.split(category_arg)

        assert args == ["-p"]

        result = await handler.handle_guide_request(args)
        assert result is not None
        assert len(result) > 0
