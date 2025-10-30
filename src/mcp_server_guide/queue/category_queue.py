"""Thread-safe category queue with supervised task management."""

import asyncio
import logging
import threading
import time
from queue import Queue
from typing import Optional

_category_queue: Queue[str] = Queue()
_supervisor_task: Optional[asyncio.Task] = None
_lock = threading.Lock()

logger = logging.getLogger(__name__)


def add_category(category_dir: str) -> None:
    """Add category to queue and ensure supervisor is running."""
    _category_queue.put(category_dir)
    _ensure_supervisor_running()


def get_next_category() -> Optional[str]:
    """Get next category from queue (non-blocking)."""
    try:
        return _category_queue.get_nowait()
    except Exception:
        return None


def _ensure_supervisor_running() -> None:
    """Start supervisor if not already running."""
    global _supervisor_task
    with _lock:
        if _supervisor_task is None or _supervisor_task.done():
            try:
                loop = asyncio.get_event_loop()
                _supervisor_task = loop.create_task(_run_supervisor())
            except RuntimeError:
                # No event loop running, supervisor will start when loop is available
                pass


async def _run_supervisor() -> None:
    """Supervised task manager for category processing."""
    from ..services.external_sync import _cleanup_category_documents, _cleanup_expired_cache_entries

    last_cache_cleanup = 0.0
    CACHE_CLEANUP_INTERVAL = 300.0  # 5 minutes

    while True:
        current_time = time.time()

        # Process category queue
        category_dir = get_next_category()
        if category_dir:
            try:
                # Process category with proper exception handling
                await _cleanup_category_documents(category_dir)
                logger.debug(f"Successfully processed category: {category_dir}")
            except Exception as e:
                logger.error(f"Error processing category {category_dir}: {e}", exc_info=True)

        # Periodic cache cleanup (independent of queue processing)
        if current_time - last_cache_cleanup > CACHE_CLEANUP_INTERVAL:
            try:
                await _cleanup_expired_cache_entries()
                last_cache_cleanup = current_time
                logger.debug("Performed periodic cache cleanup")
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}", exc_info=True)

        # Brief pause
        await asyncio.sleep(0.1)


def is_supervisor_running() -> bool:
    """Check if supervisor task is currently running."""
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
