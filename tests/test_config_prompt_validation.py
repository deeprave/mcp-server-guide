"""Tests for config prompt input validation."""

import json

import pytest
from src.mcp_server_guide.prompts import config_prompt


@pytest.mark.asyncio
async def test_config_prompt_empty_project_name() -> None:
    """Test that empty project name is rejected."""
    result = await config_prompt(project="   ", list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Project name cannot be empty" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_long_project_name() -> None:
    """Test that overly long project name is rejected."""
    long_name = "a" * 256
    result = await config_prompt(project=long_name, list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Project name too long" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_invalid_characters_slash() -> None:
    """Test that project name with slash is rejected."""
    result = await config_prompt(project="project/name", list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Invalid characters in project name" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_invalid_characters_backslash() -> None:
    """Test that project name with backslash is rejected."""
    result = await config_prompt(project="project\\name", list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Invalid characters in project name" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_invalid_characters_dotdot() -> None:
    """Test that project name with .. is rejected."""
    result = await config_prompt(project="../project", list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Invalid characters in project name" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_invalid_characters_null() -> None:
    """Test that project name with null byte is rejected."""
    result = await config_prompt(project="project\0name", list_projects=False, verbose=False)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error_type"] == "validation"
    assert "Invalid characters in project name" in parsed["error"]


@pytest.mark.asyncio
async def test_config_prompt_valid_project_name_with_spaces():
    """Test that project name with spaces is trimmed and accepted."""
    # This will fail to find the project but should pass validation
    result = await config_prompt(project="  valid-project  ", list_projects=False, verbose=False)
    # Should not contain validation errors
    assert "Error: Project name cannot be empty" not in result
    assert "Error: Invalid characters" not in result
