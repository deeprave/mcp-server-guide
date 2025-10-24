"""Full integration tests - Updated for instruction-based approach."""

import pytest
from pathlib import Path
from mcp_server_guide.prompts import discuss_prompt, plan_prompt, implement_prompt, check_prompt, status_prompt


@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory for tests."""
    import os

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@pytest.mark.asyncio
async def test_complete_workflow_provides_instructions(temp_dir):
    """Test that complete workflow provides proper instructions."""
    # Test discuss -> plan -> implement workflow
    discuss_result = await discuss_prompt()
    assert "Remove `.consent` file" in discuss_result or "remove" in discuss_result.lower()
    assert "Remove `.issue` file" in discuss_result or ".issue" in discuss_result

    plan_result = await plan_prompt()
    assert "Remove `.consent` file" in plan_result or "remove" in plan_result.lower()
    assert "Create empty `.issue` file" in plan_result or ".issue" in plan_result

    implement_result = await implement_prompt()
    assert "Create `.consent` file" in implement_result or ".consent" in implement_result
    assert "implementation" in implement_result.lower()


@pytest.mark.asyncio
async def test_status_provides_comprehensive_instructions(temp_dir):
    """Test that status provides comprehensive mode detection instructions."""
    status = await status_prompt()

    # Should provide instructions for all mode detection scenarios
    assert "Status Check" in status or "check" in status.lower()
    assert ".consent" in status
    assert ".issue" in status
    assert "Implementation" in status or "implementation" in status.lower()
    assert "Check" in status or "check" in status.lower()
    assert "Discussion" in status or "discussion" in status.lower()
    assert "Plan" in status or "plan" in status.lower()


@pytest.mark.asyncio
async def test_prompt_instruction_consistency(temp_dir):
    """Test that prompts provide consistent instructions."""
    # All prompts should provide instructions, not manipulate files
    discuss_result = await discuss_prompt()
    plan_result = await plan_prompt()
    implement_result = await implement_prompt()
    check_result = await check_prompt()

    # Each should contain mode-specific instructions
    assert "Discuss" in discuss_result or "discuss" in discuss_result.lower()
    assert "Plan" in plan_result or "plan" in plan_result.lower()
    assert "Implementation" in implement_result or "implementation" in implement_result.lower()
    assert "Check" in check_result or "check" in check_result.lower()


@pytest.mark.asyncio
async def test_argument_handling_across_prompts(temp_dir):
    """Test that prompts handle arguments correctly."""
    test_arg = "test argument"

    discuss_result = await discuss_prompt(test_arg)
    plan_result = await plan_prompt(test_arg)
    implement_result = await implement_prompt(test_arg)
    check_result = await check_prompt(test_arg)

    # Each should include the argument
    assert test_arg in discuss_result
    assert test_arg in plan_result
    assert test_arg in implement_result
    assert test_arg in check_result


@pytest.mark.asyncio
async def test_server_provides_instructions_not_file_operations(temp_dir):
    """Test that server provides instructions instead of performing file operations."""
    # Create files to ensure server doesn't manipulate them
    Path(".consent").write_text("original")
    Path(".issue").write_text("original")

    # Run all prompts
    await discuss_prompt()
    await plan_prompt()
    await implement_prompt()
    await check_prompt()

    # Files should remain unchanged since server doesn't manipulate them
    assert Path(".consent").read_text() == "original"
    assert Path(".issue").read_text() == "original"


class TestConcurrencyAndFileLocking:
    """Test concurrent prompt calls and file locking scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_prompt_calls(self, temp_dir):
        """Test multiple prompts called concurrently."""
        import asyncio

        # Run multiple prompts concurrently
        tasks = [discuss_prompt(), plan_prompt(), implement_prompt(), check_prompt(), status_prompt()]

        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_file_locked_scenarios(self, temp_dir):
        """Test behavior when files are locked or inaccessible."""
        import os

        # Create a locked file (skip on Windows)
        if os.name != "nt":
            locked_file = Path(".consent")
            locked_file.write_text("test")
            locked_file.chmod(0o000)  # No permissions

            # Prompts should still work since they don't read files
            result = await status_prompt()
            assert isinstance(result, str)

            # Restore permissions for cleanup
            locked_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_rapid_sequential_calls(self, temp_dir):
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
