"""Collection management tools for organizing categories."""

import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Literal
from ..models.collection import Collection
from ..logging_config import get_logger
from .category_tools import get_category_content

logger = get_logger()

# Collection name validation regex
# Collection names must start with a letter, can contain letters, numbers, underscores, or dashes,
# but must not end with a dash or underscore (single letters are allowed).
COLLECTION_NAME_REGEX = r"^[a-zA-Z](?:[\w-]*[a-zA-Z0-9])?$"


def is_valid_collection_name(name: str) -> bool:
    """Validate collection name using the standard regex."""
    return re.match(COLLECTION_NAME_REGEX, name) is not None


def _create_collection(
    categories: List[str],
    description: str,
    source_type: Literal["spec_kit", "user"],
    spec_kit_version: Optional[str] = None,
    existing_collection: Optional[Collection] = None,
) -> Collection:
    """Helper function to create a Collection with consistent metadata."""
    return Collection(
        categories=categories,
        description=description,
        source_type=source_type,
        spec_kit_version=spec_kit_version or None,
        created_date=existing_collection.created_date if existing_collection else datetime.now(timezone.utc),
        modified_date=datetime.now(timezone.utc),
    )


async def create_spec_kit_collection(
    name: str, categories: List[str], description: str = "", spec_kit_version: str = ""
) -> Dict[str, Any]:
    """Create a collection with spec_kit source_type and version."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Validate collection name
    if not name or not name.strip():
        return {"success": False, "error": "Collection name cannot be empty"}

    if len(name) > 30 or not is_valid_collection_name(name):
        return {
            "success": False,
            "error": (
                f"Invalid collection name '{name}'. "
                "Collection names must be at most 30 characters, start with a letter, "
                "and contain only letters, numbers, dash (-), and underscore (_)."
            ),
        }

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection already exists
    if name in config.collections:
        return {"success": False, "error": f"Collection '{name}' already exists"}

    # Validate categories
    if not categories:
        return {"success": False, "error": "Collection must have at least one category"}

    original_categories = list(categories)
    categories = [cat.strip() for cat in categories if cat is not None and cat.strip()]
    if len(categories) != len(original_categories):
        removed = [cat for cat in original_categories if cat is None or not cat.strip()]
        return {
            "success": False,
            "error": f"Collection categories contained empty or whitespace-only values: {removed}. Please provide only valid categories.",
        }

    # Check for duplicate category names (case-insensitive)
    normalized_for_check = [cat.lower() for cat in categories]
    if len(normalized_for_check) != len(set(normalized_for_check)):
        return {
            "success": False,
            "error": "Duplicate category names (case-insensitive) are not allowed in a collection",
        }

    # Validate all categories exist (case-sensitive lookup)
    for category_name in categories:
        if category_name not in config.categories:
            return {"success": False, "error": f"Category '{category_name}' does not exist"}

    try:
        # Create spec-kit collection with metadata
        collection = _create_collection(
            categories=categories,
            description=description,
            source_type="spec_kit",
            spec_kit_version=spec_kit_version,
        )

        # Add to config
        config.collections[name] = collection

        # Save config
        await session.save_session()

        return {
            "success": True,
            "message": f"Spec-kit collection '{name}' created successfully",
            "collection": collection.model_dump(),
        }

    except ValueError as e:
        return {"success": False, "error": f"Invalid collection configuration: {e}"}


async def add_collection(name: str, categories: List[str], description: Optional[str] = None) -> Dict[str, Any]:
    """Add a new collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Validate collection name
    if not name or not name.strip():
        return {"success": False, "error": "Collection name cannot be empty"}

    if len(name) > 30 or not is_valid_collection_name(name):
        return {
            "success": False,
            "error": (
                f"Invalid collection name '{name}'. "
                "Collection names must be at most 30 characters, start with a letter, "
                "and contain only letters, numbers, dash (-), and underscore (_)."
            ),
        }

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection already exists
    if name in config.collections:
        return {"success": False, "error": f"Collection '{name}' already exists"}

    # Validate categories is not None or empty
    if not categories:
        return {"success": False, "error": "Collection must have at least one category"}

    # Filter out None values from categories list and trim whitespace
    original_categories = list(categories)
    categories = [cat.strip() for cat in categories if cat is not None and cat.strip()]
    if len(categories) != len(original_categories):
        removed = [cat for cat in original_categories if cat is None or not cat.strip()]
        return {
            "success": False,
            "error": f"Collection categories contained empty or whitespace-only values: {removed}. Please provide only valid categories.",
        }

    # Check for duplicate category names (case-insensitive) while preserving original case
    normalized_for_check = [cat.lower() for cat in categories]
    if len(normalized_for_check) != len(set(normalized_for_check)):
        return {
            "success": False,
            "error": "Duplicate category names (case-insensitive) are not allowed in a collection",
        }

    # Validate all categories exist (case-sensitive lookup)
    for category_name in categories:
        if category_name not in config.categories:
            return {"success": False, "error": f"Category '{category_name}' does not exist"}

    try:
        # Create collection with metadata

        collection = _create_collection(
            categories=categories,
            description=description or "",
            source_type="user",  # Default for user-created collections
        )

        # Add to config
        config.collections[name] = collection

        # Save config
        await session.save_session()

        return {
            "success": True,
            "message": f"Collection '{name}' created successfully",
            "collection": collection.model_dump(),
        }

    except ValueError as e:
        return {"success": False, "error": f"Invalid collection configuration: {e}"}


