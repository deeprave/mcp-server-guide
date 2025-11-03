"""Validation utilities for the MCP server guide."""

import re


def is_valid_name(name: str) -> bool:
    """Check if a name is valid (letters, numbers, dash, underscore only)."""
    return bool(name and name.strip() and re.match(r"^[\w-]+$", name.strip()))


def validate_description(v: str) -> str:
    """Common description validation - strip whitespace and handle None."""
    return v.strip() if v else ""
