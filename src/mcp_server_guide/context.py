"""Async context variables for session management."""

from contextvars import ContextVar
from typing import Optional

# Context variables for async session management
_current_project: ContextVar[Optional[str]] = ContextVar("current_project", default=None)
_session_id: ContextVar[Optional[str]] = ContextVar("session_id", default=None)


def get_current_project_context() -> Optional[str]:
    """Get current project from context variables."""
    return _current_project.get()


def set_current_project_context(project: str) -> None:
    """Set current project in context variables."""
    _current_project.set(project)


def get_session_id_context() -> Optional[str]:
    """Get session ID from context variables."""
    return _session_id.get()


def set_session_id_context(session_id: str) -> None:
    """Set session ID in context variables."""
    _session_id.set(session_id)


def clear_context() -> None:
    """Clear all context variables."""
    _current_project.set(None)
    _session_id.set(None)


__all__ = [
    "get_current_project_context",
    "set_current_project_context",
    "get_session_id_context",
    "set_session_id_context",
    "clear_context",
]
