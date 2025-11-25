"""Tests for @plan prompt functionality."""

import pytest

from mcp_server_guide.prompts import plan_prompt


@pytest.mark.asyncio
async def test_plan_prompt_is_callable():
    """Test that plan prompt is callable and returns non-empty string."""
    result = await plan_prompt()

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_plan_prompt_includes_user_text():
    """Test that plan prompt includes user-provided text in output."""
    user_text = "database design for user authentication"
    result = await plan_prompt(user_text)

    assert isinstance(result, str)
    assert len(result) > 0
    assert user_text in result
