"""Tests for osvcheck.py security vulnerability checker."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

# Add src to path to import osvcheck
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import osvcheck


class TestGetDirectDependencies:
    """Test get_direct_dependencies function."""

    def test_get_direct_dependencies_success(self):
        """Test successful parsing of pyproject.toml dependencies."""
        toml_content = b"""
[project]
dependencies = [
    "click>=8.3.0",
    "mcp[cli]>=1.16.0",
    "pydantic>=2.0",
    "pyyaml~=6.0",
    "requests!=2.24.0,>=2.25.0",
]
"""
        with patch("builtins.open", mock_open(read_data=toml_content)):
            deps = osvcheck.get_direct_dependencies()

        assert deps == ["click", "mcp", "pydantic", "pyyaml", "requests"]

    def test_get_direct_dependencies_no_file(self):
        """Test handling when pyproject.toml doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            deps = osvcheck.get_direct_dependencies()

        assert deps == []

    def test_get_direct_dependencies_no_project_section(self):
        """Test handling when pyproject.toml has no project section."""
        toml_content = b"""
[build-system]
requires = ["hatchling"]
"""
        with patch("builtins.open", mock_open(read_data=toml_content)):
            deps = osvcheck.get_direct_dependencies()

        assert deps == []

    def test_get_direct_dependencies_no_dependencies(self):
        """Test handling when project section has no dependencies."""
        toml_content = b"""
[project]
name = "test-package"
"""
        with patch("builtins.open", mock_open(read_data=toml_content)):
            deps = osvcheck.get_direct_dependencies()

        assert deps == []


