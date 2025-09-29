"""Tests for main module functionality."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
import click.exceptions
from mcp_server_guide.main import main, validate_mode, start_mcp_server


def test_validate_mode_stdio():
    """Test validate_mode with stdio mode."""
    mode_type, config = validate_mode("stdio")
    assert mode_type == "stdio"
    assert config == ""  # Returns empty string, not None


def test_validate_mode_sse_valid():
    """Test validate_mode with valid SSE URLs."""
    # Test HTTP URL
    mode_type, config = validate_mode("sse=http://localhost:8080/sse")
    assert mode_type == "sse"
    assert config == "http://localhost:8080/sse"

    # Test HTTPS URL
    mode_type, config = validate_mode("sse=https://example.com:9000/mcp")
    assert mode_type == "sse"
    assert config == "https://example.com:9000/mcp"


def test_validate_mode_invalid():
    """Test validate_mode with invalid modes."""
    with pytest.raises(click.exceptions.BadParameter):
        validate_mode("invalid_mode")


def test_validate_mode_sse_empty_url():
    """Test validate_mode with empty SSE URL."""
    with pytest.raises(click.exceptions.BadParameter):
        validate_mode("sse=")


def test_validate_mode_sse_invalid_url():
    """Test validate_mode with invalid SSE URL."""
    with pytest.raises(click.exceptions.BadParameter):
        validate_mode("sse=not-a-url")


def test_start_mcp_server_stdio():
    """Test start_mcp_server with stdio mode."""
    config = {"docroot": ".", "project": "test"}

    # Test stdio mode with mocked server
    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock()
        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result
        mock_mcp.run.assert_called_once()


def test_start_mcp_server_stdio_keyboard_interrupt():
    """Test start_mcp_server stdio mode with KeyboardInterrupt."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=KeyboardInterrupt())
        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result


def test_start_mcp_server_stdio_broken_pipe():
    """Test start_mcp_server stdio mode with BrokenPipeError."""
    config = {"docroot": ".", "project": "test"}

    with patch("mcp_server_guide.server.mcp") as mock_mcp:
        mock_mcp.run = Mock(side_effect=BrokenPipeError())
        result = start_mcp_server("stdio", config)
        assert "stdio mode" in result


def test_start_mcp_server_sse():
    """Test start_mcp_server with SSE mode."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("uvicorn.run") as mock_uvicorn:
        result = start_mcp_server("sse", config)
        assert "sse mode" in result
        mock_uvicorn.assert_called_once()

        # Check uvicorn call arguments
        call_args = mock_uvicorn.call_args
        assert call_args[1]["host"] == "localhost"
        assert call_args[1]["port"] == 8080


def test_start_mcp_server_sse_keyboard_interrupt():
    """Test start_mcp_server SSE mode with KeyboardInterrupt."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("uvicorn.run") as mock_uvicorn:
        mock_uvicorn.side_effect = KeyboardInterrupt()
        result = start_mcp_server("sse", config)
        assert "sse mode" in result


def test_start_mcp_server_sse_import_error():
    """Test start_mcp_server SSE mode with uvicorn import error."""
    config = {"docroot": ".", "project": "test", "mode_config": "http://localhost:8080/sse"}

    with patch("uvicorn.run", side_effect=ImportError("uvicorn not found")):
        with pytest.raises(ImportError):
            start_mcp_server("sse", config)


def test_main_cli_help():
    """Test main CLI help."""
    command = main()
    runner = CliRunner()

    result = runner.invoke(command, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_main_cli_invalid_option():
    """Test main CLI with invalid option."""
    command = main()
    runner = CliRunner()

    result = runner.invoke(command, ["--invalid-option"])
    assert result.exit_code != 0


def test_main_cli_with_all_options():
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


def test_main_cli_sse_mode():
    """Test main CLI with SSE mode."""
    command = main()
    runner = CliRunner()

    with patch("mcp_server_guide.main.start_mcp_server") as mock_start:
        mock_start.return_value = "Started SSE"
        result = runner.invoke(command, ["sse=http://localhost:8080/sse"])

        assert result.exit_code == 0
        mock_start.assert_called_once()

        # Check that SSE mode was passed correctly
        call_args = mock_start.call_args
        assert call_args[0][0] == "sse"  # mode
        assert call_args[0][1]["mode_config"] == "http://localhost:8080/sse"
