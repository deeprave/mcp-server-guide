"""Content retrieval tools."""

from typing import Dict, Any, List, Optional
from ..session_tools import SessionManager
from .category_tools import get_category_content


def get_guide(project: Optional[str] = None) -> str:
    """Get project guidelines using unified category system."""
    result = get_category_content("guide", project)
    return result.get("content", "") if result.get("success") else ""


def get_language_guide(project: Optional[str] = None) -> str:
    """Get language-specific guidelines using unified category system."""
    result = get_category_content("lang", project)
    return result.get("content", "") if result.get("success") else ""


def get_project_context(project: Optional[str] = None) -> str:
    """Get project context using unified category system."""
    result = get_category_content("context", project)
    return result.get("content", "") if result.get("success") else ""


def get_all_guides(project: Optional[str] = None) -> Dict[str, str]:
    """Get all guide content using unified category system."""
    result = {}

    try:
        result["guide"] = get_guide(project)
    except Exception as e:
        result["guide"] = f"Error: {str(e)}"

    try:
        result["language_guide"] = get_language_guide(project)
    except Exception as e:
        result["language_guide"] = f"Error: {str(e)}"

    try:
        result["project_context"] = get_project_context(project)
    except Exception as e:
        result["project_context"] = f"Error: {str(e)}"

    return result


def search_content(query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across all categories for content matching query."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    results = []
    categories = ["guide", "lang", "context"]

    for category in categories:
        result = get_category_content(category, project)
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


def show_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display guide to user."""
    content = get_guide(project)
    return {"success": True, "content": content, "message": f"Guide content for project {project or 'current'}"}


def show_language_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display language guide to user."""
    content = get_language_guide(project)
    return {
        "success": True,
        "content": content,
        "message": f"Language guide content for project {project or 'current'}",
    }


def show_project_summary(project: Optional[str] = None) -> Dict[str, Any]:
    """Display project overview to user."""
    all_content = get_all_guides(project)
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
