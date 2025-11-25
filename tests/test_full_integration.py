"""Full integration tests - Updated for instruction-based approach."""

import pytest

from mcp_server_guide.prompts import check_prompt, discuss_prompt, implement_prompt, plan_prompt, status_prompt


@pytest.mark.asyncio
async def test_all_prompts_are_callable():
    """Test that all prompts are callable and return non-empty strings."""
    prompts = [discuss_prompt, plan_prompt, implement_prompt, check_prompt, status_prompt]

    for prompt_func in prompts:
        result = await prompt_func()
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_all_prompts_include_user_text():
    """Test that all prompts include user-provided text."""
    user_text = "test user input"
    prompts = [discuss_prompt, plan_prompt, implement_prompt, check_prompt, status_prompt]

    for prompt_func in prompts:
        result = await prompt_func(user_text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert user_text in result


@pytest.mark.asyncio
async def test_prompts_return_different_content():
    """Test that different prompts return different content."""
    discuss_result = await discuss_prompt()
    plan_result = await plan_prompt()
    implement_result = await implement_prompt()
    check_result = await check_prompt()

    # All should be different
    results = [discuss_result, plan_result, implement_result, check_result]
    unique_results = set(results)
    assert len(unique_results) == len(results)


@pytest.mark.asyncio
async def test_concurrent_prompt_calls():
    """Test multiple prompts called concurrently."""
    import asyncio

    tasks = [discuss_prompt(), plan_prompt(), implement_prompt(), check_prompt(), status_prompt()]
    results = await asyncio.gather(*tasks)

    # All should complete successfully
    assert len(results) == 5
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_rapid_sequential_calls():
    """Test rapid sequential prompt calls."""
    results = []
    for _ in range(10):
        result = await status_prompt()
        results.append(result)

    # All calls should succeed
    assert len(results) == 10
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0
