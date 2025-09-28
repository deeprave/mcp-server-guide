#!/usr/bin/env python3
"""Helper script to migrate current config to categories format."""

from src.mcp_server_guide.session_tools import SessionManager

def migrate_config():
    """Migrate current config to categories format."""
    session = SessionManager()
    project = session.get_current_project()

    print(f"Migrating config for project: {project}")

    # Get current config
    config = session.session_state.get_project_config(project)
    print("Current config:", config)

    # Create categories from existing config
    categories = {}

    # Migrate guide
    if config.get("guide") and config.get("guidesdir"):
        categories["guide"] = {
            "dir": config["guidesdir"],
            "patterns": [config["guide"]]
        }

    # Migrate lang
    if config.get("language") and config.get("langdir"):
        categories["lang"] = {
            "dir": config["langdir"],
            "patterns": [config["language"]]
        }

    # Migrate context
    if config.get("context") and config.get("contextdir"):
        categories["context"] = {
            "dir": config["contextdir"],
            "patterns": [config["context"]]
        }

    # Add categories to config
    config["categories"] = categories

    # Remove old fields (optional - can keep for backward compatibility)
    # old_fields = ["guide", "guidesdir", "language", "langdir", "context", "contextdir", "projdir"]
    # for field in old_fields:
    #     config.pop(field, None)

    # Save updated config using the config tools
    from src.mcp_server_guide.tools.config_tools import set_project_config_values

    # Set the categories in the config
    result = set_project_config_values({"categories": categories}, project)

    print("New categories:", categories)
    print("Set config result:", result)
    print("Migration complete!")

if __name__ == "__main__":
    migrate_config()
