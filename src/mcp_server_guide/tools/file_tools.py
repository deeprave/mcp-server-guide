"""File operation tools."""

from typing import List, Optional
from pathlib import Path
import aiofiles
from ..session_tools import SessionManager


async def list_files(file_type: str, project: Optional[str] = None) -> List[str]:
    """List available files (guides, languages, etc.)."""
    session = SessionManager()
    if project is None:
        project = await session.get_current_project_safe()

    config = await session.session_state.get_project_config(project)

    # Map file types to config keys - only docroot remains
    type_mapping = {"docs": "docroot"}

    dir_key = type_mapping.get(file_type, file_type)
    dir_path = config.get(dir_key, "./")

    try:
        path = Path(dir_path)
        if path.is_dir():
            return [f.name for f in path.iterdir() if f.is_file()]
        else:
            return []
    except Exception:
        return []


def file_exists(path: str, project: Optional[str] = None) -> bool:
    """Check if a file exists."""
    try:
        return Path(path).exists()
    except Exception:
        return False


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
    "list_files",
    "file_exists",
    "get_file_content",
]
