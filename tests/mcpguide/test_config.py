"""Tests for configuration module."""

from mcpguide.config import Config, ConfigOption


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
    expected_options = ["docroot", "guidesdir", "guide", "langsdir", "lang", "projdir", "project"]

    for option_name in expected_options:
        assert hasattr(config, option_name)
        option = getattr(config, option_name)
        assert hasattr(option, "cli_long")
        assert hasattr(option, "env_var")


def test_config_has_logging_options():
    """Test Config class has logging options."""
    config = Config()

    # Should have logging configuration options
    assert hasattr(config, 'log_level')
    assert hasattr(config, 'log_file')
    assert hasattr(config, 'log_console')

    # Check default values
    assert config.log_level.default == "OFF"
    assert config.log_file.default == ""
    assert config.log_console.default is True


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
