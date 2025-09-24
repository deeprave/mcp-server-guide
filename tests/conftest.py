"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def guide_dir(project_root: Path) -> Path:
    """Return the guide directory."""
    return project_root / "guide"


@pytest.fixture
def project_dir(project_root: Path) -> Path:
    """Return the project directory."""
    return project_root / "project"


@pytest.fixture
def lang_dir(project_root: Path) -> Path:
    """Return the lang directory."""
    return project_root / "lang"
