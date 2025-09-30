"""Category management tools for custom document categories."""

from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import glob
from ..session_tools import SessionManager
from ..logging_config import get_logger
from ..validation import validate_category, ConfigValidationError

logger = get_logger(__name__)

# Built-in categories that cannot be removed or overwritten
BUILTIN_CATEGORIES = {"guide", "lang", "context"}

# Safety limits for glob operations
MAX_GLOB_DEPTH = 8
MAX_DOCUMENTS_PER_GLOB = 100


def _auto_save_session(session: SessionManager, config_filename: str = ".mcp-server-guide.config.json") -> None:
    """Auto-save session state with error handling."""
    try:
        session.save_to_file(config_filename)
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

                # Skip if already processed (deduplication)
                if match_path in seen_files:
                    continue

                # Check if it's a file (not directory)
                if not match_path.is_file():
                    continue

                # Symlink detection and circular prevention
                try:
                    resolved_path = match_path.resolve()
                    if resolved_path in seen_files:
                        logger.debug(f"Skipping potential circular symlink: {match_path}")
                        continue
                    seen_files.add(resolved_path)
                except (OSError, RuntimeError) as e:
                    logger.warning(f"Error resolving path {match_path}: {e}")
                    continue

                # Depth limit check for recursive patterns
                try:
                    relative_path = resolved_path.relative_to(search_dir.resolve())
                    depth = len(relative_path.parts) - 1  # Subtract 1 for the file itself
                    if depth > MAX_GLOB_DEPTH:
                        logger.debug(f"Skipping file beyond depth limit ({MAX_GLOB_DEPTH}): {resolved_path}")
                        continue
                except ValueError:
                    # File is outside search directory - skip
                    logger.debug(f"Skipping file outside search directory: {resolved_path}")
                    continue

                matched_files.append(resolved_path)

        except (OSError, RuntimeError) as e:
            logger.warning(f"Error during glob search for pattern '{pattern}': {e}")
            continue

        # If no matches found and pattern has no extension, try with .md
        if not matches_found and "." not in Path(pattern).name:
            md_pattern = f"{pattern}.md"
            md_pattern_path = search_dir / md_pattern

            try:
                for match_str in glob.iglob(str(md_pattern_path), recursive=True):
                    if len(matched_files) >= MAX_DOCUMENTS_PER_GLOB:
                        break

                    match_path = Path(match_str)

                    # Skip if already processed (deduplication)
                    if match_path in seen_files:
                        continue

                    # Check if it's a file (not directory)
                    if not match_path.is_file():
                        continue

                    # Symlink detection and circular prevention
                    try:
                        resolved_path = match_path.resolve()
                        if resolved_path in seen_files:
                            logger.debug(f"Skipping potential circular symlink: {match_path}")
                            continue
                        seen_files.add(resolved_path)
                    except (OSError, RuntimeError) as e:
                        logger.warning(f"Error resolving path {match_path}: {e}")
                        continue

                    # Depth limit check for recursive patterns
                    try:
                        relative_path = resolved_path.relative_to(search_dir.resolve())
                        depth = len(relative_path.parts) - 1
                        if depth > MAX_GLOB_DEPTH:
                            logger.debug(f"Skipping file beyond depth limit ({MAX_GLOB_DEPTH}): {resolved_path}")
                            continue
                    except ValueError:
                        # File is outside search directory - skip
                        logger.debug(f"Skipping file outside search directory: {resolved_path}")
                        continue

                    matched_files.append(resolved_path)

            except (OSError, RuntimeError) as e:
                logger.warning(f"Error during glob search for pattern '{md_pattern}': {e}")
                continue

    return matched_files


