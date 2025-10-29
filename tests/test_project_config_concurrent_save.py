"""Tests for concurrent save operations and proper file locking."""

from unittest.mock import patch
from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig, Category


class TestConcurrentSave:
    """Test concurrent save operations use proper locking."""

    def test_save_config_uses_lock_update(self, tmp_path):
        """Test that save_config uses lock_update for proper file locking."""
        config_manager = ProjectConfigManager()
        config_manager.set_config_filename(tmp_path / "test_config.yaml")

        project_config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"], description="Test category")}
        )

        with patch("mcp_server_guide.project_config.lock_update") as mock_lock_update:
            # Mock lock_update to return a docroot value
            mock_lock_update.return_value = "."

            config_manager.save_config("test_project", project_config)

            # Verify lock_update was called
            assert mock_lock_update.called
            # Verify it was called with correct arguments
            call_args = mock_lock_update.call_args
            assert len(call_args[0]) >= 3  # config_file, function, project_name, config
            assert call_args[0][1].__name__ == "_save_config_locked"
