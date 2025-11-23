"""Tests for @plan prompt functionality."""

from pathlib import Path

import pytest

from mcp_server_guide.prompts import plan_prompt


@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory for tests."""
    import os

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@pytest.mark.asyncio
async def test_plan_prompt_provides_instructions(temp_dir):
    """Test that plan prompt provides file management instructions."""
    # Create .consent file
    Path(".consent").write_text("implementation")

    result = await plan_prompt("test planning")

    # Should provide instructions but not manipulate files
    assert "Remove `.consent` file" in result or "remove" in result.lower()
    assert "Create empty `.issue` file" in result or ".issue" in result
    # Files should remain unchanged since server doesn't manipulate them
    assert Path(".consent").exists()


@pytest.mark.asyncio
async def test_plan_prompt_preserves_existing_issue_file(temp_dir):
    """Test that plan prompt doesn't affect existing .issue file."""
    # Create existing .issue file
    Path(".issue").write_text("existing content")

    result = await plan_prompt("test planning")

    # Should provide instructions about .issue file
    assert ".issue" in result
    # File should remain unchanged
    assert Path(".issue").exists()
    assert Path(".issue").read_text() == "existing content"


@pytest.mark.asyncio
async def test_plan_prompt_uses_arg_parameter(temp_dir):
    """Test that @plan includes arg parameter in response."""
    result = await plan_prompt("database design")

    assert "database design" in result


@pytest.mark.asyncio
async def test_plan_prompt_includes_explanatory_text(temp_dir):
    """Test that @plan includes explanatory text about mode capabilities."""
    result = await plan_prompt()

    # Should include mode description
    assert "Plan" in result or "plan" in result
    assert "planning" in result.lower() or "specification" in result.lower()