def add_category(
    name: str,
    dir: str,
    patterns: List[str],
    project: Optional[str] = None,
    description: str = "",
    auto_load: bool = False,
) -> Dict[str, Any]:
    """Add a new custom category."""
    if name in BUILTIN_CATEGORIES:
        return {
            "success": False,
            "error": f"Cannot add built-in category '{name}'. Built-in categories are: {', '.join(BUILTIN_CATEGORIES)}",
        }

    # Validate category data before adding
    category_data = {"dir": dir, "patterns": patterns, "description": description, "auto_load": auto_load}

    try:
        validate_category(name, category_data)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors}

    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Get current config
    config = session.session_state.get_project_config(project)

    # Initialize categories if not present
    if "categories" not in config:
        config["categories"] = {}

    # Check if category already exists
    if name in config["categories"]:
        return {"success": False, "error": f"Category '{name}' already exists. Use update_category to modify it."}

    # Add new category
    category_config: Dict[str, Any] = {"dir": dir, "patterns": patterns, "description": description}
    if auto_load:
        category_config["auto_load"] = auto_load
    config["categories"][name] = category_config

    # Save config
    session.session_state.set_project_config(project, "categories", config["categories"])

    # Auto-save session
    _auto_save_session(session)

    return {
        "success": True,
        "message": f"Added category '{name}' with directory '{dir}' and {len(patterns)} patterns",
        "category": {"name": name, "dir": dir, "patterns": patterns, "description": description},
    }


def remove_category(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Remove a custom category."""
    if name in BUILTIN_CATEGORIES:
        return {
            "success": False,
            "error": f"Cannot remove built-in category '{name}'. Built-in categories are: {', '.join(BUILTIN_CATEGORIES)}",
        }

    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Get current config
    config = session.session_state.get_project_config(project)

    # Check if categories exist
    if "categories" not in config or name not in config["categories"]:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    # Remove category
    removed_category = config["categories"].pop(name)

    # Save config
    session.session_state.set_project_config(project, "categories", config["categories"])

    # Auto-save session
    _auto_save_session(session)

    return {"success": True, "message": f"Removed category '{name}'", "removed_category": removed_category}


def update_category(
    name: str,
    dir: str,
    patterns: List[str],
    project: Optional[str] = None,
    description: str = "",
    auto_load: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an existing category (built-in or custom)."""

    # Validate category data before updating
    category_data: Dict[str, Any] = {"dir": dir, "patterns": patterns, "description": description}
    if auto_load is not None:
        category_data["auto_load"] = auto_load

    try:
        validate_category(name, category_data)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors}

    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Get current config
    config = session.session_state.get_project_config(project)

    # Initialize categories if not present
    if "categories" not in config:
        config["categories"] = {}

    # Check if category exists
    if name not in config["categories"]:
        return {"success": False, "error": f"Category '{name}' does not exist. Use add_category to create it."}

    # Update category
    old_category = config["categories"][name].copy()
    updated_category: Dict[str, Any] = {"dir": dir, "patterns": patterns, "description": description}

    # Handle auto_load field
    if auto_load is not None:
        if auto_load:
            updated_category["auto_load"] = auto_load
        # If auto_load is False, we don't store it (missing = False)
    else:
        # Preserve existing auto_load setting if not specified
        if old_category.get("auto_load", False):
            updated_category["auto_load"] = True

    config["categories"][name] = updated_category

    # Save config
    session.session_state.set_project_config(project, "categories", config["categories"])

    # Auto-save session
    _auto_save_session(session)

    return {
        "success": True,
        "message": f"Updated category '{name}'",
        "old_category": old_category,
        "new_category": {"name": name, "dir": dir, "patterns": patterns, "description": description},
    }


def list_categories(project: Optional[str] = None) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Get current config
    config = session.session_state.get_project_config(project)

    categories = config.get("categories", {})

    builtin_categories = []
    custom_categories = []

    for name, category_config in categories.items():
        category_info = {
            "name": name,
            "dir": category_config.get("dir", ""),
            "patterns": category_config.get("patterns", []),
            "description": category_config.get("description", ""),
        }

        if name in BUILTIN_CATEGORIES:
            builtin_categories.append(category_info)
        else:
            custom_categories.append(category_info)

    return {
        "project": project,
        "builtin_categories": builtin_categories,
        "custom_categories": custom_categories,
        "total_categories": len(categories),
    }


def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

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
            content = file_path.read_text(encoding="utf-8")
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

    # Combine all content
    combined_content = "\n\n---\n\n".join(content_parts)

    return {
        "success": True,
        "content": combined_content,
        "matched_files": [str(f) for f in matched_files],
        "patterns": patterns,
        "search_dir": str(search_dir),
    }


__all__ = [
    "add_category",
    "remove_category",
    "update_category",
    "list_categories",
    "get_category_content",
    "BUILTIN_CATEGORIES",
]
