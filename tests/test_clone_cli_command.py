"""Tests for @guide clone CLI command integration."""

import pytest
from src.mcp_server_guide.cli_parser_click import parse_command


def test_clone_command_parsing_with_target():
    """Test parsing @guide clone with explicit target."""
    args = ["clone", "source-proj", "target-proj"]
    command = parse_command(args)

    assert command.type == "clone"
    assert command.data["source_project"] == "source-proj"
    assert command.data["target_project"] == "target-proj"
    assert command.data["force"] is False


def test_clone_command_parsing_without_target():
    """Test parsing @guide clone without target (defaults to current)."""
    args = ["clone", "source-proj"]
    command = parse_command(args)

    assert command.type == "clone"
    assert command.data["source_project"] == "source-proj"
    assert command.data["target_project"] is None
    assert command.data["force"] is False


def test_clone_command_parsing_with_force():
    """Test parsing @guide clone with --force flag."""
    args = ["clone", "source-proj", "target-proj", "--force"]
    command = parse_command(args)

    assert command.type == "clone"
    assert command.data["source_project"] == "source-proj"
    assert command.data["target_project"] == "target-proj"
    assert command.data["force"] is True


def test_clone_command_parsing_force_without_target():
    """Test parsing @guide clone with --force but no target."""
    args = ["clone", "source-proj", "--force"]
    command = parse_command(args)

    assert command.type == "clone"
    assert command.data["source_project"] == "source-proj"
    assert command.data["target_project"] is None
    assert command.data["force"] is True


@pytest.mark.asyncio
async def test_clone_command_handler_integration(isolated_config_file):
    """Test full integration of clone command through handler."""
    from src.mcp_server_guide.guide_integration import GuidePromptHandler
    from src.mcp_server_guide.session_manager import SessionManager
    from src.mcp_server_guide.tools.project_tools import switch_project
    from src.mcp_server_guide.tools.category_tools import add_category

    session = SessionManager()
    session._set_config_filename(isolated_config_file)
    handler = GuidePromptHandler()

    # Create source project with custom category
    await switch_project("source-proj")
    await add_category(name="custom", dir="custom/", patterns=["*.txt"])

    # Use handler to clone via CLI command
    result = await handler.handle_guide_request(["clone", "source-proj", "target-proj"])

    assert "success" in result.lower() or "cloned" in result.lower()

    # Verify target has the custom category
    await switch_project("target-proj")
    config = session.session_state.get_project_config()
    assert "custom" in config.categories
