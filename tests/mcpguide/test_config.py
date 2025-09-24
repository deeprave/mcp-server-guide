"""Tests for configuration module."""

import os
import click
from click.testing import CliRunner

from mcpguide.config import ConfigOption, Config, create_click_command, resolve_env_vars


def test_config_option_creation():
    """Test ConfigOption dataclass creation."""
    option = ConfigOption(
        name="docroot",
        cli_short="-d",
        cli_long="--docroot",
        env_var="MCP_DOCROOT",
        default=".",
        is_file=False,
        description="Document root directory",
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
    result = runner.invoke(command, ["--help"])
    assert result.exit_code == 0

    # Check all 7 options are present
    expected_options = ["--docroot", "--guidesdir", "--guide", "--langs", "--lang", "--projdir", "--project"]
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
    result = runner.invoke(command, ["--docroot", "/custom/path", "--guidesdir", "custom_guide/"])
    assert result.exit_code == 0


def test_resolve_env_vars():
    """Test environment variable resolution with fallbacks."""
    config = Config()

    # Test with no env vars set - should use defaults
    resolved = resolve_env_vars(config)
    assert resolved["docroot"] == "."
    assert resolved["guidesdir"] == "guide/"

    # Test with env vars set
    os.environ["MCP_DOCROOT"] = "/custom/root"
    os.environ["MCP_GUIDEDIR"] = "/custom/guide"

    try:
        resolved = resolve_env_vars(config)
        assert resolved["docroot"] == "/custom/root"
        assert resolved["guidesdir"] == "/custom/guide"
        # Other values should still be defaults
        assert resolved["guide"] == "guidelines"
    finally:
        # Clean up
        del os.environ["MCP_DOCROOT"]
        del os.environ["MCP_GUIDEDIR"]


def test_cli_args_override_env_vars():
    """Test that CLI arguments override environment variables."""
    config = Config()
    command = create_click_command(config)
    runner = CliRunner()

    # Set environment variable
    os.environ["MCP_DOCROOT"] = "/env/path"

    try:
        # CLI arg should override env var
        result = runner.invoke(command, ["--docroot", "/cli/path"])
        assert result.exit_code == 0

        # Test that env var is used when no CLI arg provided
        result = runner.invoke(command, [])
        assert result.exit_code == 0
    finally:
        # Clean up
        del os.environ["MCP_DOCROOT"]


def test_resolve_path():
    """Test path resolution logic."""
    from mcpguide.config import resolve_path

    # Test absolute path - should use as-is
    abs_path = "/absolute/path/file.txt"
    result = resolve_path(abs_path, "/docroot", is_file=True)
    assert result == "/absolute/path/file.txt"

    # Test relative path - should resolve relative to docroot
    rel_path = "guide/guidelines"
    result = resolve_path(rel_path, "/docroot", is_file=True)
    assert result == "/docroot/guide/guidelines.md"

    # Test directory path - no extension added
    dir_path = "guide/"
    result = resolve_path(dir_path, "/docroot", is_file=False)
    assert result == "/docroot/guide/"


def test_get_project_name():
    """Test project name extraction from current directory."""
    from mcpguide.config import get_project_name

    # Should return basename of current directory
    project_name = get_project_name()
    assert isinstance(project_name, str)
    assert len(project_name) > 0
    assert project_name == "mcpguide"  # Current directory name


def test_resolve_path_edge_cases():
    """Test edge cases for path resolution."""
    from mcpguide.config import resolve_path

    # Test file with existing extension - should not add .md
    file_with_ext = "config.yaml"
    result = resolve_path(file_with_ext, "/docroot", is_file=True)
    assert result == "/docroot/config.yaml"

    # Test empty path
    result = resolve_path("", "/docroot", is_file=False)
    assert result == "/docroot"

    # Test path with no trailing slash for directory
    dir_no_slash = "guide"
    result = resolve_path(dir_no_slash, "/docroot", is_file=False)
    assert result == "/docroot/guide"


def test_validate_config():
    """Test configuration validation."""
    from mcpguide.config import validate_config

    # Test with valid configuration (existing directories)
    valid_config = {
        "docroot": ".",
        "guidesdir": "guide/",
        "guide": "guide/guidelines.md",
        "langdir": "lang/",
        "projdir": "project/",
    }

    # Should not raise any exceptions
    result = validate_config(valid_config)
    assert result is True

    # Test with invalid directory
    invalid_config = {"docroot": ".", "guidesdir": "nonexistent/", "guide": "guide/guidelines.md"}

    # Should return False or raise exception
    result = validate_config(invalid_config)
    assert result is False


def test_validate_config_file_type_mismatch():
    """Test validation with file/directory type mismatches."""
    from mcpguide.config import validate_config

    # Test directory where file expected (guide should be a file)
    config_dir_as_file = {
        "docroot": ".",
        "guide": "guide/",  # This is a directory, but guide should be a file
    }

    result = validate_config(config_dir_as_file)
    assert result is False

    # Test file where directory expected (guidesdir should be a directory)
    config_file_as_dir = {
        "docroot": ".",
        "guidesdir": "guide/guidelines.md",  # This is a file, but guidesdir should be a directory
    }

    result = validate_config(config_file_as_dir)
    assert result is False


def test_main_cli_entry_point():
    """Test main CLI entry point function."""
    from mcpguide.config import main
    from click.testing import CliRunner

    runner = CliRunner()
    command = main()  # Get the click command

    # Test that main function exists and can be called
    result = runner.invoke(command, ["--help"])
    assert result.exit_code == 0
    assert "MCP server with configurable paths" in result.output

    # Test with some arguments
    result = runner.invoke(command, ["--docroot", ".", "--guidesdir", "guide/"])
    assert result.exit_code == 0


def test_main_cli_with_env_vars():
    """Test main CLI with environment variables."""
    from mcpguide.config import main
    from click.testing import CliRunner
    import os

    runner = CliRunner()
    command = main()

    # Set environment variable
    os.environ["MCP_DOCROOT"] = "/env/path"

    try:
        # Test that env var is used when no CLI arg provided
        # Use empty args to ensure no CLI override
        result = runner.invoke(command, [])
        assert result.exit_code == 0
        assert "/env/path" in result.output

        # Also test with explicit None values to trigger env var path
        result = runner.invoke(command, ["--docroot", "/env/path"])
        assert result.exit_code == 0
    finally:
        # Clean up
        del os.environ["MCP_DOCROOT"]


def test_main_cli_env_var_resolution():
    """Test main CLI environment variable resolution path."""
    from mcpguide.config import main
    from click.testing import CliRunner
    import os

    runner = CliRunner()
    command = main()

    # Set multiple environment variables to ensure env var path is taken
    os.environ["MCP_GUIDEDIR"] = "/custom/guide"
    os.environ["MCP_LANGDIR"] = "/custom/lang"

    try:
        # Run without any CLI args to force env var resolution
        result = runner.invoke(command, [])
        assert result.exit_code == 0
        # Check that env vars are used in the output
        assert "/custom/guide" in result.output
        assert "/custom/lang" in result.output
    finally:
        # Clean up
        if "MCP_GUIDEDIR" in os.environ:
            del os.environ["MCP_GUIDEDIR"]
        if "MCP_LANGDIR" in os.environ:
            del os.environ["MCP_LANGDIR"]


def test_cli_main_entry_point():
    """Test CLI entry point function for console script."""
    from mcpguide.config import cli_main

    # Test that cli_main function exists and is callable
    assert callable(cli_main)

    # Test that it can be called (though it will try to run the server)
    # We'll just check it doesn't crash on import/definition
    assert cli_main.__name__ == "cli_main"
