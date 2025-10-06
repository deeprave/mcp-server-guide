"""Integration tests for category auto-save functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.mcp_server_guide.tools.category_tools import update_category
from src.mcp_server_guide.session_tools import SessionManager


async def test_auto_save_actually_writes_to_file(monkeypatch):
    """Test that auto-save actually writes changes to the config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "test-config.json"

        # Mock ClientPath to use temp directory
        from mcp_server_guide.client_path import ClientPath

        monkeypatch.setattr(ClientPath, "_initialized", True)
        monkeypatch.setattr(ClientPath, "_primary_root", temp_path)

        # Create initial config file
        initial_config = {
            "projects": {
                "test-project": {
                    "categories": {
                        "custom_test": {"dir": "test/", "patterns": ["*.md"], "description": "Original description"}
                    }
                }
            }
        }
        config_file.write_text(json.dumps(initial_config, indent=2))

        # Create .current file to set the project
        current_file = temp_path / ".mcp-server-guide.current"
        current_file.write_text("test-project")

        # Mock SessionManager to use our test config file
        with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
            session_instance = SessionManager()
            mock_session_class.return_value = session_instance

            # Set up the session to use our test project and config
            session_instance.set_directory(str(temp_path))
            session_instance.session_state.projects["test-project"] = {
                "categories": {
                    "custom_test": {"dir": "test/", "patterns": ["*.md"], "description": "Original description"}
                }
            }

            # Override save_to_file to use our test config file
            original_save = session_instance.save_to_file

            async def mock_save(filename=None):
                # Ensure directory exists
                config_file.parent.mkdir(parents=True, exist_ok=True)
                return await original_save(str(config_file))

            session_instance.save_to_file = mock_save

            # Update category - this should trigger auto-save
            result = await update_category(
                "custom_test", "test/", ["*.md"], description="Updated description via auto-save"
            )

            assert result["success"] is True

            # Check that the file was actually updated
            updated_config = json.loads(config_file.read_text())
            updated_description = updated_config["projects"]["test-project"]["categories"]["custom_test"]["description"]
            assert updated_description == "Updated description via auto-save"
