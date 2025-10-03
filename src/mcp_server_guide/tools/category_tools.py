"""Category management tools for custom document categories."""

from ..naming import config_filename
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import glob
import re
import aiofiles
from ..session_tools import SessionManager
from ..logging_config import get_logger
from ..validation import validate_category, ConfigValidationError

logger = get_logger(__name__)

# Built-in categories that cannot be removed or overwritten
BUILTIN_CATEGORIES = {"guide", "lang", "context"}

# Safety limits for glob operations
MAX_GLOB_DEPTH = 8
MAX_DOCUMENTS_PER_GLOB = 100

# Category name validation pattern
CATEGORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_category_name(name: str) -> bool:
    """Validate category name against allowed pattern."""
    return bool(name and CATEGORY_NAME_PATTERN.match(name))


async def _auto_save_session(session: SessionManager, config_filename: str = config_filename()) -> None:
    """Auto-save session state with error handling."""
    try:
        await session.save_to_file(config_filename)
        logger.debug(f"Auto-saved session to {config_filename}")
    except Exception as e:
        logger.warning(f"Auto-save failed: {e}")
        # Don't raise - category operations should succeed even if save fails


def _safe_glob_search(search_dir: Path, patterns: List[str]) -> List[Path]:
    """Safely search for files using glob patterns with safety limits and smart .md extension."""
    matched_files: List[Path] = []
    seen_files: Set[Path] = set()

    for pattern in patterns:
        if len(matched_files) >= MAX_DOCUMENTS_PER_GLOB:
            logger.warning(f"Reached maximum document limit ({MAX_DOCUMENTS_PER_GLOB}) for glob search")
            break

        pattern_path = search_dir / pattern

        # Try original pattern first
        matches_found = False
        try:
            # Use iglob for memory efficiency
            for match_str in glob.iglob(str(pattern_path), recursive=True):
                matches_found = True
                if len(matched_files) >= MAX_DOCUMENTS_PER_GLOB:
                    break

                match_path = Path(match_str)
                if match_path.is_file():
                    # Resolve symlinks with error handling
                    try:
                        resolved_path = match_path.resolve()
                    except OSError as e:
                        logger.warning(f"Failed to resolve symlink {match_path}: {e}")
                        continue

                    # Check if we've already seen this resolved path
                    if resolved_path in seen_files:
                        continue

                    # Check depth limit
                    try:
                        relative_path = resolved_path.relative_to(search_dir.resolve())
                        depth = len(relative_path.parts) - 1  # Subtract 1 for the file itself
                        if depth <= MAX_GLOB_DEPTH:
                            matched_files.append(resolved_path)
                            seen_files.add(resolved_path)
                    except ValueError:
                        # Path is not relative to search_dir, skip it
                        logger.debug(f"Skipping file outside search directory: {resolved_path}")
                        continue

        except Exception as e:
            logger.warning(f"Glob pattern '{pattern}' failed: {e}")
            continue

        # If no matches and pattern doesn't end with .md, try adding .md
        if not matches_found and not pattern.endswith(".md"):
            md_pattern = f"{pattern}.md"
            md_pattern_path = search_dir / md_pattern
            try:
                for match_str in glob.iglob(str(md_pattern_path), recursive=True):
                    if len(matched_files) >= MAX_DOCUMENTS_PER_GLOB:
                        break

                    match_path = Path(match_str)
                    if match_path.is_file() and match_path not in seen_files:
                        matched_files.append(match_path)
                        seen_files.add(match_path)

            except Exception as e:
                logger.warning(f"Glob pattern '{md_pattern}' failed: {e}")
                continue

    return matched_files


