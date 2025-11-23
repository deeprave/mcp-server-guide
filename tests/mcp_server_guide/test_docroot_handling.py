"""Tests for docroot handling in ProjectConfigManager."""

from pathlib import Path
from unittest.mock import patch

import yaml

from mcp_server_guide.models.category import Category
from mcp_server_guide.path_resolver import LazyPath
from mcp_server_guide.project_config import ProjectConfig, ProjectConfigManager


class TestDocrootInitialization:
    """Test docroot initialization for new config files."""

    async def test_new_config_file_gets_default_docroot(self, tmp_path):
        """New config file should get docroot='.' as default."""
        config_file = tmp_path / "config.yaml"
        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Create a new project config
        project_config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"], description="Test category")}
        )

        # Mock get_default_docroot to return test-relative path
        expected_docroot = str(config_file.parent / "docs")

        # Mock both the config file function and the auto-init function
        with (
            patch("mcp_server_guide.models.config_file.get_default_docroot", return_value=expected_docroot),
            patch("mcp_server_guide.installation.get_default_docroot", return_value=expected_docroot),
        ):
            # Save the config
            await manager.save_config("test-project", project_config)

        # Verify the file was created with docroot="."
        assert config_file.exists()
        with open(config_file) as f:
            data = yaml.safe_load(f)

        # Docroot should now be the proper default path, not "."
        assert data["docroot"] == expected_docroot
        assert "test-project" in data["projects"]

        # Verify docroot is cached in manager
        assert manager.docroot is not None
        assert str(manager.docroot) == expected_docroot

    async def test_config_without_docroot_element_gets_default(self, tmp_path):
        """Existing config file without docroot element gets docroot='.' when saving."""
        config_file = tmp_path / "config.yaml"

        # Create a config file without docroot element
        initial_data = {
            "projects": {
                "existing-project": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            }
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load existing project
        loaded_config = await manager.load_config("existing-project")
        assert loaded_config is not None

        # Verify docroot was defaulted and cached
        assert manager.docroot is not None
        # Docroot should be the proper default path
        from mcp_server_guide.models.config_file import get_default_docroot

        expected_docroot = str(get_default_docroot())
        assert str(manager.docroot) == expected_docroot

        # Save a new project
        new_project_config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"], description="Test")}
        )
        await manager.save_config("new-project", new_project_config)

        # Verify docroot was set to default
        with open(config_file) as f:
            data = yaml.safe_load(f)

        assert data["docroot"] == expected_docroot
        assert "existing-project" in data["projects"]
        assert "new-project" in data["projects"]


class TestDocrootPreservation:
    """Test that existing docroot is preserved."""

    async def test_existing_docroot_is_preserved(self, tmp_path):
        """Existing docroot should be preserved when saving new projects."""
        config_file = tmp_path / "config.yaml"

        # Create a config file with custom docroot
        initial_data = {
            "docroot": "~/custom/docs",
            "projects": {
                "project1": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load existing project
        loaded_config = await manager.load_config("project1")
        assert loaded_config is not None

        # Verify docroot was loaded and cached
        assert manager.docroot is not None
        assert str(manager.docroot) == "~/custom/docs"

        # Save a new project
        new_project_config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"], description="Test")}
        )
        await manager.save_config("project2", new_project_config)

        # Verify docroot was preserved
        with open(config_file) as f:
            data = yaml.safe_load(f)

        assert data["docroot"] == "~/custom/docs"
        assert "project1" in data["projects"]
        assert "project2" in data["projects"]

        # Verify cached docroot is still correct
        assert str(manager.docroot) == "~/custom/docs"

    async def test_updating_project_preserves_docroot(self, tmp_path):
        """Updating a project should preserve the docroot."""
        config_file = tmp_path / "config.yaml"

        # Create initial config
        initial_data = {
            "docroot": "/absolute/path/docs",
            "projects": {
                "test-project": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load and update the project
        loaded_config = await manager.load_config("test-project")
        assert loaded_config is not None

        # Update the project config
        updated_config = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["*.md"], description="Guide"),
                "context": Category(dir="context/", patterns=["*.md"], description="Context"),
            }
        )
        await manager.save_config("test-project", updated_config)

        # Verify docroot was preserved
        with open(config_file) as f:
            data = yaml.safe_load(f)

        assert data["docroot"] == "/absolute/path/docs"
        assert len(data["projects"]["test-project"]["categories"]) == 2


