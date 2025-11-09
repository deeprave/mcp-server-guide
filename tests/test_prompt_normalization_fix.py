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
            (["-d", "This is a multi word argument"], "This is a multi word argument"),
            (
                ["-p", "Now let's work on document-specific-access-spec.md"],
                "Now let's work on document-specific-access-spec.md",
            ),
            (["-i", "Implement feature #123 with proper handling"], "Implement feature #123 with proper handling"),
            (["-c", "Verify the implementation works correctly"], "Verify the implementation works correctly"),
            (["-s", "Check current progress on the task"], "Check current progress on the task"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_unquoted_multi_word_arguments_joined(self, handler):
        """Test that unquoted multi-word arguments are properly joined."""
        # When shlex splits unquoted text, we should join it back together
        # This simulates what happens when user types: @guide -d Fix this issue
        # shlex.split() would produce: ['-d', 'Fix', 'this', 'issue']
        # We should join 'Fix', 'this', 'issue' back to 'Fix this issue'

        test_cases = [
            (["-d", "Fix", "this", "parsing", "issue"], "Fix this parsing issue"),
            (["-p", "Work", "on", "the", "new", "feature"], "Work on the new feature"),
            (["-i", "Add", "tests", "for", "validation"], "Add tests for validation"),
            (["-c", "Run", "all", "quality", "checks"], "Run all quality checks"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_special_characters_preserved(self, handler):
        """Test that special characters in arguments are preserved."""
        test_cases = [
            (["-d", "Fix issue #123: handle edge cases"], "Fix issue #123: handle edge cases"),
            (["-i", "Implement feature @user requested"], "Implement feature @user requested"),
            (["-c", "Test with data: {key: 'value'}"], "Test with data: {key: 'value'}"),
        ]

        for args, expected_text in test_cases:
            result = await handler.handle_guide_request(args)
            assert expected_text in result, f"Expected '{expected_text}' not found in result for args {args}"

    @pytest.mark.asyncio
    async def test_empty_additional_text_handled(self, handler):
        """Test that phase commands work without additional text."""
        test_cases = ["-d", "-p", "-i", "-c", "-s"]

        for flag in test_cases:
            result = await handler.handle_guide_request([flag])
            assert result is not None
            assert len(result) > 0
