"""Tests for auditing PWD usage in the codebase."""

import ast
from pathlib import Path
from typing import List, Tuple

import pytest


class PWDUsageFinder(ast.NodeVisitor):
    """AST visitor to find PWD and getcwd usage."""

    def __init__(self):
        self.pwd_usage: List[Tuple[int, str]] = []

    def visit_Name(self, node: ast.Name) -> None:
        """Visit name nodes to find PWD references."""
        if node.id == "PWD":
            self.pwd_usage.append((node.lineno, "PWD variable"))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute nodes to find getcwd calls."""
        if isinstance(node.value, ast.Name) and node.value.id == "os" and node.attr == "getcwd":
            self.pwd_usage.append((node.lineno, "os.getcwd()"))
        elif (
            isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "Path"
            and node.attr == "cwd"
        ):
            self.pwd_usage.append((node.lineno, "Path.cwd()"))
        self.generic_visit(node)


def scan_file_for_pwd_usage(file_path: Path) -> List[Tuple[int, str]]:
    """Scan a Python file for PWD usage."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        finder = PWDUsageFinder()
        finder.visit(tree)
        return finder.pwd_usage
    except (SyntaxError, UnicodeDecodeError):
        return []


def test_pwd_usage_audit():
    """Test that identifies all PWD/getcwd usage in codebase."""
    src_dir = Path("src")
    pwd_findings = {}

    # Scan all Python files in src directory
    for py_file in src_dir.rglob("*.py"):
        usage = scan_file_for_pwd_usage(py_file)
        if usage:
            pwd_findings[str(py_file)] = usage

    # This test should initially fail to expose current PWD usage
    if pwd_findings:
        findings_report = []
        for file_path, usages in pwd_findings.items():
            for line_no, usage_type in usages:
                findings_report.append(f"{file_path}:{line_no} - {usage_type}")

        pytest.fail("Found PWD/getcwd usage that needs migration:\n" + "\n".join(findings_report))

    # If no PWD usage found, the audit is complete
    assert True, "No PWD usage found - audit complete"


def test_environment_pwd_usage():
    """Test for environment variable PWD usage."""
    src_dir = Path("src")
    env_pwd_findings = {}

    for py_file in src_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for os.environ['PWD'] or os.getenv('PWD')
            if "PWD" in content and ("environ" in content or "getenv" in content):
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "PWD" in line and ("environ" in line or "getenv" in line):
                        if py_file not in env_pwd_findings:
                            env_pwd_findings[py_file] = []
                        env_pwd_findings[py_file].append((i, line.strip()))
        except UnicodeDecodeError:
            continue

    if env_pwd_findings:
        findings_report = []
        for file_path, usages in env_pwd_findings.items():
            for line_no, line_content in usages:
                findings_report.append(f"{file_path}:{line_no} - {line_content}")

        pytest.fail("Found environment PWD usage that needs migration:\n" + "\n".join(findings_report))

    assert True, "No environment PWD usage found"
