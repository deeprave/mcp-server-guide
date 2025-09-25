"""Integration tests for mcpguide CLI and configuration."""

import os
from click.testing import CliRunner

from mcpguide.main import main
from mcpguide.config import Config


def test_complete_workflow_with_defaults():
    """Test complete workflow using default values."""
    runner = CliRunner()
    command = main()

    # Mock the server startup to avoid hanging
    import pytest
    with pytest.MonkeyPatch().context() as m:
        m.setattr("mcpguide.main.start_mcp_server", lambda mode, config: "Started")
        result = runner.invoke(command, [])

    assert result.exit_code == 0


def test_complete_workflow_with_cli_args():
    """Test complete workflow with CLI arguments."""
    runner = CliRunner()
    command = main()

    import pytest
    with pytest.MonkeyPatch().context() as m:
        m.setattr("mcpguide.main.start_mcp_server", lambda mode, config: "Started")
        result = runner.invoke(
            command,
            [
                "--docroot",
                "/custom/root",
                "--guidesdir",
                "custom_guide/",
                "--guide",
                "custom_guidelines",
                "--langsdir",
                "custom_lang/",
                "--lang",
                "rust",
                "--projdir",
                "custom_project/",
                "--project",
                "test_project",
            ],
        )

    assert result.exit_code == 0


def test_config_class_basic():
    """Test basic Config class functionality."""
    config = Config()
    
    # Should have basic attributes
    assert hasattr(config, 'docroot')
    assert hasattr(config, 'project')
    assert hasattr(config, 'resolve_path')
    
    # Test resolve_path method
    abs_path = "/absolute/path"
    resolved = config.resolve_path(abs_path, "/base")
    assert resolved == abs_path
