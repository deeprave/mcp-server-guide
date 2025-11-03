"""Tests for main module functionality."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
import click.exceptions
from mcp_server_guide.main import main, validate_mode, start_mcp_server


async def test_validate_mode_stdio():
    """Test validate_mode with stdio mode."""
    mode_type, config = validate_mode("stdio")
    assert mode_type == "stdio"
    assert config == ""  # Returns empty string, not None


async def test_validate_mode_invalid():
    """Test validate_mode with invalid modes."""
    with pytest.raises(click.exceptions.BadParameter):
        validate_mode("invalid_mode")


async def test_start_mcp_server_stdio():
    """Test start_mcp_server with stdio mode."""
    from mcp_server_guide.server import reset_server_state
    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    # Test stdio mode with mocked server
    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock()
        mock_create.return_value = mock_server

        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result
        mock_server.run.assert_called_once()


async def test_start_mcp_server_stdio_keyboard_interrupt():
    """Test start_mcp_server stdio mode with KeyboardInterrupt."""
    from mcp_server_guide.server import reset_server_state
    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock(side_effect=KeyboardInterrupt())
        mock_create.return_value = mock_server
        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result


async def test_start_mcp_server_stdio_broken_pipe():
    """Test start_mcp_server stdio mode with BrokenPipeError."""
    from mcp_server_guide.server import reset_server_state
    reset_server_state()  # Reset global state

    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.create_server_with_config") as mock_create:
        mock_server = Mock()
        mock_server.run = Mock(side_effect=BrokenPipeError())
        mock_create.return_value = mock_server
        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result


async def test_main_cli_help():
    """Test main CLI help."""
    command = main()
    runner = CliRunner()

    result = runner.invoke(command, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


async def test_main_cli_invalid_option():
    """Test main CLI with invalid option."""
    command = main()
    runner = CliRunner()

    result = runner.invoke(command, ["--invalid-option"])
    assert result.exit_code != 0


async def test_main_cli_with_all_options():
    """Test main CLI with all options."""
    command = main()
    runner = CliRunner()

    with patch("mcp_server_guide.main.start_mcp_server") as mock_start:
        mock_start.return_value = "Started"
        result = runner.invoke(
            command,
            [
                "--docroot",
                "/custom",
                "--guidesdir",
                "guides/",
                "--guide",
                "custom_guide",
                "--langsdir",
                "langs/",
                "--lang",
                "python",
                "--contextdir",
                "projects/",
                "--context",
                "test_project",
                "--log-level",
                "INFO",
                "--log-file",
                "/tmp/test.log",
                "--log-console",
            ],
        )

        assert result.exit_code == 0
        mock_start.assert_called_once()
