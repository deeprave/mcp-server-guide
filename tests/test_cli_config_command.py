"""Tests for CLI config command parsing."""

from src.mcp_server_guide.cli_parser_click import parse_command


def test_config_command_no_args():
    """Parse @guide config with no arguments."""
    result = parse_command(["config"])
    assert result.type == "config"
    assert result.data.get("project") is None
    assert result.data.get("list_projects") is False
    assert result.data.get("verbose") is False


def test_config_command_with_verbose():
    """Parse @guide config --verbose."""
    result = parse_command(["config", "--verbose"])
    assert result.type == "config"
    assert result.data.get("verbose") is True


def test_config_command_with_v_flag():
    """Parse @guide config -v."""
    result = parse_command(["config", "-v"])
    assert result.type == "config"
    assert result.data.get("verbose") is True


def test_config_command_with_projects():
    """Parse @guide config --projects."""
    result = parse_command(["config", "--projects"])
    assert result.type == "config"
    assert result.data.get("list_projects") is True


def test_config_command_with_project_name():
    """Parse @guide config myproject."""
    result = parse_command(["config", "myproject"])
    assert result.type == "config"
    assert result.data.get("project") == "myproject"


def test_config_command_projects_and_verbose():
    """Parse @guide config --projects --verbose."""
    result = parse_command(["config", "--projects", "--verbose"])
    assert result.type == "config"
    assert result.data.get("list_projects") is True
    assert result.data.get("verbose") is True


def test_config_command_project_and_verbose():
    """Parse @guide config myproject --verbose."""
    result = parse_command(["config", "myproject", "--verbose"])
    assert result.type == "config"
    assert result.data.get("project") == "myproject"
    assert result.data.get("verbose") is True
