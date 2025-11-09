"""Integration tests for mcp-server-guide CLI and configuration."""

from unittest.mock import patch, Mock
from click.testing import CliRunner

from mcp_server_guide.main import main
from mcp_server_guide.config import Config


def test_complete_workflow_with_defaults():
    """Test complete workflow using default values."""
    import asyncio

    # Mock the ContextVar to avoid the dict.set() error
    with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
        mock_contextvar.set = Mock()
        mock_contextvar.get = Mock(return_value={})

        runner = CliRunner()

        async def get_command():
            return await main()

        command = asyncio.run(get_command())

        async def mock_start_server(mode, config):
            return "Started"

        with patch("mcp_server_guide.main.start_mcp_server", side_effect=mock_start_server):
            result = runner.invoke(command, [])

        assert result.exit_code == 0


def test_complete_workflow_with_cli_args():
    """Test complete workflow with CLI arguments."""
    import asyncio

    # Mock the ContextVar to avoid the dict.set() error
    with patch("mcp_server_guide.main._deferred_builtin_config") as mock_contextvar:
        mock_contextvar.set = Mock()
        mock_contextvar.get = Mock(return_value={})

        runner = CliRunner()

        async def get_command():
            return await main()

        command = asyncio.run(get_command())

        async def mock_start_server(mode, config):
            return "Started"

        with patch("mcp_server_guide.main.start_mcp_server", side_effect=mock_start_server):
            result = runner.invoke(
                command,
                [
                    "--docroot",
                    "/custom/root",
                ],
            )

        assert result.exit_code == 0


async def test_config_class_basic():
    """Test basic Config class functionality."""
    config = Config()

    # Should have basic attributes
    assert hasattr(config, "docroot")
    assert hasattr(config, "resolve_path")

    # Test resolve_path method
    abs_path = "/absolute/path"
    resolved = config.resolve_path(abs_path, "/base")
    assert resolved == abs_path
