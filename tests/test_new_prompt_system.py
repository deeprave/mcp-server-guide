"""Tests for new prompt system - Updated for instruction-based approach."""

import pytest

from mcp_server_guide.prompts import check_prompt, discuss_prompt, implement_prompt, plan_prompt, status_prompt


class TestDiscussPrompt:
    """Test discuss prompt functionality."""

    @pytest.mark.asyncio
    async def test_discuss_is_callable(self):
        """Test that discuss prompt is callable and returns non-empty string."""
        result = await discuss_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_discuss_includes_user_text(self):
        """Test that discuss prompt includes user-provided text."""
        user_text = "refactoring authentication module"
        result = await discuss_prompt(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result


class TestPlanPrompt:
    """Test plan prompt functionality."""

    @pytest.mark.asyncio
    async def test_plan_is_callable(self):
        """Test that plan prompt is callable and returns non-empty string."""
        result = await plan_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_plan_includes_user_text(self):
        """Test that plan prompt includes user-provided text."""
        user_text = "implement caching layer"
        result = await plan_prompt(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result


class TestImplementPrompt:
    """Test implement prompt functionality."""

    @pytest.mark.asyncio
    async def test_implement_is_callable(self):
        """Test that implement prompt is callable and returns non-empty string."""
        result = await implement_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_implement_includes_user_text(self):
        """Test that implement prompt includes user-provided text."""
        user_text = "add error handling"
        result = await implement_prompt(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result


class TestCheckPrompt:
    """Test check prompt functionality."""

    @pytest.mark.asyncio
    async def test_check_is_callable(self):
        """Test that check prompt is callable and returns non-empty string."""
        result = await check_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_check_includes_user_text(self):
        """Test that check prompt includes user-provided text."""
        user_text = "verify type annotations"
        result = await check_prompt(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result


class TestStatusPrompt:
    """Test status prompt functionality."""

    @pytest.mark.asyncio
    async def test_status_is_callable(self):
        """Test that status prompt is callable and returns non-empty string."""
        result = await status_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_status_includes_user_text(self):
        """Test that status prompt includes user-provided text."""
        user_text = "check current progress"
        result = await status_prompt(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result
