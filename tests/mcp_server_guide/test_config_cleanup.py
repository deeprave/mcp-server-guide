"""Tests for configuration cleanup - removing obsolete fields."""

from src.mcp_server_guide.session_tools import SessionManager


def test_cleanup_preserves_docroot():
    """Test that cleanup preserves docroot field (not obsolete)."""
    session = SessionManager()

    # Set up project config with docroot and obsolete fields
    project_name = "test-project"
    session.session_state.projects[project_name] = {
        # Should be preserved
        "docroot": "/custom/path",
        "tools": ["tool1"],
        "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"]}},
        # Should be removed
        "guidesdir": "old/guide/",
        "language": "python",
    }

    # Run cleanup
    session.cleanup_obsolete_config()

    # Verify docroot is preserved but obsolete fields removed
    config = session.session_state.projects[project_name]

    assert "docroot" in config  # Should be preserved
    assert config["docroot"] == "/custom/path"
    assert "tools" in config
    assert "categories" in config

    assert "guidesdir" not in config  # Should be removed
    assert "language" not in config  # Should be removed


def test_cleanup_obsolete_config_method():
    """Test that cleanup_obsolete_config removes obsolete fields."""
    session = SessionManager()

    # Manually set up project config with obsolete fields
    project_name = "test-project"
    session.session_state.projects[project_name] = {
        # Obsolete fields
        "guidesdir": "aidocs/guide/",
        "guide": "guidelines",
        "langdir": "aidocs/lang/",
        "language": "python",
        "contextdir": "aidocs/context",
        "context": "freeform",
        "projdir": "aidocs/context/",
        # Modern fields
        "docroot": ".",
        "tools": ["example-tool"],
        "categories": {"guide": {"dir": "guide/", "patterns": ["**/*.md"]}},
    }

    # Run cleanup
    session.cleanup_obsolete_config()

    # Verify obsolete fields are removed
    config = session.session_state.projects[project_name]

    # Obsolete fields should be gone
    assert "guidesdir" not in config
    assert "guide" not in config
    assert "langdir" not in config
    assert "language" not in config
    assert "contextdir" not in config
    assert "context" not in config
    assert "projdir" not in config

    # Modern fields should remain
    assert "docroot" in config
    assert "tools" in config
    assert "categories" in config


def test_cleanup_preserves_modern_fields():
    """Test that cleanup preserves modern configuration fields."""
    session = SessionManager()

    # Set up project config with only modern fields
    project_name = "test-project"
    session.session_state.projects[project_name] = {
        "docroot": "/custom/path",
        "tools": ["tool1", "tool2"],
        "categories": {
            "guide": {"dir": "guides/", "patterns": ["*.md"]},
            "custom": {"dir": "custom/", "patterns": ["*.txt"]},
        },
    }

    # Run cleanup
    session.cleanup_obsolete_config()

    # Verify all modern fields are preserved
    config = session.session_state.projects[project_name]

    assert config["docroot"] == "/custom/path"
    assert config["tools"] == ["tool1", "tool2"]
    assert len(config["categories"]) == 2
    assert "guide" in config["categories"]
    assert "custom" in config["categories"]


def test_cleanup_handles_empty_project():
    """Test that cleanup handles projects without any config gracefully."""
    session = SessionManager()

    # Set up empty project config
    project_name = "empty-project"
    session.session_state.projects[project_name] = {}

    # Run cleanup (should not crash)
    session.cleanup_obsolete_config()

    # Verify project still exists but empty
    assert project_name in session.session_state.projects
    assert session.session_state.projects[project_name] == {}


def test_cleanup_multiple_projects():
    """Test that cleanup works across multiple projects."""
    session = SessionManager()

    # Set up multiple projects with mixed configs
    session.session_state.projects["project1"] = {
        "guidesdir": "old/path",  # obsolete
        "docroot": ".",  # modern
        "categories": {},  # modern
    }

    session.session_state.projects["project2"] = {
        "language": "python",  # obsolete
        "tools": ["tool1"],  # modern
    }

    # Run cleanup
    session.cleanup_obsolete_config()

    # Verify cleanup worked for both projects
    config1 = session.session_state.projects["project1"]
    config2 = session.session_state.projects["project2"]

    assert "guidesdir" not in config1
    assert "docroot" in config1
    assert "categories" in config1

    assert "language" not in config2
    assert "tools" in config2
