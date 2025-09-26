"""Tests for configuration module."""

from unittest.mock import patch
from mcp_server_guide.config import Config, ConfigOption


def test_config_option_creation():
    """Test ConfigOption dataclass creation."""
    option = ConfigOption(
        name="docroot",
        cli_short="-d",
        cli_long="--docroot",
        env_var="MCP_DOCROOT",
        default=".",
        description="Document root directory",
    )

    assert option.name == "docroot"
    assert option.cli_short == "-d"
    assert option.cli_long == "--docroot"
    assert option.env_var == "MCP_DOCROOT"
    assert option.default == "."
    assert option.description == "Document root directory"


def test_config_class_has_all_options():
    """Test Config class contains all required options."""
    config = Config()

    # Check that all expected options exist
    expected_options = ["docroot", "guidesdir", "guide", "langsdir", "lang", "contextdir", "context"]

    for option_name in expected_options:
        assert hasattr(config, option_name)
        option = getattr(config, option_name)
        assert hasattr(option, "cli_long")
        assert hasattr(option, "env_var")


def test_config_has_logging_options():
    """Test Config class has logging options."""
    config = Config()

    # Should have logging configuration options
    assert hasattr(config, "log_level")
    assert hasattr(config, "log_file")
    assert hasattr(config, "log_console")

    # Check default values
    assert config.log_level.default == "OFF"
    assert config.log_file.default == ""
    assert config.log_console.default() == "true"


def test_resolve_path():
    """Test path resolution logic."""
    config = Config()

    # Test absolute paths
    abs_path = "/absolute/path"
    resolved = config.resolve_path(abs_path, "/base")
    assert resolved == abs_path

    # Test relative paths
    rel_path = "relative/path"
    resolved = config.resolve_path(rel_path, "/base")
    assert resolved == "/base/relative/path"


def test_config_resolve_path_edge_cases():
    """Test Config.resolve_path edge cases."""
    config = Config()

    # Test with empty string
    result = config.resolve_path("", "/base")
    assert result.startswith("/base")

    # Test with directory path
    result = config.resolve_path("dir/", "/base")
    assert result.endswith("/")

    # Test absolute path
    result = config.resolve_path("/absolute/path", "/base")
    assert result == "/absolute/path"


def test_config_basic_functionality():
    """Test basic Config functionality."""
    config = Config()

    # Test that config has expected attributes
    assert hasattr(config, "docroot")
    assert hasattr(config, "context")
    assert hasattr(config, "resolve_path")

    # Test resolve_path works
    result = config.resolve_path("test", "/base")
    assert isinstance(result, str)


def test_config_all_options_have_required_attributes():
    """Test that all config options have required attributes."""
    config = Config()

    # Get all option attributes
    option_names = [
        attr for attr in dir(config) if not attr.startswith("_") and hasattr(getattr(config, attr), "cli_long")
    ]

    for option_name in option_names:
        option = getattr(config, option_name)

        # Each option should have these attributes
        assert hasattr(option, "name")
        assert hasattr(option, "cli_short")
        assert hasattr(option, "cli_long")
        assert hasattr(option, "env_var")
        assert hasattr(option, "default")
        assert hasattr(option, "description")

        # Verify types
        assert isinstance(option.name, str)
        assert isinstance(option.cli_short, str)
        assert isinstance(option.cli_long, str)
        assert isinstance(option.env_var, str)
        assert isinstance(option.description, str)


def test_config_add_md_extension():
    """Test Config.add_md_extension method."""
    config = Config()

    # Test adding extension to path without extension
    result = config.add_md_extension("test")
    assert result == "test.md"

    # Test path that already has extension
    result = config.add_md_extension("test.txt")
    assert result == "test.txt"

    # Test path with .md extension
    result = config.add_md_extension("test.md")
    assert result == "test.md"


def test_config_validate_path():
    """Test Config.validate_path method."""
    config = Config()

    # Test with must_exist=False
    result = config.validate_path("/nonexistent/path", must_exist=False)
    assert result is True

    # Test existing file validation
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            result = config.validate_path("/test/file.txt", must_be_file=True)
            assert result is True

    # Test existing directory validation
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=True):
            result = config.validate_path("/test/dir", must_be_dir=True)
            assert result is True

    # Test non-existent path
    with patch("os.path.exists", return_value=False):
        result = config.validate_path("/nonexistent", must_exist=True)
        assert result is False

    # Test file validation failure
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=False):
            result = config.validate_path("/test/dir", must_be_file=True)
            assert result is False

    # Test directory validation failure
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=False):
            result = config.validate_path("/test/file.txt", must_be_dir=True)
            assert result is False
