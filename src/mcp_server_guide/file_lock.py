"""File locking strategy for configuration updates."""

import os
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")
STALE_LOCK_SECONDS = 600  # 10 minutes


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def is_lock_stale(lock_file: Path, current_hostname: str) -> bool:
    """Check if lock file is stale."""
    try:
        # Check mtime first
        if time.time() - os.path.getmtime(lock_file) > STALE_LOCK_SECONDS:
            return True

        # Check hostname and pid
        with open(lock_file, "r") as lf:
            lock_info = lf.read().strip().split(":")

        if len(lock_info) >= 2:
            lock_hostname, lock_pid_str = lock_info[0], lock_info[1]
        elif len(lock_info) == 1:
            lock_hostname, lock_pid_str = "", lock_info[0]
        else:
            return True  # Invalid format, consider stale

        lock_pid = int(lock_pid_str) if lock_pid_str.isdigit() else None
        if lock_pid is None:
            return True

        # Stale if different hostname and process not running
        return lock_hostname != current_hostname and not is_process_running(lock_pid)

    except (OSError, ValueError):
        return True  # Error reading lock file, consider stale


def lock_update(file_path: Path, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Execute function with file locking to prevent concurrent updates."""
    pid = os.getpid()
    hostname = os.uname().nodename.split(".")[0]
    lock_file = file_path.with_suffix(f"{file_path.suffix}.lock")

    while True:
        # Attempt to create the lock file
        try:
            with open(lock_file, "x") as lockfile:
                lockfile.write(f"{hostname}:{pid}")
            break
        except FileExistsError:
            # Check if the lock is stale
            try:
                if is_lock_stale(lock_file, hostname):
                    lock_file.unlink(missing_ok=True)
                else:
                    time.sleep(1)
            except Exception:
                # If we can't read the lock file, treat as stale
                lock_file.unlink(missing_ok=True)

    try:
        return func(file_path, *args, **kwargs)
    finally:
        lock_file.unlink(missing_ok=True)
