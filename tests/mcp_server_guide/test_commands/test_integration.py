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

    # Test simple command
    parsed = parser.parse_command("guide lang")
    assert parsed is not None
    assert parsed["command"] == "guide"
    assert parsed["args"] == ["lang"]

    # Test handler can accept this format
    result = await handler.execute_command(parsed["command"], parsed["args"], parsed.get("params", {}))

    assert "success" in result


def test_error_handling_invalid_syntax():
    """Test error handling for invalid command syntax."""
    parser = CommandParser()

    # Test various invalid inputs
    assert parser.parse_command("") is None
    assert parser.parse_command("   ") is None
    assert parser.parse_command("please guide me") is None  # Natural language

    # Valid commands should still work
    result = parser.parse_command("guide")
    assert result is not None


@pytest.mark.asyncio
async def test_error_handling_missing_params():
    """Test error handling for missing required parameters."""
    handler = CommandHandler()

    # Test category add without required parameters
    result = await handler.execute_command("category", ["add"], {})

    assert result["success"] is False
    assert "Usage:" in result["error"]


def test_command_help_structure():
    """Test that commands return consistent help structure."""
    parser = CommandParser()

    # Test that all valid commands parse to consistent structure
    commands = ["guide", "guide lang"]
    expected_outputs = [
        {"command": "guide", "args": [], "params": {}},
        {"command": "guide", "args": ["lang"], "params": {}},
    ]

    for cmd, expected in zip(commands, expected_outputs):
        result = parser.parse_command(cmd)
        assert result is not None, f"Parser returned None for command: {cmd}"
        assert result.get("command") == expected["command"], (
            f"Command mismatch for '{cmd}': {result.get('command')} != {expected['command']}"
        )
        assert result.get("args") == expected["args"], (
            f"Args mismatch for '{cmd}': {result.get('args')} != {expected['args']}"
        )
        assert result.get("params") == expected["params"], (
            f"Params mismatch for '{cmd}': {result.get('params')} != {expected['params']}"
        )