async def add_category(
    name: str,
    dir: str,
    patterns: List[str],
    description: str = "",
    project: Optional[str] = None,
    auto_load: bool = False,
) -> Dict[str, Any]:
    """Add a new custom category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    if name in BUILTIN_CATEGORIES:
        return {"success": False, "error": f"Cannot override built-in category '{name}'"}

    # Validate category configuration
    category_config = {
        "dir": dir,
        "patterns": patterns,
        "description": description,
        "auto_load": auto_load,
    }

    try:
        validate_category(name, category_config)
    except ConfigValidationError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}

    session = SessionManager()
    if project is None:
        project = session.get_current_project_safe()

    # Get current config
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    if name in categories:
        return {"success": False, "error": f"Category '{name}' already exists"}

    # Add the new category
    categories[name] = category_config

    # Update session
    session.session_state.set_project_config(project, "categories", categories)

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' added successfully",
        "category": {**category_config, "name": name},
        "project": project,
    }


async def update_category(
    name: str,
    dir: str,
    patterns: List[str],
    description: str = "",
    project: Optional[str] = None,
    auto_load: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an existing category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    # Allow partial updates to builtin categories (dir, patterns, auto_load)
    # but prevent complete removal or name changes
    if name in BUILTIN_CATEGORIES:
        # Built-in categories can only be updated, not renamed or removed
        # This is handled by the function signature - name cannot be changed
        pass

    # Validate category configuration
    category_config = {
        "dir": dir,
        "patterns": patterns,
        "description": description,
        "auto_load": False,
    }

    # Handle auto_load - if not provided, preserve existing value
    auto_load_value: bool
    if auto_load is not None:
        auto_load_value = auto_load
        category_config["auto_load"] = auto_load_value

    try:
        validate_category(name, category_config)
    except ConfigValidationError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}

    session = SessionManager()
    if project is None:
        project = session.get_current_project_safe()

    # Get current config
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    # Preserve existing auto_load setting if not explicitly provided
    existing_category = categories[name]
    if auto_load is None:
        auto_load_value = existing_category.get("auto_load", False)
        category_config["auto_load"] = auto_load_value
    else:
        auto_load_value = auto_load
        category_config["auto_load"] = auto_load_value

    # Update the category
    categories[name] = category_config

    # Update session
    session.session_state.set_project_config(project, "categories", categories)

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' updated successfully",
        "category": category_config,
        "project": project,
    }


async def remove_category(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Remove a custom category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    if name in BUILTIN_CATEGORIES:
        return {"success": False, "error": f"Cannot remove built-in category '{name}'"}

    session = SessionManager()
    if project is None:
        project = session.get_current_project_safe()

    # Get current config
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    # Remove the category
    removed_category = categories.pop(name)

    # Update session
    session.session_state.set_project_config(project, "categories", categories)

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' removed successfully",
        "removed_category": removed_category,
        "project": project,
    }


def list_categories(project: Optional[str] = None) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project_safe()

    # Get current config
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    # Separate built-in and custom categories
    builtin = {name: categories.get(name, {}) for name in BUILTIN_CATEGORIES if name in categories}
    custom = {name: cat for name, cat in categories.items() if name not in BUILTIN_CATEGORIES}

    return {
        "success": True,
        "builtin_categories": builtin,
        "custom_categories": custom,
        "total_categories": len(categories),
        "project": project,
    }


async def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project_safe()

    # Get current config
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    category = categories[name]
    category_dir = category.get("dir", "")
    patterns = category.get("patterns", [])

    if not patterns:
        return {"success": False, "error": f"Category '{name}' has no patterns defined"}

    # Find matching files using safe glob search with resolved absolute paths
    docroot = config.get("docroot", ".")
    # Ensure docroot is absolute for reliable path resolution
    if not Path(docroot).is_absolute():
        docroot = str(Path(docroot).resolve())

    base_path = Path(docroot)
    search_dir = base_path / category_dir

    if not search_dir.exists():
        return {"success": False, "error": f"Category directory '{search_dir}' does not exist"}

    matched_files = _safe_glob_search(search_dir, patterns)
    content_parts = []

    for file_path in matched_files:
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
            content_parts.append(f"# {file_path.name}\n\n{content}")
        except Exception as e:
            content_parts.append(f"# {file_path.name}\n\nError reading file: {str(e)}")

    if not content_parts:
        return {
            "success": True,
            "content": "",
            "message": f"No files found matching patterns in category '{name}'",
            "matched_files": [],
            "patterns": patterns,
            "search_dir": str(search_dir),
        }

    combined_content = "\n\n".join(content_parts)
    matched_file_names = [str(f) for f in matched_files]

    return {
        "success": True,
        "content": combined_content,
        "matched_files": matched_file_names,
        "patterns": patterns,
        "search_dir": str(search_dir),
        "file_count": len(matched_files),
    }


__all__ = [
    "add_category",
    "update_category",
    "remove_category",
    "list_categories",
    "get_category_content",
    "BUILTIN_CATEGORIES",
]
