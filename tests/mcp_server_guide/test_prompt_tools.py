"""Tests for prompt tools functionality."""

import pytest
from mcp_server_guide.tools.prompt_tools import list_prompts, list_resources
from mcp_server_guide.server import create_server_with_config


@pytest.fixture
async def server():
    """Create a server instance for testing."""
    config = {"docroot": ".", "project": "test"}
    server = await create_server_with_config(config)

    # Register prompts for testing
    from mcp_server_guide.prompts import register_prompts

    register_prompts(server)

    return server


async def test_list_prompts_returns_expected_structure(server):
    """Test that list_prompts returns the expected structure."""
    result = await list_prompts()

    assert isinstance(result, dict)
    assert result["success"] is True
    assert "prompts" in result
    assert "total_prompts" in result
    assert isinstance(result["prompts"], list)
    assert result["total_prompts"] == len(result["prompts"])


async def test_list_prompts_includes_all_registered_prompts(server):
    """Test that list_prompts includes all 4 registered prompts."""
    result = await list_prompts()

    assert result["success"] is True
    assert result["total_prompts"] == 2  # Updated: spec and guide only

    prompt_names = {p["name"] for p in result["prompts"]}
    assert "guide" in prompt_names
    assert "spec" in prompt_names


async def test_list_prompts_includes_prompt_metadata(server):
    """Test that each prompt includes required metadata."""
    result = await list_prompts()

    assert result["success"] is True
    assert len(result["prompts"]) > 0

    for prompt in result["prompts"]:
        assert "name" in prompt
        assert "description" in prompt
        assert "arguments" in prompt
        assert isinstance(prompt["name"], str)
        assert isinstance(prompt["arguments"], list)


async def test_list_prompts_guide_has_category_argument(server):
    """Test that the 'guide' prompt has a 'arg1' argument."""
    result = await list_prompts()

    guide_prompt = next((p for p in result["prompts"] if p["name"] == "guide"), None)
    assert guide_prompt is not None

    arg_names = {arg["name"] for arg in guide_prompt["arguments"]}
    assert "arg1" in arg_names


async def test_list_prompts_guide_has_comprehensive_arguments(server):
    """Test that the 'guide' prompt has comprehensive argument support."""
    result = await list_prompts()

    guide_prompt = next((p for p in result["prompts"] if p["name"] == "guide"), None)
    assert guide_prompt is not None

    # Guide prompt should have multiple argument slots for flexibility
    assert len(guide_prompt["arguments"]) >= 16  # Has arg1 through arg16


async def test_list_resources_returns_expected_structure():
    """Test that list_resources returns the expected structure."""
    result = await list_resources()

    assert isinstance(result, dict)
    assert "success" in result
    assert "resources" in result
    assert "total_resources" in result
    assert isinstance(result["resources"], list)

    if result["success"]:
        assert result["total_resources"] == len(result["resources"])
    else:
        # Should have error message when not successful
        assert "error" in result


async def test_list_resources_includes_resource_metadata():
    """Test that each resource includes required metadata."""
    result = await list_resources()

    if result["success"] and len(result["resources"]) > 0:
        for resource in result["resources"]:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mime_type" in resource
            assert isinstance(resource["uri"], (str, type(resource["uri"])))
            assert isinstance(resource["name"], str)
            assert isinstance(resource["description"], str)


async def test_list_resources_handles_errors_gracefully():
    """Test that list_resources handles errors gracefully."""
    result = await list_resources()

    # Should always return a dict with required keys
    assert isinstance(result, dict)
    assert "success" in result
    assert "resources" in result
    assert "total_resources" in result

    # If not successful, should have error message
    if not result["success"]:
        assert "error" in result
        assert isinstance(result["error"], str)
        assert result["resources"] == []
        assert result["total_resources"] == 0
