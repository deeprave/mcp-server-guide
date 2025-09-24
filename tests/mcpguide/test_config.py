"""Tests for configuration module."""

import click
from click.testing import CliRunner

from mcpguide.config import ConfigOption, Config, create_click_command


def test_config_option_creation():
    """Test ConfigOption dataclass creation."""
    option = ConfigOption(
        name="docroot",
        cli_short="-d",
        cli_long="--docroot",
        env_var="MCP_DOCROOT",
        default=".",
        is_file=False,
        description="Document root directory"
    )

    assert option.name == "docroot"
    assert option.cli_short == "-d"
    assert option.cli_long == "--docroot"
    assert option.env_var == "MCP_DOCROOT"
    assert option.default == "."
    assert option.is_file is False
    assert option.description == "Document root directory"


def test_config_class_has_all_options():
    """Test Config class contains all required options."""
    config = Config()

    # Check that all expected options exist
    expected_options = ["docroot", "guidesdir", "guide", "langdir", "language", "projdir", "project"]

    for option_name in expected_options:
        assert hasattr(config, option_name)
        option = getattr(config, option_name)
        assert isinstance(option, ConfigOption)
        assert option.name == option_name


def test_create_click_command():
    """Test creating click command from config."""
    config = Config()
    command = create_click_command(config)

    # Test that it's a click command
    assert isinstance(command, click.Command)

    # Test that it has all expected options
    runner = CliRunner()
    result = runner.invoke(command, ['--help'])
    assert result.exit_code == 0

    # Check all 7 options are present
    expected_options = ['--docroot', '--guidesdir', '--guide', '--langs', '--lang', '--projdir', '--project']
    for option in expected_options:
        assert option in result.output


def test_click_command_option_parsing():
    """Test that click command parses options correctly."""
    config = Config()
    command = create_click_command(config)

    runner = CliRunner()

    # Test with default values
    result = runner.invoke(command, [])
    assert result.exit_code == 0

    # Test with custom values
    result = runner.invoke(command, ['--docroot', '/custom/path', '--guidesdir', 'custom_guide/'])
    assert result.exit_code == 0
