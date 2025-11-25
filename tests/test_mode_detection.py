"""Tests for mode detection functionality - Updated for instruction-based approach."""

import pytest

from mcp_server_guide.prompts import status_prompt


@pytest.mark.asyncio
async def test_status_is_callable():
    """Test that status prompt is callable and returns non-empty string."""
    result = await status_prompt()

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_status_includes_user_text():
    """Test that status prompt includes user-provided text."""
    user_text = "show current mode"
    result = await status_prompt(user_text)

    assert isinstance(result, str)
    assert len(result) > 0
    assert user_text in result


@pytest.mark.asyncio
async def test_status_returns_consistent_output():
    """Test that status returns consistent output when called multiple times."""
    result1 = await status_prompt()
    result2 = await status_prompt()

    assert result1 == result2
