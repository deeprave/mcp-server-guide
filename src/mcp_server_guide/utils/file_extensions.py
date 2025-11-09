"""File extension utilities for consistent extension handling."""

from pathlib import Path
from typing import List, Optional


def try_file_with_extensions(base_path: Path, filename: str, extensions: Optional[List[str]] = None) -> Optional[Path]:
    """Try to find a file with automatic extension fallback.

    Args:
        base_path: Directory to search in
        filename: Base filename to search for
        extensions: List of extensions to try (defaults to ['.md'])

    Returns:
        Path to found file or None if not found

    Priority:
        1. Exact filename match
        2. Filename with extensions (in order provided)
    """
    if extensions is None:
        extensions = [".md"]

    # Try exact match first
    exact_path = base_path / filename
    if exact_path.exists() and exact_path.is_file():
        return exact_path

    # Only try extensions if filename doesn't already have one
    if "." not in filename:
        for ext in extensions:
            ext_path = base_path / f"{filename}{ext}"
            if ext_path.exists() and ext_path.is_file():
                return ext_path

    return None


def get_extension_candidates(filename: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Get list of filename candidates with extension fallback.

    Args:
        filename: Base filename
        extensions: List of extensions to try (defaults to ['.md'])

    Returns:
        List of filename candidates in priority order
    """
    if extensions is None:
        extensions = [".md"]

    candidates = [filename]  # Exact match first

    # Only add extensions if filename doesn't already have one
    if "." not in filename:
        candidates.extend(f"{filename}{ext}" for ext in extensions)

    return candidates
