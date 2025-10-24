"""Category management tools for custom document categories."""

from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import glob
import re
import aiofiles
from ..project_config import Category
from ..session_manager import SessionManager
from ..document_cache import CategoryDocumentCache
from ..logging_config import get_logger


logger = get_logger()

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


async def _auto_save_session(session: SessionManager) -> None:
    """Auto-save session state with error handling."""
    try:
        await session.save_session()
        logger.debug("Auto-saved session")
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

    # Provide default description if empty
    if not description.strip():
        description = f"Custom category: {name}"

    # Create and validate category using Pydantic model
    try:
        category = Category(
            url=None,
            dir=dir,
            patterns=patterns,
            description=description,
            auto_load=auto_load,
        )
    except ValueError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}

    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    # Get current config
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    if name in categories:
        return {"success": False, "error": f"Category '{name}' already exists"}

    # Add the new category (keep as Category object)
    categories[name] = category

    # Update session
    session.session_state.set_project_config("categories", categories)

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' added successfully",
        "category": {**category.model_dump(), "name": name},
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

    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    # Get current config
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    # Preserve existing auto_load setting if not explicitly provided
    existing_category = categories[name]
    if auto_load is None:
        # Category is always a Pydantic model
        auto_load = existing_category.auto_load if existing_category.auto_load is not None else False

    # Provide default description if empty
    if not description.strip():
        # Category is always a Pydantic model
        existing_description = existing_category.description

        if existing_description.strip():
            description = existing_description
        else:
            description = f"Custom category: {name}"

    # Create and validate category using Pydantic model
    try:
        category = Category(
            url=None,
            dir=dir,
            patterns=patterns,
            description=description,
            auto_load=auto_load,
        )
    except ValueError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}

    # Update the category (keep as Category object)
    categories[name] = category

    # Invalidate cache for this category before updating session
    await CategoryDocumentCache.invalidate_category(name)

    # Update session
    session.session_state.set_project_config("categories", categories)

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' updated successfully",
        "category": category.model_dump(),
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

    # Use current session config directly instead of loading from disk
    config = session.session_state.project_config

    if name not in config.categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    # Store the removed category for return
    removed_category = config.categories[name]

    # Create new categories dict without the removed category
    new_categories = {k: v for k, v in config.categories.items() if k != name}

    # Create new ProjectConfig preserving all existing fields
    updated_config = config.model_copy(update={"categories": new_categories})

    # Invalidate cache for this category before updating session
    await CategoryDocumentCache.invalidate_category(name)

    # Update session state with the new config
    session.session_state.project_config = updated_config

    # Auto-save
    await _auto_save_session(session)

    return {
        "success": True,
        "message": f"Category '{name}' removed successfully",
        "removed_category": removed_category,
        "project": project,
    }


async def list_categories(project: Optional[str] = None) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    config = await session.get_or_create_project_config(project)
    categories = config.categories

    # Convert Category objects to dicts for API response
    categories_dict = {name: cat.model_dump() for name, cat in categories.items()}

    return {
        "success": True,
        "project": project,
        "categories": categories_dict,
        "total_categories": len(categories),
    }


async def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns or HTTP URL."""
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    # Get current config - use get_or_create_project_config for consistency
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    category = categories[name]

    # Check if this is a URL-based category (Category is always a Pydantic model)
    if category.url:
        # Return URL information for HTTP-based categories
        return {
            "success": True,
            "content": "",  # Content will be fetched by HTTP client
            "url": category.url,
            "is_http": True,
            "category_name": name,
        }

    # Handle file-based categories (Category is always a Pydantic model)
    category_dir = category.dir
    patterns = category.patterns

    if not category_dir:
        return {"success": False, "error": f"Category '{name}' has no directory specified"}

    if not patterns:
        return {"success": False, "error": f"Category '{name}' has no patterns defined"}

    # Get docroot from session manager's config manager
    docroot = session.config_manager().docroot
    base_path = docroot.resolve_sync() if docroot else Path(".")
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
