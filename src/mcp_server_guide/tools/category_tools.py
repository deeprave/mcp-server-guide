"""Category management tools for custom document categories."""

from typing import Dict, Any, List, Optional, Set, TYPE_CHECKING
from pathlib import Path
import glob
import re
import aiofiles
from ..models.category import Category
from ..document_cache import CategoryDocumentCache
from ..logging_config import get_logger
from ..constants import METADATA_SUFFIX
from ..utils.document_discovery import get_category_documents_by_path

if TYPE_CHECKING:
    from ..session_manager import SessionManager


logger = get_logger()

# Safety limits for glob operations
MAX_GLOB_DEPTH = 8
MAX_DOCUMENTS_PER_GLOB = 100

# Category name validation pattern
CATEGORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_category_name(name: str) -> bool:
    """Validate category name against allowed pattern."""
    return bool(name and CATEGORY_NAME_PATTERN.match(name))


async def _auto_save_session(session: "SessionManager") -> None:
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

                    # Exclude metadata files from pattern matching
                    if resolved_path.name.endswith(METADATA_SUFFIX):
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
                        # Exclude metadata files from pattern matching
                        if not match_path.name.endswith(METADATA_SUFFIX):
                            matched_files.append(match_path)
                            seen_files.add(match_path)

            except Exception as e:
                logger.warning(f"Glob pattern '{md_pattern}' failed: {e}")
                continue

    return matched_files


def _get_combined_category_files(category_dir: Path, patterns: List[str]) -> List[Path]:
    """Get combined list of pattern files and managed documents with deduplication.

    Managed documents take precedence over pattern files when there are name conflicts.
    """
    # Get pattern files (excluding metadata files)
    pattern_files = _safe_glob_search(category_dir, patterns)

    # Get managed documents
    managed_docs = get_category_documents_by_path(category_dir)

    # Create a set of managed document names for deduplication
    managed_names = {doc.path.name for doc in managed_docs}

    # Filter out pattern files that conflict with managed documents
    deduplicated_pattern_files = [f for f in pattern_files if f.name not in managed_names]

    # Convert managed documents to Path objects
    managed_paths = [doc.path for doc in managed_docs]

    # Combine and return
    return deduplicated_pattern_files + managed_paths


async def add_category(
    name: str,
    dir: str,
    patterns: List[str],
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new custom category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    # Provide default description if description is None or empty
    if not description or not description.strip():
        description = f"Custom category: {name}"

    # Create and validate category using Pydantic model
    try:
        category = Category(
            url=None,
            dir=dir,
            patterns=patterns,
            description=description,
        )
    except ValueError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}

    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
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
    }


async def update_category(
    name: str,
    *,
    description: Optional[str] = None,
    dir: Optional[str] = None,
    patterns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Update an existing category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    if name not in categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    existing_category = categories[name]

    # Handle description with proper defaults
    if description is None:
        # None means do not update, keep existing
        final_description = existing_category.description
    elif description == "":
        # Empty string means explicitly clear the description
        final_description = ""
    else:
        # Any other value is used as the new description
        final_description = description

    # If after all this, the description is still empty or None, use the default
    if final_description is None or final_description == "":
        final_description = f"Custom category: {name}"

    try:
        # Update only specified fields, preserving unknown fields using model_copy
        category = existing_category.model_copy(
            update={
                "dir": dir if dir is not None else existing_category.dir,
                "patterns": patterns if patterns is not None else existing_category.patterns,
                "description": final_description,
            }
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
    }


async def remove_category(name: str) -> Dict[str, Any]:
    """Remove a custom category."""
    # Validate category name
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    from ..session_manager import SessionManager

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
    }


async def list_categories(verbose: bool = False) -> Dict[str, Any]:
    """List all categories (built-in and custom)."""
    from ..session_manager import SessionManager

    session = SessionManager()

    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    categories_data = {}
    for name, category in categories.items():
        category_info: Dict[str, Any] = {"description": category.description}

        if verbose:
            category_info.update({"dir": category.dir, "patterns": category.patterns, "url": category.url})

        categories_data[name] = category_info

    return {"success": True, "categories": categories_data}


