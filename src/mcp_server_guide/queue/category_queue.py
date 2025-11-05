"""Thread-safe category queue with supervised task management."""

import asyncio
import threading
from queue import Queue
from typing import Optional

from ..logging_config import get_logger

# Global queue state (simpler than ContextVar for this use case)
_category_queue: Optional[Queue[str]] = None
_supervisor_task: Optional[asyncio.Task[None]] = None
_lock = threading.Lock()

logger = get_logger(__name__)


def get_queue() -> Queue[str]:
    """Get or create the category queue."""
    global _category_queue
    if _category_queue is None:
        _category_queue = Queue()
    return _category_queue


def add_category(category_dir: str) -> None:
    """Add category to queue and ensure supervisor is running."""
    get_queue().put(category_dir)
    _ensure_supervisor_running()


def get_next_category() -> Optional[str]:
    """Get next category from queue (non-blocking)."""
    try:
        return get_queue().get_nowait()
    except Exception:
        return None


def _ensure_supervisor_running() -> None:
    """Start supervisor if not already running. TEMPORARILY DISABLED."""
    # Feature temporarily disabled to prevent RuntimeWarning
    pass


async def _run_supervisor() -> None:
    """Supervised task manager for category processing. TEMPORARILY DISABLED."""
    # Feature temporarily disabled to prevent RuntimeWarning
    pass


def is_supervisor_running() -> bool:
    """Check if supervisor task is currently running."""
    global _supervisor_task
    return _supervisor_task is not None and not _supervisor_task.done()


async def shutdown_supervisor() -> None:
    """Gracefully shutdown the supervisor task."""
    global _supervisor_task
    if _supervisor_task and not _supervisor_task.done():
        _supervisor_task.cancel()
        try:
            await _supervisor_task
        except asyncio.CancelledError:
            pass
        _supervisor_task = None
