"""Integration tests for command system."""

import pytest
from mcp_server_guide.commands.parser import CommandParser
from mcp_server_guide.commands.handler import CommandHandler


@pytest.mark.asyncio
async def test_full_command_pipeline():
    """Test complete command parsing and execution pipeline."""
    parser = CommandParser()
    handler = CommandHandler()

    # Test /guide command
    parsed = parser.parse_command("guide")
    assert parsed is not None

    # Mock the execution (would need actual integration in real scenario)
    # This tests the interface compatibility
    result = await handler.execute_command(parsed["command"], parsed["args"], parsed.get("params", {}))

    # Should return proper structure
    assert "success" in result


@pytest.mark.asyncio
async def test_parameter_parsing_integration():
    """Test parameter parsing integration with handler."""
    parser = CommandParser()
    handler = CommandHandler()

    # Test complex command with parameters
    parsed = parser.parse_command("guide:new typescript dir=lang/ts patterns=*.ts,*.tsx auto-load=true")
    assert parsed is not None
    assert parsed["command"] == "guide"
    assert parsed["subcommand"] == "new"
    assert parsed["args"] == ["typescript"]
    assert parsed["params"]["dir"] == "lang/ts"
    assert parsed["params"]["patterns"] == ["*.ts", "*.tsx"]
    assert parsed["params"]["auto-load"] is True

    # Test handler can accept this format
    result = await handler.execute_command(parsed["command"], parsed["args"], parsed["params"])

    assert "success" in result


def test_error_handling_invalid_syntax():
    """Test error handling for invalid command syntax."""
    parser = CommandParser()

    # Test various invalid inputs
    assert parser.parse_command("") is None
    assert parser.parse_command("   ") is None
    assert parser.parse_command("guide me through this") is None  # Natural language
    assert parser.parse_command("please guide me") is None  # Natural language

    # Valid commands should still work
    result = parser.parse_command("guide")
    assert result is not None


@pytest.mark.asyncio
async def test_error_handling_missing_params():
    """Test error handling for missing required parameters."""
    handler = CommandHandler()

    # Test guide-new without category name
    result = await handler.execute_command("guide-new", [], {})

    assert result["success"] is False
    assert "required" in result["error"].lower()


def test_command_help_structure():
    """Test that commands return consistent help structure."""
    parser = CommandParser()

    # Test that all valid commands parse to consistent structure
    commands = ["guide", "guide lang", "g:lang", "guide:new test", "guide:edit test dir=new", "guide:del test"]
    expected_outputs = [
        {"command": "guide", "subcommand": None, "args": [], "params": {}},
        {"command": "guide", "subcommand": None, "args": ["lang"], "params": {}},
        {"command": "g", "subcommand": "lang", "args": [], "params": {}},
        {"command": "guide", "subcommand": "new", "args": ["test"], "params": {}},
        {"command": "guide", "subcommand": "edit", "args": ["test"], "params": {"dir": "new"}},
        {"command": "guide", "subcommand": "del", "args": ["test"], "params": {}},
    ]

    for cmd, expected in zip(commands, expected_outputs):
        result = parser.parse_command(cmd)
        assert result is not None, f"Parser returned None for command: {cmd}"
        assert result.get("command") == expected["command"], (
            f"Command mismatch for '{cmd}': {result.get('command')} != {expected['command']}"
        )
        assert result.get("subcommand") == expected["subcommand"], (
            f"Subcommand mismatch for '{cmd}': {result.get('subcommand')} != {expected['subcommand']}"
        )
        assert result.get("args") == expected["args"], (
            f"Args mismatch for '{cmd}': {result.get('args')} != {expected['args']}"
        )
        assert result.get("params") == expected["params"], (
            f"Params mismatch for '{cmd}': {result.get('params')} != {expected['params']}"
        )
