"""Test commands module initialization."""


def test_commands_init_imports():
    """Test that commands module imports work correctly."""
    from mcp_server_guide.commands import CommandParser, CommandHandler, CommandProcessor

    assert CommandParser is not None
    assert CommandHandler is not None
    assert CommandProcessor is not None
