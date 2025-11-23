"""Tests for commands module."""


def test_commands_registry_structure():
    """Test that COMMANDS registry has expected structure."""
    from mcp_server_guide.commands import COMMANDS, CommandInfo

    # Verify COMMANDS is a dict
    assert isinstance(COMMANDS, dict)

    # Verify it's not empty
    assert len(COMMANDS) > 0

    # Verify all keys are strings
    assert all(isinstance(k, str) for k in COMMANDS.keys())

    # Verify all values are CommandInfo instances
    assert all(isinstance(v, CommandInfo) for v in COMMANDS.values())

    # Verify each CommandInfo has required fields
    for cmd_name, cmd_info in COMMANDS.items():
        assert cmd_info.name == cmd_name
        assert isinstance(cmd_info.description, str)
        assert isinstance(cmd_info.usage, str)
        assert isinstance(cmd_info.help_text, str)
        assert cmd_info.category in {"phase", "utility", "management"}
        assert isinstance(cmd_info.usage_pattern, str)
        assert isinstance(cmd_info.accepts_user_content, bool)
        assert isinstance(cmd_info.has_prompt_document, bool)


def test_command_sets():
    """Test that command category sets are correct."""
    from mcp_server_guide.commands import (
        ALL_COMMANDS,
        PHASE_COMMANDS,
        UTILITY_COMMANDS,
        MANAGEMENT_COMMANDS,
        COMMANDS_WITH_PROMPTS,
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


def test_get_command_info():
    """Test get_command_info helper function."""
    from mcp_server_guide.commands import get_command_info, CMD_DISCUSS

    # Valid command
    info = get_command_info(CMD_DISCUSS)
    assert info is not None
    assert info.name == CMD_DISCUSS

    # Invalid command
    info = get_command_info("nonexistent")
    assert info is None