async def add_to_category(name: str, patterns: List[str]) -> Dict[str, Any]:
    """Add patterns to existing category."""
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    from ..session_manager import SessionManager

    session = SessionManager()
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    if name not in config.categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    existing_category = config.categories[name]

    # Add new patterns to existing ones, deduplicating while preserving order.
    # By default, deduplication is case-sensitive to align with file system behavior.
    # On case-insensitive file systems, this may cause duplicate matches.
    case_insensitive_deduplication = False  # Could be made configurable in future

    all_patterns = (existing_category.patterns or []) + patterns
    seen = set()
    updated_patterns = []
    for pat in all_patterns:
        key = pat.lower() if case_insensitive_deduplication else pat
        if key not in seen:
            seen.add(key)
            updated_patterns.append(pat)

    try:
        # Create updated category
        updated_category = Category(
            url=existing_category.url,
            dir=existing_category.dir,
            patterns=updated_patterns,
            description=existing_category.description,
        )

        # Update the category
        config.categories[name] = updated_category

        # Invalidate cache for this category before updating session
        await CategoryDocumentCache.invalidate_category(name)

        # Update session
        session.session_state.set_project_config("categories", config.categories)

        # Auto-save
        await _auto_save_session(session)

        return {
            "success": True,
            "message": f"Patterns added to category '{name}' successfully",
            "category": updated_category.model_dump(),
        }

    except ValueError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}


async def remove_from_category(name: str, patterns: List[str]) -> Dict[str, Any]:
    """Remove patterns from category."""
    if not _validate_category_name(name):
        return {"success": False, "error": "Invalid category name. Must match pattern [A-Za-z0-9_-]+"}

    from ..session_manager import SessionManager

    session = SessionManager()
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    if name not in config.categories:
        return {"success": False, "error": f"Category '{name}' does not exist"}

    existing_category = config.categories[name]
    current_patterns = existing_category.patterns or []

    # Aggregate patterns not found in category (case-sensitive matching)
    # Note: Pattern removal is case-sensitive to align with file system behavior
    # This means '*.py' and '*.PY' are treated as different patterns
    not_found_patterns = [pattern for pattern in patterns if pattern not in current_patterns]

    # Remove only patterns that exist in current_patterns (case-sensitive matching)
    patterns_to_remove = [pattern for pattern in patterns if pattern in current_patterns]
    updated_patterns = [p for p in current_patterns if p not in patterns_to_remove]

    # Check if category would be empty
    if not updated_patterns and not existing_category.url:
        return {
            "success": False,
            "error": f"Cannot remove all patterns from file-based category '{name}'. Use remove_category to delete it.",
            "not_found_patterns": not_found_patterns if not_found_patterns else None,
        }

    try:
        # Create updated category
        updated_category = Category(
            url=existing_category.url,
            dir=existing_category.dir,
            patterns=updated_patterns if updated_patterns else None,
            description=existing_category.description,
        )

        # Update the category
        config.categories[name] = updated_category

        # Invalidate cache for this category before updating session
        await CategoryDocumentCache.invalidate_category(name)

        # Update session
        session.session_state.set_project_config("categories", config.categories)

        # Auto-save
        await _auto_save_session(session)

        result = {
            "success": True,
            "message": f"Patterns removed from category '{name}' successfully",
            "category": updated_category.model_dump(),
        }

        # If some patterns were not found, report them but do not fail the operation
        if not_found_patterns:
            result["not_found_patterns"] = not_found_patterns

        return result

    except ValueError as e:
        return {"success": False, "error": f"Invalid category configuration: {e}"}


async def get_category_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get content from a category using glob patterns or HTTP URL."""
    from ..session_manager import SessionManager

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
]
