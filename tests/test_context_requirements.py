"""Tests for identifying tools that need Context parameters."""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any

import pytest

from mcp_server_guide.tools import category_tools, collection_tools, content_tools, document_tools


class ToolAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze tool function signatures."""

    def __init__(self):
        self.functions: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to analyze signatures."""
        # Check if it's a tool function (has @mcp.tool decorator or similar)
        is_tool = any(
            (isinstance(decorator, ast.Name) and decorator.id in ["tool"])
            or (isinstance(decorator, ast.Attribute) and decorator.attr == "tool")
            for decorator in node.decorator_list
        )

        if is_tool:
            # Analyze parameters
            has_context = any(
                arg.arg == "ctx"
                or (arg.annotation and isinstance(arg.annotation, ast.Name) and arg.annotation.id == "Context")
                for arg in node.args.args
            )

            self.functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "has_context": has_context,
                    "args": [arg.arg for arg in node.args.args],
                }
            )

        self.generic_visit(node)


def analyze_tool_file(file_path: Path) -> List[Dict[str, Any]]:
    """Analyze a Python file for tool functions."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analyzer = ToolAnalyzer()
        analyzer.visit(tree)
        return analyzer.functions
    except (SyntaxError, UnicodeDecodeError):
        return []


def test_tools_needing_context():
    """Test that identifies tools requiring Context parameters."""
    tools_dir = Path("src/mcp_server_guide/tools")
    context_findings = {}

    # Analyze all tool files
    for py_file in tools_dir.glob("*_tools.py"):
        if py_file.name.endswith("_json.py"):
            continue  # Skip JSON tool files

        functions = analyze_tool_file(py_file)
        if functions:
            context_findings[str(py_file)] = functions

    # Report tools that might need Context but don't have it
    needs_context = []
    for file_path, functions in context_findings.items():
        for func in functions:
            # Tools that work with files/paths likely need Context
            if not func["has_context"] and any(
                keyword in func["name"].lower() for keyword in ["file", "content", "search", "category", "document"]
            ):
                needs_context.append(f"{file_path}:{func['line']} - {func['name']}()")

    if needs_context:
        pytest.fail("Tools that may need Context parameter:\n" + "\n".join(needs_context))

    # For now, this test documents the current state
    assert True, f"Analyzed {len(context_findings)} tool files"


def test_current_tool_signatures():
    """Test to document current tool signatures for migration planning."""
    # Get actual function signatures from imported modules
    tool_modules = [category_tools, collection_tools, content_tools, document_tools]

    signatures = {}
    for module in tool_modules:
        module_name = module.__name__.split(".")[-1]
        signatures[module_name] = {}

        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    sig = inspect.signature(obj)
                    has_context = "ctx" in sig.parameters
                    signatures[module_name][name] = {
                        "signature": str(sig),
                        "has_context": has_context,
                        "parameters": list(sig.parameters.keys()),
                    }
                except (ValueError, TypeError):
                    continue

    # This test documents current state - will be used for migration planning
    tools_without_context = []
    for module_name, functions in signatures.items():
        for func_name, info in functions.items():
            if not info["has_context"] and "guide_" in func_name:
                tools_without_context.append(f"{module_name}.{func_name}")

    if tools_without_context:
        pytest.fail("Tools without Context parameter (need migration):\n" + "\n".join(tools_without_context))

    assert True, "Tool signature analysis complete"
