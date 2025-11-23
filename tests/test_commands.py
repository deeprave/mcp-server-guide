"""Tests for commands module."""

import pytest


@pytest.mark.parametrize(
    "cmd_constant,expected_pattern,expected_has_prompt,expected_category",
    [
        ("CMD_DISCUSS", ":discuss", True, "phase"),
        ("CMD_PLAN", ":plan", True, "phase"),
        ("CMD_IMPLEMENT", ":implement", True, "phase"),
        ("CMD_CHECK", ":check", True, "phase"),
        ("CMD_STATUS", ":status", True, "utility"),
        ("CMD_SEARCH", ":search", False, "utility"),
        ("CMD_HELP", ":help", True, "utility"),
        ("CMD_CONFIG", ":config", False, "utility"),
        ("CMD_CLONE", ":clone", False, "utility"),
        ("CMD_AGENT_INFO", ":agent-info", False, "utility"),
        ("CMD_CATEGORY", ":category", False, "management"),
        ("CMD_COLLECTION", ":collection", False, "management"),
        ("CMD_DOCUMENT", ":document", False, "management"),
    ],
)
def test_command_metadata(cmd_constant, expected_pattern, expected_has_prompt, expected_category):
    """Test individual command metadata is correct."""
    # Import the constant dynamically
    import mcp_server_guide.commands as cmds
    from mcp_server_guide.commands import COMMANDS

    cmd_value = getattr(cmds, cmd_constant)
    cmd_info = COMMANDS[cmd_value]

    # Verify name matches constant value
    assert cmd_info.name == cmd_value

    # Verify usage_pattern uses actual command value
    assert cmd_info.usage_pattern == expected_pattern

    # Verify has_prompt_document matches implementation
    assert cmd_info.has_prompt_document == expected_has_prompt

    # Verify category is correct
    assert cmd_info.category == expected_category

    # Verify required fields are present and correct types
    assert isinstance(cmd_info.description, str)
    assert isinstance(cmd_info.usage, str)
    assert isinstance(cmd_info.help_text, str)


@pytest.mark.parametrize(
    "category,expected_commands",
    [
        ("phase", {"discuss", "plan", "implement", "check"}),
        ("utility", {"status", "search", "help", "config", "clone", "agent-info"}),
        ("management", {"category", "collection", "document"}),
    ],
)
def test_command_categories(category, expected_commands):
    """Test commands are correctly categorized."""
    from mcp_server_guide.commands import COMMANDS

    actual_commands = {name for name, info in COMMANDS.items() if info.category == category}
    assert actual_commands == expected_commands


def test_command_sets():
    """Test that command category sets are correct."""
    from mcp_server_guide.commands import (
        ALL_COMMANDS,
        COMMANDS_WITH_PROMPTS,
        MANAGEMENT_COMMANDS,
        PHASE_COMMANDS,
        UTILITY_COMMANDS,
    )

    # Verify all are sets
    assert isinstance(ALL_COMMANDS, set)
    assert isinstance(PHASE_COMMANDS, set)
    assert isinstance(UTILITY_COMMANDS, set)
    assert isinstance(MANAGEMENT_COMMANDS, set)
    assert isinstance(COMMANDS_WITH_PROMPTS, set)

    # Verify categories don't overlap
    assert PHASE_COMMANDS.isdisjoint(UTILITY_COMMANDS)
    assert PHASE_COMMANDS.isdisjoint(MANAGEMENT_COMMANDS)
    assert UTILITY_COMMANDS.isdisjoint(MANAGEMENT_COMMANDS)

    # Verify union equals ALL_COMMANDS
    assert PHASE_COMMANDS | UTILITY_COMMANDS | MANAGEMENT_COMMANDS == ALL_COMMANDS


@pytest.mark.parametrize(
    "command,should_exist",
    [
        ("discuss", True),
        ("plan", True),
        ("nonexistent", False),
        ("invalid", False),
    ],
)
def test_get_command_info(command, should_exist):
    """Test get_command_info helper function."""
    from mcp_server_guide.commands import get_command_info

    info = get_command_info(command)

    if should_exist:
        assert info is not None
        assert info.name == command
    else:
        assert info is None
