"""Tests for language detection functionality."""

import tempfile
from pathlib import Path
import json

from mcp_server_guide.language_detection import (
    detect_project_language,
    count_source_files,
    should_auto_detect_language,
)


def test_count_source_files():
    """Test source file counting with limits."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        (Path(temp_dir) / "test1.py").touch()
        (Path(temp_dir) / "test2.py").touch()
        (Path(temp_dir) / "subdir").mkdir()
        (Path(temp_dir) / "subdir" / "test3.py").touch()

        count = count_source_files(temp_dir, ["*.py"], max_depth=3, max_files=60)
        assert count == 3


def test_definitive_indicators():
    """Test definitive language indicators."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test Rust
        (Path(temp_dir) / "Cargo.toml").touch()
        assert detect_project_language(temp_dir) == "rust"

        # Test Python
        (Path(temp_dir) / "Cargo.toml").unlink()
        (Path(temp_dir) / "pyproject.toml").touch()
        assert detect_project_language(temp_dir) == "python"


def test_gradle_detection():
    """Test Gradle project detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "build.gradle").touch()

        # Create more Kotlin files than Java
        (Path(temp_dir) / "src").mkdir()
        (Path(temp_dir) / "src" / "App.kt").touch()
        (Path(temp_dir) / "src" / "Utils.kt").touch()
        (Path(temp_dir) / "src" / "Main.java").touch()

        assert detect_project_language(temp_dir) == "kotlin"


def test_package_json_detection():
    """Test package.json detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create package.json with TypeScript deps
        package_json = Path(temp_dir) / "package.json"
        package_json.write_text(json.dumps({"devDependencies": {"typescript": "^4.0.0"}}))

        (Path(temp_dir) / "src.js").touch()
        assert detect_project_language(temp_dir) == "typescript"


def test_makefile_detection():
    """Test Makefile detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "Makefile").touch()

        # Create C++ files
        (Path(temp_dir) / "main.cpp").touch()
        (Path(temp_dir) / "utils.hpp").touch()

        assert detect_project_language(temp_dir) == "cpp"


def test_pure_source_detection():
    """Test pure source file detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test Swift
        (Path(temp_dir) / "App.swift").touch()
        assert detect_project_language(temp_dir) == "swift"

        # Test C#
        (Path(temp_dir) / "App.swift").unlink()
        (Path(temp_dir) / "Program.cs").touch()
        assert detect_project_language(temp_dir) == "csharp"


def test_scala_detection():
    """Test Scala detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "build.sbt").touch()
        (Path(temp_dir) / "App.scala").touch()
        (Path(temp_dir) / "Utils.scala").touch()
        (Path(temp_dir) / "Main.java").touch()

        assert detect_project_language(temp_dir) == "scala"


def test_no_detection():
    """Test when no language can be detected."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "README.txt").touch()
        assert detect_project_language(temp_dir) is None


def test_should_auto_detect_language():
    """Test auto-detection conditions."""
    assert should_auto_detect_language(None) is True
    assert should_auto_detect_language("") is True
    assert should_auto_detect_language("none") is True
    assert should_auto_detect_language("python") is False


def test_package_json_fallback():
    """Test package.json fallback when JSON parsing fails."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid JSON
        (Path(temp_dir) / "package.json").write_text("invalid json")
        (Path(temp_dir) / "app.ts").touch()
        (Path(temp_dir) / "app2.ts").touch()  # More TS files than JS
        (Path(temp_dir) / "utils.js").touch()

        assert detect_project_language(temp_dir) == "typescript"


def test_makefile_no_source_files():
    """Test Makefile with no source files (generic Makefile)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "Makefile").touch()
        (Path(temp_dir) / "README.txt").touch()

        assert detect_project_language(temp_dir) is None


def test_maven_kotlin_preference():
    """Test Maven with more Kotlin than Java files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "pom.xml").touch()
        (Path(temp_dir) / "App.kt").touch()
        (Path(temp_dir) / "Utils.kt").touch()
        (Path(temp_dir) / "Main.java").touch()

        assert detect_project_language(temp_dir) == "kotlin"
