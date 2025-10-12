"""Test for config_filename function removal."""


async def test_config_filename_function_removed():
    """Test that config_filename function is removed from naming module."""
    from mcp_server_guide import naming

    # Should not have config_filename function
    assert not hasattr(naming, "config_filename")


async def test_config_tools_uses_direct_filename():
    """Test that ProjectConfigManager uses direct filename from get_config_filename method."""
    from mcp_server_guide.naming import mcp_name
    from mcp_server_guide.project_config import ProjectConfigManager

    # ProjectConfigManager should have get_config_filename method
    manager = ProjectConfigManager()
    filename = manager.get_config_filename()

    # Should use direct filename with mcp_name, not a config_filename() function
    assert mcp_name() in str(filename)
    assert str(filename).endswith("config.yaml")


async def test_no_global_config_cli_flags():
    """Test that global config CLI flags are removed."""
    from mcp_server_guide.config import Config

    config = Config()

    # Should not have global_config option
    assert not hasattr(config, "global_config")

    # Should not have get_global_config_path method
    assert not hasattr(config, "get_global_config_path")
