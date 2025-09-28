"""Path validation and sanitization utilities for security."""

import re
from pathlib import Path
from typing import List, Union
from ..exceptions import SecurityError


class PathValidator:
    """Validates file paths to prevent traversal attacks and unauthorized access."""

    def __init__(self, allowed_roots: List[Union[str, Path]]):
        """Initialize validator with allowed root directories.

        Args:
            allowed_roots: List of directory paths that are allowed as roots
        """
        self.allowed_roots = [Path(root).resolve() for root in allowed_roots]

    def validate_path(self, user_path: str, base_path: Path) -> Path:
        """Validate a user-provided path against security policies.

        Args:
            user_path: User-provided path string
            base_path: Base directory to resolve relative paths against

        Returns:
            Resolved absolute path if valid

        Raises:
            SecurityError: If path violates security boundaries
        """
        try:
            # Normalize path separators (convert backslashes to forward slashes)
            normalized_path = user_path.replace("\\", "/")

            # Handle absolute paths - they should be rejected unless they're within allowed roots
            if Path(normalized_path).is_absolute():
                resolved_path = Path(normalized_path).resolve()
            else:
                # Resolve relative paths against base_path
                resolved_path = (base_path / normalized_path).resolve()
        except (OSError, ValueError) as e:
            raise SecurityError(f"Invalid path: {user_path}") from e

        # Check if resolved path is within any allowed root
        if not any(self._is_within_root(resolved_path, root) for root in self.allowed_roots):
            raise SecurityError(f"Path outside allowed boundaries: {resolved_path}")

        return resolved_path

    def _is_within_root(self, path: Path, root: Path) -> bool:
        """Check if path is within the specified root directory."""
        try:
            # Both paths should be resolved to handle symlinks consistently
            resolved_path = path.resolve()
            resolved_root = root.resolve()
            resolved_path.relative_to(resolved_root)
            return True
        except ValueError:
            return False


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing dangerous characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename or filename.strip() in ("", ".", ".."):
        return "unnamed"

    # Remove or replace dangerous characters
    # Replace path separators and dangerous chars with underscores
    dangerous_chars = r'[/\\:*?"<>|]'
    sanitized = re.sub(dangerous_chars, "_", filename)

    # Remove path traversal sequences
    sanitized = re.sub(r"\.\.+", "", sanitized)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")

    # Remove multiple consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")

    # Ensure we have a valid filename
    if not sanitized:
        return "unnamed"

    return sanitized