class TestGetAllInstalledPackages:
    """Test get_all_installed_packages function."""

    def test_get_all_installed_packages_success(self):
        """Test successful retrieval of installed packages."""
        mock_output = json.dumps(
            [
                {"name": "click", "version": "8.3.0"},
                {"name": "pydantic", "version": "2.12.3"},
            ]
        )

        mock_result = Mock()
        mock_result.stdout = mock_output

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            packages = osvcheck.get_all_installed_packages()

        mock_run.assert_called_once_with(
            ["uv", "pip", "list", "--format", "json"], capture_output=True, text=True, check=True
        )
        assert packages == [
            {"name": "click", "version": "8.3.0"},
            {"name": "pydantic", "version": "2.12.3"},
        ]

    def test_get_all_installed_packages_subprocess_error(self):
        """Test handling when subprocess fails."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "uv")):
            packages = osvcheck.get_all_installed_packages()

        assert packages == []

    def test_get_all_installed_packages_json_error(self):
        """Test handling when JSON parsing fails."""
        mock_result = Mock()
        mock_result.stdout = "invalid json"

        with patch("subprocess.run", return_value=mock_result):
            packages = osvcheck.get_all_installed_packages()

        assert packages == []


class TestMain:
    """Test main function integration."""

    @patch("osvcheck.save_cache")
    @patch("osvcheck.load_cache")
    @patch("osvcheck.get_all_installed_packages")
    @patch("osvcheck.get_direct_dependencies")
    @patch("urllib.request.urlopen")
    def test_main_no_vulnerabilities(self, mock_urlopen, mock_get_deps, mock_get_packages, mock_load_cache, mock_save_cache, capsys):
        """Test main function with no vulnerabilities found."""
        # Setup cache mocks
        mock_load_cache.return_value = {}

        # Setup mocks
        mock_get_deps.return_value = ["click", "pydantic"]
        mock_get_packages.return_value = [
            {"name": "click", "version": "8.3.0"},
            {"name": "pydantic", "version": "2.12.3"},
        ]

        # Mock OSV API response (no vulnerabilities)
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({"vulns": []}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(SystemExit) as exc_info:
            osvcheck.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Checking 2 packages (2 direct dependencies)" in captured.out

    @patch("osvcheck.save_cache")
    @patch("osvcheck.load_cache")
    @patch("osvcheck.get_all_installed_packages")
    @patch("osvcheck.get_direct_dependencies")
    @patch("urllib.request.urlopen")
    def test_main_with_direct_vulnerabilities(self, mock_urlopen, mock_get_deps, mock_get_packages, mock_load_cache, mock_save_cache, capsys):
        """Test main function with direct dependency vulnerabilities."""
        # Setup cache mocks
        mock_load_cache.return_value = {}

        # Setup mocks
        mock_get_deps.return_value = ["vulnerable-pkg"]
        mock_get_packages.return_value = [
            {"name": "vulnerable-pkg", "version": "1.0.0"},
        ]

        # Mock OSV API response (with vulnerabilities)
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {"vulns": [{"id": "VULN-001", "summary": "Test vulnerability"}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(SystemExit) as exc_info:
            osvcheck.main()

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "⚠️  [DIRECT] vulnerable-pkg 1.0.0: vulnerabilities found" in captured.out
        assert "1 direct dependency vulnerabilities:" in captured.out
        assert "vulnerable-pkg" in captured.out

    @patch("osvcheck.save_cache")
    @patch("osvcheck.load_cache")
    @patch("osvcheck.get_all_installed_packages")
    @patch("osvcheck.get_direct_dependencies")
    @patch("urllib.request.urlopen")
    def test_main_with_indirect_vulnerabilities(self, mock_urlopen, mock_get_deps, mock_get_packages, mock_load_cache, mock_save_cache, capsys):
        """Test main function with indirect dependency vulnerabilities."""
        # Setup cache mocks
        mock_load_cache.return_value = {}

        # Setup mocks
        mock_get_deps.return_value = ["safe-pkg"]
        mock_get_packages.return_value = [
            {"name": "safe-pkg", "version": "1.0.0"},
            {"name": "indirect-vuln", "version": "2.0.0"},
        ]

        # Track which package is being queried
        call_count = [0]

        def mock_api_response(*args, **kwargs):
            """Mock different responses based on call order."""
            mock_response = Mock()
            if call_count[0] == 0:  # First call (safe-pkg)
                mock_response.read.return_value = json.dumps({"vulns": []}).encode()
            else:  # Second call (indirect-vuln)
                mock_response.read.return_value = json.dumps(
                    {"vulns": [{"id": "VULN-002", "summary": "Indirect vulnerability"}]}
                ).encode()
            call_count[0] += 1
            return mock_response

        mock_urlopen.return_value.__enter__ = mock_api_response

        with pytest.raises(SystemExit) as exc_info:
            osvcheck.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "  ⚠️ [indirect] indirect-vuln 2.0.0: vulnerabilities found" in captured.out
        assert "1 indirect dependency vulnerabilities:" in captured.out
        assert "indirect-vuln" in captured.out

    @patch("osvcheck.save_cache")
    @patch("osvcheck.load_cache")
    @patch("osvcheck.get_all_installed_packages")
    @patch("osvcheck.get_direct_dependencies")
    @patch("urllib.request.urlopen")
    def test_main_api_error_handling(self, mock_urlopen, mock_get_deps, mock_get_packages, mock_load_cache, mock_save_cache, capsys):
        """Test main function handles API errors gracefully."""
        # Setup cache mocks
        mock_load_cache.return_value = {}

        # Setup mocks
        mock_get_deps.return_value = ["test-pkg"]
        mock_get_packages.return_value = [{"name": "test-pkg", "version": "1.0.0"}]

        # Mock API error
        mock_urlopen.side_effect = Exception("API Error")

        with pytest.raises(SystemExit) as exc_info:
            osvcheck.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Checking 1 packages (1 direct dependencies)" in captured.out

    @patch("osvcheck.save_cache")
    @patch("osvcheck.load_cache")
    @patch("osvcheck.get_all_installed_packages")
    @patch("osvcheck.get_direct_dependencies")
    @patch("urllib.request.urlopen")
    def test_main_many_indirect_vulnerabilities(self, mock_urlopen, mock_get_deps, mock_get_packages, mock_load_cache, mock_save_cache, capsys):
        """Test main function with many indirect vulnerabilities (truncation)."""
        # Setup cache mocks
        mock_load_cache.return_value = {}

        # Setup mocks with many indirect vulnerable packages
        mock_get_deps.return_value = []
        mock_get_packages.return_value = [{"name": f"vuln-pkg-{i}", "version": "1.0.0"} for i in range(10)]

        # Mock all packages as vulnerable
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {"vulns": [{"id": "VULN-001", "summary": "Test vulnerability"}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(SystemExit) as exc_info:
            osvcheck.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "10 indirect dependency vulnerabilities:" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])
