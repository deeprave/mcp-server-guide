"""Integration tests for mcpguide CLI and configuration."""

import os
import tempfile
from pathlib import Path
from click.testing import CliRunner

from mcpguide.main import main
from mcpguide.config import Config


def test_complete_workflow_with_defaults():
    """Test complete workflow using default values."""
    runner = CliRunner()
    command = main()

    result = runner.invoke(command, [])
    assert result.exit_code == 0
    assert "Starting MCP server with config:" in result.output
    assert "'docroot': '.'" in result.output
    assert "'guidesdir': 'guide/'" in result.output


def test_complete_workflow_with_cli_args():
    """Test complete workflow with CLI arguments."""
    runner = CliRunner()
    command = main()

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
    assert "'/custom/root'" in result.output
    assert "'custom_guide/'" in result.output
    assert "'custom_guidelines'" in result.output
    assert "'custom_lang/'" in result.output  # This is langdir
    assert "'rust'" in result.output  # This is language
    assert "'test_project'" in result.output


def test_environment_variable_precedence():
    """Test that environment variables override defaults but CLI args override env vars."""
    runner = CliRunner()
    command = main()

    # Set environment variables
    env_vars = {
        "MCP_DOCROOT": "/env/root",
        "MCP_GUIDEDIR": "/env/guide",
        "MCP_GUIDE": "env_guidelines",
        "MCP_LANGDIR": "/env/lang",
        "MCP_LANGUAGE": "python",
        "MCP_PROJDIR": "/env/project",
        "MCP_PROJECT": "env_project",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    try:
        # Test env vars are used when no CLI args
        result = runner.invoke(command, [])
        assert result.exit_code == 0
        assert "'/env/root'" in result.output
        assert "'env_guidelines'" in result.output

        # Test CLI args override env vars
        result = runner.invoke(command, ["--docroot", "/cli/root", "--guide", "cli_guidelines"])
        assert result.exit_code == 0
        assert "'/cli/root'" in result.output
        assert "'cli_guidelines'" in result.output
        # Env vars should still be used for non-overridden options
        assert "'python'" in result.output

    finally:
        # Clean up
        for key in env_vars:
            if key in os.environ:
                del os.environ[key]


def test_path_resolution_scenarios():
    """Test path resolution in different scenarios."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directories and files
        guide_dir = temp_path / "guide"
        guide_dir.mkdir()
        guide_file = guide_dir / "guidelines.md"
        guide_file.write_text("# Guidelines")

        lang_dir = temp_path / "lang"
        lang_dir.mkdir()
        lang_file = lang_dir / "python.md"
        lang_file.write_text("# Python")

        # Test absolute paths
        abs_guide = resolve_path(str(guide_file), str(temp_path), is_file=True)
        assert abs_guide == str(guide_file)

        # Test relative paths with docroot
        rel_guide = resolve_path("guide/guidelines", str(temp_path), is_file=True)
        assert rel_guide == str(temp_path / "guide" / "guidelines.md")

        # Test directory paths
        dir_path = resolve_path("guide/", str(temp_path), is_file=False)
        assert dir_path == str(temp_path / "guide") + "/"

        # Test validation with existing files
        config_values = {
            "docroot": str(temp_path),
            "guidesdir": str(guide_dir),
            "guide": str(guide_file),
            "langdir": str(lang_dir),
            "language": str(lang_file),
        }

        assert validate_config(config_values) is True


def test_configuration_resolution_integration():
    """Test complete configuration resolution process."""
    config = Config()

    # Test with no environment variables - should use defaults
    resolved = resolve_env_vars(config)
    assert resolved["docroot"] == "."
    assert resolved["guidesdir"] == "guide/"
    assert resolved["guide"] == "guidelines"
    assert resolved["project"] == "mcpguide"  # Current directory name

    # Test with environment variables
    os.environ["MCP_DOCROOT"] = "/test/root"
    os.environ["MCP_GUIDE"] = "test_guide"

    try:
        resolved = resolve_env_vars(config)
        assert resolved["docroot"] == "/test/root"
        assert resolved["guide"] == "test_guide"
        # Others should still be defaults
        assert resolved["guidesdir"] == "guide/"

    finally:
        # Clean up
        if "MCP_DOCROOT" in os.environ:
            del os.environ["MCP_DOCROOT"]
        if "MCP_GUIDE" in os.environ:
            del os.environ["MCP_GUIDE"]


def test_error_handling_invalid_paths():
    """Test error handling with invalid paths."""
    # Test validation with non-existent paths
    invalid_config = {
        "docroot": "/nonexistent/path",
        "guidesdir": "/nonexistent/guide/",
        "guide": "/nonexistent/guide.md",
    }

    assert validate_config(invalid_config) is False

    # Test with wrong file/directory types
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"
        test_file.write_text("test")

        # File where directory expected
        wrong_type_config = {
            "docroot": str(temp_path),
            "guidesdir": str(test_file),  # File, but should be directory
        }

        assert validate_config(wrong_type_config) is False
