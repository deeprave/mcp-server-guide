"""Tests for @discuss prompt functionality."""

import pytest
from pathlib import Path
from mcp_server_guide.prompts import discuss_prompt


@pytest.mark.asyncio
async def test_discuss_prompt_provides_file_removal_instructions(temp_project_dir):
    """Test that discuss prompt provides instructions to remove files."""
    # Create .consent file
    Path(".consent").write_text("implementation")

    result = await discuss_prompt("test discussion")

    # Should provide instructions to remove .consent file
    assert "Remove `.consent` file" in result or "remove" in result.lower()
    assert ".consent" in result
    # File should still exist since server doesn't manipulate it
    assert Path(".consent").exists()


@pytest.mark.asyncio
async def test_discuss_prompt_provides_issue_file_instructions(temp_project_dir):
    """Test that discuss prompt provides instructions about .issue file."""
    # Create .issue file
    Path(".issue").write_text("test.md\n")

    result = await discuss_prompt("test discussion")

    # Should provide instructions about .issue file
    assert "Remove `.issue` file" in result or ".issue" in result
    # File should still exist since server doesn't manipulate it
    assert Path(".issue").exists()


@pytest.mark.asyncio
async def test_discuss_prompt_uses_arg_parameter():
    """Test that @discuss includes arg parameter in response"""
    result = await discuss_prompt("machine learning concepts")

    assert "machine learning concepts" in result


@pytest.mark.asyncio
async def test_discuss_prompt_includes_explanatory_text():
    """Test that @discuss includes explanatory text about mode capabilities"""
    result = await discuss_prompt()

    # Should include mode description
    assert "Discuss" in result or "discuss" in result
    assert "ideation" in result.lower() or "exploration" in result.lower()