async def update_collection(name: str, *, description: Optional[str] = None) -> Dict[str, Any]:
    """Update collection description."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    try:
        collection = config.collections[name]

        # Update description if provided
        if description is not None:
            # Update only the changed fields to preserve any future fields
            collection.description = description
            collection.modified_date = datetime.now(timezone.utc)
            config.collections[name] = collection

        # Save config
        await session.save_session()

        return {
            "success": True,
            "message": f"Collection '{name}' updated successfully",
            "collection": collection.model_dump(),
        }

    except ValueError as e:
        return {"success": False, "error": f"Invalid collection configuration: {e}"}


async def add_to_collection(name: str, categories: List[str]) -> Dict[str, Any]:
    """Add categories to existing collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    # Validate categories list is not empty
    if not categories:
        return {"success": False, "error": "Cannot add empty categories list to collection"}

    # Validate all categories exist (case-sensitive lookup)
    for category_name in categories:
        if category_name not in config.categories:
            return {"success": False, "error": f"Category '{category_name}' does not exist"}

    collection = config.collections[name]

    # Prepare for case-insensitive duplicate check
    # Note: Categories are stored with original case but checked case-insensitively
    # This means 'Foo' and 'foo' are treated as duplicates, preventing confusion
    collection_categories_lower = [cat.lower() for cat in collection.categories]
    added = []
    skipped = []
    for category_name in categories:
        if category_name.lower() in collection_categories_lower:
            # Clarify in skipped message that check is case-insensitive
            skipped.append(f"{category_name} (skipped: case-insensitive duplicate)")
        else:
            collection.categories.append(category_name)
            added.append(category_name)

    if not added:
        return {
            "success": False,
            "error": f"All categories already exist in collection '{name}': {skipped}",
            "skipped": skipped,
        }

    try:
        # Update collection with added categories and new modified_date
        updated_categories = list(collection.categories) + added
        config.collections[name] = collection.model_copy(
            update={
                "categories": updated_categories,
                "modified_date": datetime.now(timezone.utc),
            }
        )

        # Save config
        await session.save_session()

        result = {
            "success": True,
            "message": f"Added {len(added)} categories to collection '{name}'",
            "collection": config.collections[name].model_dump(),
            "added": added,
        }
        if skipped:
            result["skipped"] = skipped
            result["message"] = str(result["message"]) + f" (skipped {len(skipped)} existing)"
        return result

    except ValueError as e:
        return {"success": False, "error": f"Invalid collection configuration: {e}"}


