"""Tests for config_tools.py error handling scenarios."""


class TestConfigToolsErrorHandling:
    """Test error handling paths in config_tools.py."""

    # Note: Validation error tests removed as validation is now handled by Pydantic models
    # Note: Auto-save exception test removed - set_project_config no longer calls save_session
