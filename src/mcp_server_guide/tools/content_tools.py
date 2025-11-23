"""Content retrieval tools."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..document_cache import CategoryDocumentCache
from ..logging_config import get_logger
from .category_tools import get_category_content
from .collection_tools import get_collection_document


async def get_content(category_or_collection: str, document: str, project: Optional[str] = None) -> Optional[str]:
    """Get content for a specific document in a category or collection with caching."""
    # Check cache first for category
    cache_entry = await CategoryDocumentCache.get(category_or_collection, document)
    if cache_entry is not None:
        if not cache_entry.exists:
            return None

    category_error: Optional[Exception] = None

    # Try category first
    try:
        result = await get_category_content(category_or_collection)
        if result.get("success") and result.get("content"):
            content = str(result["content"])
            matched_files = result.get("matched_files", [])
            document_content = _extract_document_from_content(content, document)

            if document_content is not None:
                await CategoryDocumentCache.set(category_or_collection, document, True, matched_files)
                return document_content
            else:
                await CategoryDocumentCache.set(category_or_collection, document, False, None)
                return None
    except Exception as e:
        # Log exception for debugging
        logger = get_logger(__name__)
        logger.error(f"Category content retrieval failed: {e}", exc_info=True)
        category_error = e

    # Try collection if category failed
    try:
        result = await get_collection_document(category_or_collection, document, project)
        if result.get("success") and result.get("content"):
            return str(result["content"])
        else:
            # Cache failed collection document lookup
            await CategoryDocumentCache.set(category_or_collection, document, False, None)
    except Exception as ce:
        # Log exception for debugging
        logger = get_logger(__name__)
        if category_error:
            logger.critical(
                f"Both category and collection content retrieval raised exceptions for '{category_or_collection}': "
                f"category error: {category_error}, collection error: {ce}",
                exc_info=True,
            )
        else:
            logger.error(f"Collection content retrieval failed: {ce}", exc_info=True)
        # Cache exception as failed lookup
        await CategoryDocumentCache.set(category_or_collection, document, False, None)

    return None


async def get_guide(category_or_collection: str, document: str, project: Optional[str] = None) -> Optional[str]:
    """Get guide content for a specific document in a category or collection.

    This is an alias for get_content() to provide a more intuitive API for guide retrieval.
    """
    return await get_content(category_or_collection, document, project)


def _extract_document_from_content(content: str, document: str) -> Optional[str]:
    """Extract a specific document from combined category content.

    Matches document headers in format: # filename
    Supports exact match, with extension (.md), or base name matching.
    Handles edge cases with unusual headers and alternative formats.
    """
    if not content.strip():
        return None

    # Robust header detection - handle various markdown header formats
    # Match: # filename, ## filename, ### filename at start of line
    header_pattern = r"^(#{1,6})\s+(.+?)(?:\s*\{[^}]*\})?\s*$"

    sections = []
    current_section: list[str] = []
    current_header = None

    for line in content.split("\n"):
        header_match = re.match(header_pattern, line.strip())
        if header_match:
            # Save previous section
            if current_header and current_section:
                sections.append((current_header, "\n".join(current_section)))
            # Start new section
            current_header = header_match.group(2).strip()
            current_section = []
        else:
            current_section.append(line)

    # Add final section
    if current_header and current_section:
        sections.append((current_header, "\n".join(current_section)))

    # Find matching section using extension fallback logic
    from ..utils.file_extensions import get_extension_candidates

    # Get candidates with extension fallback
    candidates = get_extension_candidates(document)

    for candidate in candidates:
        candidate_normalized = candidate.strip().lower()

        for filename, section_content in sections:
            filename_normalized = filename.strip().lower()
            filename_path = Path(filename_normalized)

            # Exact match, stem match, or document with extension match
            if (
                filename_normalized == candidate_normalized
                or filename_path.stem == candidate_normalized
                or (candidate_normalized + ".") in filename_normalized
            ):
                return section_content.strip()

    return None


async def search_content(query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across all categories for content matching the query.
    This is a read-only operation that finds and displays matching content without making changes."""
    from ..session_manager import SessionManager

    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    # Get all categories from project config instead of hardcoded list
    config = await session.get_or_create_project_config(project)
    categories = list(config.categories.keys())

    results = []
    for category in categories:
        result = await get_category_content(category)
        if result.get("success") and result.get("content"):
            content = result["content"]
            if query.lower() in content.lower():
                results.append(
                    {
                        "category": category,
                        "content": content,
                        "matched_files": result.get("matched_files", []),
                        "search_dir": result.get("search_dir", ""),
                    }
                )

    return results


__all__ = [
    "get_content",
    "search_content",
]
