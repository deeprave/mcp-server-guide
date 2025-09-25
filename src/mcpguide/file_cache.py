"""HTTP-aware file caching system (Issue 003 Phase 3)."""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class CacheEntry:
    """Cache entry with HTTP headers for validation."""
    content: str
    headers: Dict[str, str] = field(default_factory=dict)
    cached_at: float = field(default_factory=time.time)

    @property
    def last_modified(self) -> Optional[str]:
        """Get Last-Modified header."""
        return self.headers.get("last-modified")

    @property
    def etag(self) -> Optional[str]:
        """Get ETag header."""
        return self.headers.get("etag")

    @property
    def cache_control(self) -> Optional[str]:
        """Get Cache-Control header."""
        return self.headers.get("cache-control")

    def needs_validation(self) -> bool:
        """Check if cache entry needs validation."""
        # Check Cache-Control directives first
        if self.cache_control:
            if "no-cache" in self.cache_control:
                return True

            # Check max-age
            if "max-age=" in self.cache_control:
                try:
                    max_age_start = self.cache_control.find("max-age=") + 8
                    max_age_end = self.cache_control.find(",", max_age_start)
                    if max_age_end == -1:
                        max_age_end = len(self.cache_control)
                    max_age = int(self.cache_control[max_age_start:max_age_end].strip())

                    age = time.time() - self.cached_at
                    return age > max_age
                except (ValueError, IndexError):
                    pass

        # If we have Last-Modified or ETag, assume fresh for a short time
        if self.last_modified or self.etag:
            age = time.time() - self.cached_at
            return age > 300  # 5 minutes default freshness

        # If no cache headers, always validate
        return True


class FileCache:
    """HTTP-aware file cache."""

    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 100):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".mcpguide" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb

    def _generate_key(self, url: str) -> str:
        """Generate filesystem-safe cache key from URL."""
        # Use SHA256 hash for consistent, filesystem-safe keys
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[CacheEntry]:
        """Get cached entry for URL."""
        key = self._generate_key(url)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            return CacheEntry(
                content=data["content"],
                headers=data.get("headers", {}),
                cached_at=data.get("cached_at", time.time())
            )
        except (json.JSONDecodeError, KeyError, IOError):
            # Invalid cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None

    def put(self, url: str, content: str, headers: Optional[Dict[str, str]] = None) -> None:
        """Put content in cache with HTTP headers."""
        key = self._generate_key(url)
        cache_file = self.cache_dir / f"{key}.json"

        data = {
            "content": content,
            "headers": headers or {},
            "cached_at": time.time()
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            # Ignore cache write failures
            pass

    def clear(self) -> None:
        """Clear all cached entries."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