class TestDocrootExpansion:
    """Test docroot expansion with tilde and environment variables."""

    async def test_docroot_with_tilde_expansion(self, tmp_path):
        """Docroot with ~ should be cached as LazyPath and expand correctly."""
        config_file = tmp_path / "config.yaml"

        # Create config with tilde path
        initial_data = {
            "docroot": "~/documents/project-docs",
            "projects": {
                "test-project": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load the config
        loaded_config = await manager.load_config("test-project")
        assert loaded_config is not None

        # Verify docroot is cached as LazyPath
        assert manager.docroot is not None
        assert isinstance(manager.docroot, LazyPath)
        assert str(manager.docroot) == "~/documents/project-docs"

        # Verify expansion works
        expanded = manager.docroot.expanduser()
        assert expanded.startswith(str(Path.home()))
        assert "documents/project-docs" in expanded

    async def test_docroot_with_environment_variable(self, tmp_path, monkeypatch):
        """Docroot with ${VAR} should be cached as LazyPath and expand correctly."""
        config_file = tmp_path / "config.yaml"

        # Set test environment variable
        test_base = "/opt/project-base"
        monkeypatch.setenv("PROJECT_BASE", test_base)

        # Create config with environment variable
        initial_data = {
            "docroot": "${PROJECT_BASE}/docs",
            "projects": {
                "test-project": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load the config
        loaded_config = await manager.load_config("test-project")
        assert loaded_config is not None

        # Verify docroot is cached as LazyPath
        assert manager.docroot is not None
        assert isinstance(manager.docroot, LazyPath)
        assert str(manager.docroot) == "${PROJECT_BASE}/docs"

        # Verify expansion works
        expanded = manager.docroot.expandvars()
        assert expanded == f"{test_base}/docs"


class TestDocrootCaching:
    """Test docroot caching behavior."""

    async def test_docroot_cached_after_load(self, tmp_path):
        """Docroot should be cached after loading a project."""
        config_file = tmp_path / "config.yaml"

        # Create config
        initial_data = {
            "docroot": "~/test-docs",
            "projects": {
                "project1": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Before loading, docroot should be None
        assert manager.docroot is None

        # Load config
        loaded_config = await manager.load_config("project1")
        assert loaded_config is not None

        # After loading, docroot should be cached
        assert manager.docroot is not None
        assert str(manager.docroot) == "~/test-docs"

    async def test_docroot_cached_after_save(self, tmp_path):
        """Docroot should be cached after saving a project."""
        config_file = tmp_path / "config.yaml"

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Before saving, docroot should be None
        assert manager.docroot is None

        # Save a new project
        project_config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"], description="Test")}
        )

        # Mock get_default_docroot to return test-relative path
        expected_docroot = str(tmp_path / "docs")

        # Mock both the config file function and the auto-init function
        with (
            patch("mcp_server_guide.models.config_file.get_default_docroot", return_value=expected_docroot),
            patch("mcp_server_guide.installation.get_default_docroot", return_value=expected_docroot),
        ):
            await manager.save_config("new-project", project_config)

        # After saving, docroot should be cached (with default value)
        assert manager.docroot is not None
        # Docroot should be the proper default path
        assert str(manager.docroot) == expected_docroot

    async def test_docroot_updated_on_subsequent_operations(self, tmp_path):
        """Docroot cache should be updated on subsequent load/save operations."""
        config_file = tmp_path / "config.yaml"

        # Create initial config with one docroot
        initial_data = {
            "docroot": "~/first-docs",
            "projects": {
                "project1": {
                    "categories": {
                        "guide": {
                            "dir": "guide/",
                            "patterns": ["*.md"],
                            "description": "Guide",
                        }
                    }
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        manager = ProjectConfigManager()
        manager.set_config_filename(config_file)

        # Load and verify first docroot
        await manager.load_config("project1")
        assert str(manager.docroot) == "~/first-docs"

        # Manually update docroot in file
        updated_data = {
            "docroot": "~/second-docs",
            "projects": initial_data["projects"],
        }
        with open(config_file, "w") as f:
            yaml.dump(updated_data, f)

        # Load again and verify cache is updated
        await manager.load_config("project1")
        assert str(manager.docroot) == "~/second-docs"
