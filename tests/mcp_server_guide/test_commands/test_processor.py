"""Tests for CommandProcessor."""

import pytest
from unittest.mock import AsyncMock, patch
from mcp_server_guide.commands.processor import CommandProcessor


class TestCommandProcessor:
    """Test CommandProcessor functionality."""

    @pytest.fixture
    def processor(self):
        """Create CommandProcessor instance."""
        return CommandProcessor()

    def test_init(self, processor):
        """Test CommandProcessor initialization."""
        assert processor.parser is not None
        assert processor.handler is not None

    @pytest.mark.asyncio
    async def test_process_message_no_command(self, processor):
        """Test processing message that's not a command."""
        with patch.object(processor.parser, "parse_command", return_value=None):
            result = await processor.process_message("regular message")
            assert result is None

    @pytest.mark.asyncio
    async def test_process_message_successful_command(self, processor):
        """Test processing valid command successfully."""
        mock_parsed = {"command": "guide", "args": ["lang"], "params": {"auto-load": "true"}}
        mock_result = {"success": True, "data": "test"}

        with patch.object(processor.parser, "parse_command", return_value=mock_parsed):
            with patch.object(processor.handler, "execute_command", new_callable=AsyncMock, return_value=mock_result):
                result = await processor.process_message("/guide lang auto-load=true")

                assert result == mock_result
                processor.handler.execute_command.assert_called_once_with("guide", ["lang"], {"auto-load": "true"})

    @pytest.mark.asyncio
    async def test_process_message_command_without_params(self, processor):
        """Test processing command without params key."""
        mock_parsed = {
            "command": "guide",
            "args": ["lang"],
            # No "params" key
        }
        mock_result = {"success": True, "data": "test"}

        with patch.object(processor.parser, "parse_command", return_value=mock_parsed):
            with patch.object(processor.handler, "execute_command", new_callable=AsyncMock, return_value=mock_result):
                result = await processor.process_message("/guide lang")

                assert result == mock_result
                processor.handler.execute_command.assert_called_once_with("guide", ["lang"], {})

    @pytest.mark.asyncio
    async def test_process_message_handler_exception(self, processor):
        """Test handling exception from command handler."""
        mock_parsed = {"command": "guide", "args": ["lang"], "params": {}}

        with patch.object(processor.parser, "parse_command", return_value=mock_parsed):
            with patch.object(
                processor.handler, "execute_command", new_callable=AsyncMock, side_effect=ValueError("Test error")
            ):
                result = await processor.process_message("/guide lang")

                assert result == {"success": False, "error": "Command processing error: Test error"}

    def test_get_help(self, processor):
        """Test get_help method returns proper help structure."""
        result = processor.get_help()

        assert result["success"] is True
        assert "help" in result
        assert "commands" in result["help"]
        assert "parameters" in result["help"]
        assert "examples" in result["help"]

        # Check specific commands are present
        commands = result["help"]["commands"]
        assert "/guide" in commands
        assert "/guide <category>" in commands
        assert "/<category>" in commands
        assert "/guide-new <name> [params]" in commands
        assert "/guide-edit <name> [params]" in commands
        assert "/guide-del <name>" in commands

        # Check parameters are present
        parameters = result["help"]["parameters"]
        assert "dir=<path>" in parameters
        assert "patterns=<pattern>[,<pattern>]" in parameters
        assert "auto-load=true|false" in parameters

        # Check examples are present
        examples = result["help"]["examples"]
        assert "/guide" in examples
        assert "/guide lang" in examples
        assert "/lang" in examples
        assert any("guide-new" in ex for ex in examples)
        assert any("guide-edit" in ex for ex in examples)
        assert any("guide-del" in ex for ex in examples)
