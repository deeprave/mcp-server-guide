"""Tests for additional prompt context functionality."""

import pytest
from mcp_server_guide.prompts import check_prompt, implement_prompt, discuss_prompt


class TestPromptAdditionalContext:
    """Tests for prompts with additional bulk content."""

    @pytest.mark.asyncio
    async def test_check_prompt_with_instruction_only(self):
        """Test check prompt with just quoted instruction."""
        result = await check_prompt("analyze this code")

        assert "🔍 **Check Mode Instructions**" in result
        assert "🎯 Focus: analyze this code" in result

    @pytest.mark.asyncio
    async def test_check_prompt_with_instruction_and_content(self):
        """Test check prompt with instruction and additional content."""
        # This should fail initially - we need to implement content detection
        instruction = "analyze these suggestions"
        additional_content = """
src/example.py:10
suggestion: Fix this bug
def broken_function():
    return None
"""

        result = await check_prompt(instruction, additional_content)

        assert "🔍 **Check Mode Instructions**" in result
        assert "🎯 Focus: analyze these suggestions" in result
        assert "src/example.py:10" in result
        assert "suggestion: Fix this bug" in result

    @pytest.mark.asyncio
    async def test_implement_prompt_with_additional_content(self):
        """Test implement prompt with instruction and additional content."""
        instruction = "implement these features"
        additional_content = """
Feature 1: Add validation
Feature 2: Improve error handling
Feature 3: Add tests
"""

        result = await implement_prompt(instruction, additional_content)

        assert "⚙️ **Implementation Mode Instructions**" in result
        assert "🎯 Focus: implement these features" in result
        assert "Feature 1: Add validation" in result
        assert "Feature 2: Improve error handling" in result

    @pytest.mark.asyncio
    async def test_discuss_prompt_with_additional_content(self):
        """Test discuss prompt with instruction and additional content."""
        instruction = "review this design"
        additional_content = """
## Architecture Overview
- Component A handles requests
- Component B processes data
- Component C stores results

## Questions
1. Is this scalable?
2. Are there security concerns?
"""

        result = await discuss_prompt(instruction, additional_content)

        assert "💬 **Discussion Mode Instructions**" in result
        assert "🎯 Focus: review this design" in result
        assert "## Architecture Overview" in result
        assert "## Questions" in result

    @pytest.mark.asyncio
    async def test_prompt_with_empty_additional_content(self):
        """Test prompt with empty additional content."""
        result = await check_prompt("analyze code", "")

        assert "🔍 **Check Mode Instructions**" in result
        assert "🎯 Focus: analyze code" in result

    @pytest.mark.asyncio
    async def test_prompt_with_whitespace_only_content(self):
        """Test prompt with whitespace-only additional content."""
        result = await check_prompt("analyze code", "   \n\n   ")

        assert "🔍 **Check Mode Instructions**" in result
        assert "🎯 Focus: analyze code" in result
