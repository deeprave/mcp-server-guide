"""Tests for prompt normalization preserving additional text."""

import pytest

from mcp_server_guide.guide_integration import GuidePromptHandler


class TestPromptNormalizationFix:
    """Test that prompt normalization preserves additional text correctly."""

    @pytest.fixture
    def handler(self):
        return GuidePromptHandler()

    @pytest.mark.asyncio
    async def test_quoted_multi_word_arguments_preserved(self, handler):
        """Test that quoted multi-word arguments are preserved through normalization."""
        # Test cases with properly quoted arguments
        test_cases = [
            ([":discuss", "This is a multi word argument"], "This is a multi word argument"),
            (
                [":plan", "Now let's work on document-specific-access-spec.md"],
                "Now let's work on document-specific-access-spec.md",
            ),
            (
                [":implement", "Implement feature #123 with proper handling"],
                "Implement feature #123 with proper handling",
            ),
            ([":check", "Verify the implementation works correctly"], "Verify the implementation works correctly"),
            ([":status", "Check current progress on the task"], "Check current progress on the task"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_unquoted_multi_word_arguments_joined(self, handler):
        """Test that unquoted multi-word arguments are properly joined."""
        # When shlex splits unquoted text, we should join it back together
        # This simulates what happens when user types: @guide :discuss Fix this issue
        # shlex.split() would produce: [':discuss', 'Fix', 'this', 'issue']
        # We should join 'Fix', 'this', 'issue' back to 'Fix this issue'

        test_cases = [
            ([":discuss", "Fix", "this", "parsing", "issue"], "Fix this parsing issue"),
            ([":plan", "Work", "on", "the", "new", "feature"], "Work on the new feature"),
            ([":implement", "Add", "tests", "for", "validation"], "Add tests for validation"),
            ([":check", "Run", "all", "quality", "checks"], "Run all quality checks"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_special_characters_preserved(self, handler):
        """Test that special characters in arguments are preserved."""
        test_cases = [
            ([":discuss", "Fix issue #123: handle edge cases"], "Fix issue #123: handle edge cases"),
            ([":implement", "Implement feature @user requested"], "Implement feature @user requested"),
            ([":check", "Test with data: {key: 'value'}"], "Test with data: {key: 'value'}"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_empty_additional_text_handled(self, handler):
        """Test that phase commands work without additional text."""
        test_cases = [":discuss", ":plan", ":implement", ":check", ":status"]

        for flag in test_cases:
            result = await handler.handle_guide_request([flag])
            assert result is not None
            assert len(result) > 0
