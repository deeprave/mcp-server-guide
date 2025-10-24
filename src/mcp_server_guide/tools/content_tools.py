"""Content retrieval tools."""

from typing import Dict, Any, List, Optional
from ..session_manager import SessionManager
from ..document_cache import CategoryDocumentCache
from .category_tools import get_category_content


async def get_content(category: str, document: str, project: Optional[str] = None) -> Optional[str]:
    """Get content for a specific document in a category with caching."""
    # Check cache first
    cache_entry = await CategoryDocumentCache.get(category, document)
    if cache_entry is not None:
        if not cache_entry.exists:
            return None
        # For cached entries that exist, we still need to fetch the actual content
        # since we only cache metadata, not the full content

    # Fetch from category system
    try:
        result = await get_category_content(category, project)
        if result.get("success") and result.get("content"):
            content = str(result["content"])  # Ensure content is str
            matched_files = result.get("matched_files", [])

            # Extract specific document from combined content
            document_content = _extract_document_from_content(content, document)

            if document_content is not None:
                # Cache the result as found
                await CategoryDocumentCache.set(category, document, True, matched_files)
                return document_content
            else:
                # Document not found in content
                await CategoryDocumentCache.set(category, document, False, None)
                return None
        else:
            # Cache the "not found" result
            await CategoryDocumentCache.set(category, document, False, None)
            return None
    except (FileNotFoundError, PermissionError, OSError) as e:
        # Cache the "not found" result on file system errors
        import logging

        logging.getLogger(__name__).warning(f"Failed to get content for {category}/{document}: {e}")
        await CategoryDocumentCache.set(category, document, False, None)
        return None


def _extract_document_from_content(content: str, document: str) -> Optional[str]:
    """Extract a specific document from combined category content.

    Matches document headers in format: # filename
    Supports exact match, with extension (.md), or base name matching.
    Handles edge cases with unusual headers and alternative formats.
    """
    if not content.strip():
        return None

    import re

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

    # Find matching section using normalized filename comparison
    from pathlib import Path

    # Normalize the document name for comparison
    document_normalized = document.strip().lower()

    for filename, section_content in sections:
        filename_normalized = filename.strip().lower()
        filename_path = Path(filename_normalized)

        # Exact match, stem match, or document with extension match
        if (
            filename_normalized == document_normalized
            or filename_path.stem == document_normalized
            or (document_normalized + ".") in filename_normalized
        ):
            return section_content.strip()

    return None


async def get_guide(project: Optional[str] = None) -> str:
    """Get project guidelines using unified category system."""
    result = await get_category_content("guide", project)
    return result.get("content", "") if result.get("success") else ""


async def get_language_guide(project: Optional[str] = None) -> str:
    """Get language-specific guidelines using unified category system."""
    result = await get_category_content("lang", project)
    return result.get("content", "") if result.get("success") else ""


async def get_project_context(project: Optional[str] = None) -> str:
    """Get project context using unified category system."""
    result = await get_category_content("context", project)
    return result.get("content", "") if result.get("success") else ""


async def get_all_guides(project: Optional[str] = None) -> Dict[str, str]:
    """Get all guide content using unified category system."""
    result = {}
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    # Get project config to find categories with auto_load: true
    config = await session.get_or_create_project_config(project)
    categories = config.categories

    # Filter categories with auto_load: true
    auto_load_categories = [name for name, category_config in categories.items() if category_config.auto_load or False]

    # Load content for each auto_load category
    for category_name in auto_load_categories:
        try:
            category_result = await get_category_content(category_name, project)
            if category_result.get("success"):
                result[category_name] = category_result.get("content", "")
            else:
                result[category_name] = f"Error: {category_result.get('error', 'Unknown error')}"
        except Exception as e:
            result[category_name] = f"Error: {str(e)}"

    return result


async def search_content(query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across all categories for content matching query."""
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    results = []
    categories = ["guide", "lang", "context"]

    for category in categories:
        result = await get_category_content(category, project)
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


async def show_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display guide to user."""
    content = await get_guide(project)
    return {"success": True, "content": content, "message": f"Guide content for project {project or 'current'}"}


async def show_language_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display language guide to user."""
    content = await get_language_guide(project)
    return {
        "success": True,
        "content": content,
        "message": f"Language guide content for project {project or 'current'}",
    }


async def show_project_summary(project: Optional[str] = None) -> Dict[str, Any]:
    """Display project overview to user."""
    all_content = await get_all_guides(project)
    return {"success": True, "content": all_content, "message": f"Project summary for {project or 'current'}"}


__all__ = [
    "get_content",
    "get_guide",
    "get_language_guide",
    "get_project_context",
    "get_all_guides",
    "search_content",
    "show_guide",
    "show_language_guide",
    "show_project_summary",
]