async def remove_from_collection(name: str, categories: List[str]) -> Dict[str, Any]:
    """Remove categories from collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    # Validate categories list is not empty
    if not categories:
        return {"success": False, "error": "Cannot remove empty categories list from collection"}

    collection = config.collections[name]

    # Prepare lowercased sets for case-insensitive comparison
    collection_categories_lower = {cat.lower(): cat for cat in collection.categories}
    categories_lower = [cat.lower() for cat in categories]

    # Determine which categories are missing (case-insensitive)
    missing_categories = [
        category_name
        for category_name, category_name_lower in zip(categories, categories_lower)
        if category_name_lower not in collection_categories_lower
    ]

    present_categories_lower = [
        category_name_lower
        for category_name, category_name_lower in zip(categories, categories_lower)
        if category_name_lower in collection_categories_lower
    ]

    if not present_categories_lower:
        return {
            "success": False,
            "error": f"None of the specified categories exist in collection '{name}': {missing_categories}",
            "missing": missing_categories,
        }

    try:
        # Check for ambiguous removals: categories that differ only by case
        ambiguous_removals = {}
        for remove_cat in present_categories_lower:
            matches = [cat for cat in collection.categories if cat.lower() == remove_cat]
            if len(matches) > 1:
                ambiguous_removals[remove_cat] = matches

        if ambiguous_removals:
            return {
                "success": False,
                "error": (
                    "Ambiguous removal: multiple categories in the collection differ only by case for the following names: "
                    + ", ".join(f"'{name}': {matches}" for name, matches in ambiguous_removals.items())
                    + ". Please specify the exact category name(s) to remove."
                ),
                "ambiguous": ambiguous_removals,
            }

        # Remove categories using exact matching to avoid unintended removals
        # Map requested categories to their exact matches in the collection
        exact_categories_to_remove = []
        for requested_cat in categories:
            # Find exact match first
            if requested_cat in collection.categories:
                exact_categories_to_remove.append(requested_cat)
            else:
                # Fall back to case-insensitive match (only one match guaranteed by ambiguity check above)
                for existing_cat in collection.categories:
                    if existing_cat.lower() == requested_cat.lower():
                        exact_categories_to_remove.append(existing_cat)
                        break

        updated_categories = [cat for cat in collection.categories if cat not in exact_categories_to_remove]

        # Check if collection would be empty
        if not updated_categories:
            return {
                "success": False,
                "error": (
                    f"Cannot remove all categories from collection '{name}'. "
                    f"To remove the entire collection, use the 'remove_collection' command or method."
                ),
            }

        # Re-instantiate the Collection object to ensure validation is applied
        config.collections[name] = collection.model_copy(
            update={
                "categories": updated_categories,
                "modified_date": datetime.now(timezone.utc),
            }
        )

        # Save config
        await session.save_session()

        result = {
            "success": True,
            "message": f"Removed {len(present_categories_lower)} categories from collection '{name}'",
            "collection": config.collections[name].model_dump(),
            "removed": [collection_categories_lower[cat] for cat in present_categories_lower],
        }
        if missing_categories:
            result["missing"] = missing_categories
            result["message"] = str(result["message"]) + f" ({len(missing_categories)} not found)"
        return result

    except ValueError as e:
        return {"success": False, "error": f"Invalid collection configuration: {e}"}


async def remove_collection(name: str) -> Dict[str, Any]:
    """Remove a collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    # Store removed collection for return
    removed_collection = config.collections[name]

    # Remove collection
    del config.collections[name]

    # Save config
    await session.save_session()

    return {
        "success": True,
        "message": f"Collection '{name}' removed successfully",
        "removed_collection": removed_collection.model_dump(),
    }


