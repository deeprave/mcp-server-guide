"""Content retrieval tools."""

from typing import Dict, Any, List, Optional
from ..session_tools import SessionManager
from .category_tools import get_category_content


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
        project = await session.get_current_project_safe()

    # Get project config to find categories with auto_load: true
    config = session.session_state.get_project_config(project)
    categories = config.get("categories", {})

    # Filter categories with auto_load: true
    auto_load_categories = [
        name for name, category_config in categories.items() if category_config.get("auto_load", False)
    ]

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
        project = await session.get_current_project_safe()

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
    "get_guide",
    "get_language_guide",
    "get_project_context",
    "get_all_guides",
    "search_content",
    "show_guide",
    "show_language_guide",
    "show_project_summary",
]
