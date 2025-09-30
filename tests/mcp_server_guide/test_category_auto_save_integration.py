"""Integration tests for category auto-save functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.mcp_server_guide.tools.category_tools import update_category
from src.mcp_server_guide.session_tools import SessionManager


def test_auto_save_actually_writes_to_file():
    """Test that auto-save actually writes changes to the config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test-config.json"

        # Create initial config file
        initial_config = {
            "projects": {
                "test-project": {
                    "categories": {
                        "guide": {"dir": "guide/", "patterns": ["guidelines"], "description": "Original description"}
                    }
                }
            }
        }
        config_file.write_text(json.dumps(initial_config, indent=2))

        # Mock SessionManager to use our test config file
        with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
            session_instance = SessionManager()
            mock_session_class.return_value = session_instance

            # Set up the session to use our test project and config
            session_instance.set_current_project("test-project")
            session_instance.session_state.projects["test-project"] = {
                "categories": {
                    "guide": {"dir": "guide/", "patterns": ["guidelines"], "description": "Original description"}
                }
            }

            # Override save_to_file to use our test config file
            original_save = session_instance.save_to_file

            def mock_save(filename=None):
                # Ensure directory exists
                config_file.parent.mkdir(parents=True, exist_ok=True)
                return original_save(str(config_file))

            session_instance.save_to_file = mock_save

            # Update category - this should trigger auto-save
            result = update_category("guide", "guide/", ["guidelines"], description="Updated description via auto-save")

            assert result["success"] is True

            # Check that the file was actually updated
            updated_config = json.loads(config_file.read_text())
            updated_description = updated_config["projects"]["test-project"]["categories"]["guide"]["description"]
            assert updated_description == "Updated description via auto-save"
