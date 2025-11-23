"""File operation tools."""

from pathlib import Path
from typing import Optional

import aiofiles


async def get_file_content(path: str, project: Optional[str] = None) -> str:
    """Get raw file content."""
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        else:
            return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"


__all__ = [
    "get_file_content",
]
