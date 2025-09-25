"""Tests for tools module structure (Issue 005 Phase 1)."""

import pytest


def test_tools_module_imports():
    """Test that tools module can be imported."""
    from mcpguide import tools

    assert tools is not None


def test_project_tools_module():
    """Test project tools module exists."""
    from mcpguide.tools import project_tools

    assert project_tools is not None


def test_config_tools_module():
    """Test config tools module exists."""
    from mcpguide.tools import config_tools

    assert config_tools is not None


def test_content_tools_module():
    """Test content tools module exists."""
    from mcpguide.tools import content_tools

    assert content_tools is not None


def test_file_tools_module():
    """Test file tools module exists."""
    from mcpguide.tools import file_tools

    assert file_tools is not None


def test_session_tools_module():
    """Test session tools module exists."""
    from mcpguide.tools import session_management

    assert session_management is not None


def test_tools_module_has_all_exports():
    """Test that tools module exports all expected functions."""
    from mcpguide import tools

    # Project Management
    assert hasattr(tools, "get_current_project")
    assert hasattr(tools, "switch_project")
    assert hasattr(tools, "list_projects")

    # Configuration Access
    assert hasattr(tools, "get_project_config")
    assert hasattr(tools, "set_project_config")
    assert hasattr(tools, "get_effective_config")
    assert hasattr(tools, "get_tools")
    assert hasattr(tools, "set_tools")

    # Content Retrieval
    assert hasattr(tools, "get_guide")
    assert hasattr(tools, "get_language_guide")
    assert hasattr(tools, "get_project_context")
    assert hasattr(tools, "get_all_guides")
    assert hasattr(tools, "search_content")
    assert hasattr(tools, "show_guide")
    assert hasattr(tools, "show_language_guide")
    assert hasattr(tools, "show_project_summary")

    # File Operations
    assert hasattr(tools, "list_files")
    assert hasattr(tools, "file_exists")
    assert hasattr(tools, "get_file_content")

    # Session Management
    assert hasattr(tools, "save_session")
    assert hasattr(tools, "load_session")
    assert hasattr(tools, "reset_session")
