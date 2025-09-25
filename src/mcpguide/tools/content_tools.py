"""Content retrieval tools."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from ..session_tools import SessionManager


def get_guide(project: Optional[str] = None) -> str:
    """Get project guidelines for AI injection."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Use the server's hybrid file access to read guide
    try:
        from ..server import create_server

        server = create_server()
        return server.read_guide(project)
    except Exception as e:
        return f"Error reading guide for project {project}: {str(e)}"


def get_language_guide(project: Optional[str] = None) -> str:
    """Get language-specific guidelines for AI injection."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Use the server's hybrid file access to read language guide
    try:
        from ..server import create_server

        server = create_server()
        return server.read_language(project)
    except Exception as e:
        return f"Error reading language guide for project {project}: {str(e)}"


def get_project_context(project: Optional[str] = None) -> str:
    """Get project context document for AI injection."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Get project context from configuration
    config = session.session_state.get_project_config(project)
    context_path = config.get("projdir", "./aidocs/project/")

    # Try to read project context file
    try:
        if context_path.startswith(("http://", "https://")):
            # Use server's HTTP access
            from ..server import create_server

            server = create_server()
            from ..file_source import FileSource

            source = FileSource("http", context_path)
            return server.file_accessor.read_file("", source)
        else:
            # Read local file
            context_file = Path(context_path)
            if context_file.is_dir():
                # Look for common project files
                for filename in ["freeform.md", "context.md", "project.md", "README.md"]:
                    file_path = context_file / filename
                    if file_path.exists():
                        return file_path.read_text()
            elif context_file.exists():
                return context_file.read_text()

        return f"No project context found for {project}"
    except Exception as e:
        return f"Error reading project context for {project}: {str(e)}"


def get_all_guides(project: Optional[str] = None) -> Dict[str, str]:
    """Get all guide files for comprehensive AI context."""
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
    """Search across project content."""
    results = []
    guides = get_all_guides(project)

    for guide_type, content in guides.items():
        if query.lower() in content.lower():
            # Find matching lines
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    results.append(
                        {
                            "source": guide_type,
                            "line_number": i + 1,
                            "line": line.strip(),
                            "context": "\n".join(lines[max(0, i - 2) : i + 3]),
                        }
                    )

    return results


def show_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display guide to user."""
    content = get_guide(project)
    return {
        "type": "user_display",
        "title": f"Project Guide - {project or 'Current Project'}",
        "content": content,
        "format": "markdown",
    }


def show_language_guide(project: Optional[str] = None) -> Dict[str, Any]:
    """Display language guide to user."""
    content = get_language_guide(project)
    return {
        "type": "user_display",
        "title": f"Language Guide - {project or 'Current Project'}",
        "content": content,
        "format": "markdown",
    }


def show_project_summary(project: Optional[str] = None) -> Dict[str, Any]:
    """Display project overview to user."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    config = session.session_state.get_project_config(project)
    guides = get_all_guides(project)

    summary = f"# Project: {project}\n\n"
    summary += f"## Configuration\n"
    for key, value in config.items():
        summary += f"- **{key}**: {value}\n"

    summary += f"\n## Available Content\n"
    for guide_type, content in guides.items():
        if content and not content.startswith("Error"):
            summary += f"- **{guide_type}**: {len(content)} characters\n"

    return {"type": "user_display", "title": f"Project Summary - {project}", "content": summary, "format": "markdown"}


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
