"""Tests for guide_clone_project tool."""

import pytest
from src.mcp_server_guide.session_manager import SessionManager


@pytest.mark.asyncio
async def test_clone_project_source_not_found(isolated_config_file):
    """Test error when source project doesn't exist."""
    from src.mcp_server_guide.tools.project_tools import clone_project

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    result = await clone_project(source_project="nonexistent")

    assert result["success"] is False
    assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()


@pytest.mark.asyncio
async def test_clone_project_to_new_target(isolated_config_file, tmp_path):
    """Test cloning to a new project that doesn't exist."""
    from src.mcp_server_guide.tools.project_tools import clone_project, switch_project

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    # Create source project with custom category
    await switch_project("source-proj")
    from src.mcp_server_guide.tools.category_tools import add_category

    await add_category(name="custom", dir="custom/", patterns=["*.txt"])

    # Clone to new target
    result = await clone_project(source_project="source-proj", target_project="target-proj")

    assert result["success"] is True

    # Verify target has the custom category
    await switch_project("target-proj")
    config = session.session_state.get_project_config()
    assert "custom" in config.categories


@pytest.mark.asyncio
async def test_clone_project_defaults_to_current(isolated_config_file):
    """Test that target defaults to current project."""
    from src.mcp_server_guide.tools.project_tools import clone_project, switch_project

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    # Create source with custom category
    await switch_project("source-proj")
    from src.mcp_server_guide.tools.category_tools import add_category

    await add_category(name="custom", dir="custom/", patterns=["*.txt"])

    # Switch to new target (will have defaults)
    await switch_project("target-proj")

    # Clone without specifying target (should use current)
    result = await clone_project(source_project="source-proj")

    assert result["success"] is True

    # Verify current project has custom category
    config = session.session_state.get_project_config()
    assert "custom" in config.categories


@pytest.mark.asyncio
async def test_clone_project_rejects_target_with_custom_content(isolated_config_file):
    """Test that clone rejects target with custom content without force."""
    from src.mcp_server_guide.tools.project_tools import clone_project, switch_project
    from src.mcp_server_guide.tools.category_tools import add_category

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    # Create source
    await switch_project("source-proj")
    await add_category(name="source-custom", dir="src/", patterns=["*.py"])

    # Create target with custom content
    await switch_project("target-proj")
    await add_category(name="target-custom", dir="tgt/", patterns=["*.md"])

    # Try to clone without force
    result = await clone_project(source_project="source-proj", target_project="target-proj")

    assert result["success"] is False
    assert "force" in result["error"].lower() or "custom" in result["error"].lower()


@pytest.mark.asyncio
async def test_clone_project_with_force_overwrites(isolated_config_file):
    """Test that force flag overwrites target with custom content."""
    from src.mcp_server_guide.tools.project_tools import clone_project, switch_project
    from src.mcp_server_guide.tools.category_tools import add_category

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    # Create source
    await switch_project("source-proj")
    await add_category(name="source-custom", dir="src/", patterns=["*.py"])

    # Create target with custom content
    await switch_project("target-proj")
    await add_category(name="target-custom", dir="tgt/", patterns=["*.md"])

    # Clone with force
    result = await clone_project(source_project="source-proj", target_project="target-proj", force=True)

    assert result["success"] is True

    # Verify target has source categories, not target's old ones
    config = session.session_state.get_project_config()
    assert "source-custom" in config.categories
    assert "target-custom" not in config.categories


@pytest.mark.asyncio
async def test_clone_project_creates_independent_copies(isolated_config_file):
    """Test that cloned categories are independent (deep copy, not shallow)."""
    from src.mcp_server_guide.tools.project_tools import clone_project, switch_project
    from src.mcp_server_guide.tools.category_tools import add_category, update_category

    session = SessionManager()
    session._set_config_filename(isolated_config_file)

    # Create source with custom category
    await switch_project("source-proj")
    await add_category(name="custom", dir="custom/", patterns=["*.txt"])

    # Get source config before cloning
    source_config_before = session.session_state.get_project_config()
    assert source_config_before.categories["custom"].patterns == ["*.txt"]

    # Clone to target
    await clone_project(source_project="source-proj", target_project="target-proj")

    # Modify target's category patterns
    await switch_project("target-proj")
    await update_category(name="custom", patterns=["*.md", "*.rst"])
    target_config = session.session_state.get_project_config()
    assert set(target_config.categories["custom"].patterns) == {"*.md", "*.rst"}

    # Verify source is unchanged by reloading it
    await switch_project("source-proj")
    source_config_after = session.session_state.get_project_config()
    assert source_config_after.categories["custom"].patterns == ["*.txt"]