async def list_collections(verbose: bool = False) -> Dict[str, Any]:
    """List all collections."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    if not config.collections:
        return {"success": True, "collections": {}, "message": "No collections found"}

    collections_data = {}

    for name, collection in config.collections.items():
        collection_info: Dict[str, Any] = {
            "categories": collection.categories,
            "description": collection.description,
            "source_type": collection.source_type,
            "created_date": collection.created_date.isoformat(),
            "modified_date": collection.modified_date.isoformat(),
        }

        # Add spec_kit_version if present
        if collection.spec_kit_version:
            collection_info["spec_kit_version"] = collection.spec_kit_version

        if verbose:
            # Add category details
            category_details: Dict[str, Dict[str, Any]] = {}
            for cat_name in collection.categories:
                if cat_name in config.categories:
                    cat = config.categories[cat_name]
                    category_details[cat_name] = {
                        "dir": cat.dir,
                        "patterns": cat.patterns,
                        "url": cat.url,
                        "description": cat.description,
                    }
            collection_info["category_details"] = category_details

        collections_data[name] = collection_info

    return {"success": True, "collections": collections_data}


async def get_collection_content(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get aggregated content from all categories in a collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    collection = config.collections[name]
    content_parts = []

    # Deduplicate category names while preserving order
    deduped_categories = list(dict.fromkeys(collection.categories))

    # Aggregate content from all categories in collection, adding section headers
    for category_name in deduped_categories:
        content_parts.append(f"\n=== Category: {category_name} ===\n")
        try:
            result = await get_category_content(category_name, project)
            if result.get("success") and result.get("content"):
                content_parts.append(f"# Collection: {name} - Category: {category_name}\n\n{result['content']}")
            elif not result.get("success"):
                content_parts.append(
                    f"# Collection: {name} - Category: {category_name}\n\nError: {result.get('error', 'Unknown error')}"
                )
        except Exception as e:
            content_parts.append(f"# Collection: {name} - Category: {category_name}\n\nError: {str(e)}")

    if not content_parts:
        return {
            "success": True,
            "content": "",
            "message": f"No content found in collection '{name}'",
            "categories": collection.categories,
        }

    combined_content = "\n\n".join(content_parts)

    return {"success": True, "content": combined_content, "categories": collection.categories, "collection_name": name}


async def get_collection_listing(name: str, project: Optional[str] = None) -> Dict[str, Any]:
    """Get directory listing of all documents in a collection."""
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    collection = config.collections[name]
    all_files = []

    # Get file listings from all categories in collection
    for category_name in collection.categories:
        try:
            result = await get_category_content(category_name, project)
            if result.get("success") and result.get("matched_files"):
                category_files = {"category": category_name, "files": result["matched_files"]}
                all_files.append(category_files)
        except Exception as e:
            logger.warning(f"Error getting files from category '{category_name}': {e}")

    return {
        "success": True,
        "collection_name": name,
        "categories": collection.categories,
        "files_by_category": all_files,
    }


async def get_collection_document(
    name: str, document: str, project: Optional[str] = None, partial_match: bool = False
) -> Dict[str, Any]:
    """Search for a specific document across all categories in a collection.

    Args:
        name: Collection name
        document: Document name to search for
        project: Project name (optional)
        partial_match: If True, allow partial filename matching (default: False)
    """
    from ..session_manager import SessionManager

    session = SessionManager()

    # Get current config
    project = session.get_project_name()
    config = await session.get_or_create_project_config(project)

    # Check if collection exists
    if name not in config.collections:
        return {"success": False, "error": f"Collection '{name}' does not exist"}

    collection = config.collections[name]

    # Search for document in each category
    matches_found = []

    for category_name in collection.categories:
        try:
            result = await get_category_content(category_name, project)
            if result.get("success") and result.get("matched_files"):
                # Check for filename matches (exact, with extensions, or containing the document name)
                for file_path in result["matched_files"]:
                    filename = os.path.basename(file_path)
                    # Exact match or with common extensions
                    match = (
                        filename == document
                        or filename == f"{document}.md"
                        or filename == f"{document}.txt"
                        or filename == f"{document}.rst"
                    )
                    # Optionally allow partial matches if partial_match is True
                    if partial_match and not match:
                        match = document in filename

                    if match:
                        matches_found.append((category_name, file_path))

        except Exception as e:
            logger.warning(f"Error searching category '{category_name}': {e}")
            continue

    # Handle multiple matches for both partial and exact matching
    if len(matches_found) > 1:
        match_type = "partial" if partial_match else "exact"
        return {
            "success": False,
            "error": f"Multiple files match '{document}' ({match_type} match): {[path for _, path in matches_found]}. Please specify the exact filename.",
            "collection_name": name,
        }

    # Process first match
    if matches_found:
        category_name, file_path = matches_found[0]
        try:
            result = await get_category_content(category_name, project)
            if result.get("success"):
                # Found the document, extract and return only its content
                from .content_tools import _extract_document_from_content

                document_content = _extract_document_from_content(result["content"], document)
                # If extraction fails, return error instead of exposing full content
                if document_content is None:
                    logger.warning(f"Could not extract specific document '{document}' from '{file_path}'")
                    return {
                        "success": False,
                        "error": f"Document '{document}' found but could not be extracted from '{file_path}'",
                        "found_in_category": category_name,
                        "collection_name": name,
                    }
                return {
                    "success": True,
                    "content": document_content,
                    "found_in_category": category_name,
                    "collection_name": name,
                    "document": document,
                    "file_path": file_path,
                }
        except Exception as e:
            logger.warning(f"Error searching category '{category_name}' for document '{document}': {e}")

    return {
        "success": False,
        "error": f"Document '{document}' not found in collection '{name}'",
        "searched_categories": collection.categories,
    }
