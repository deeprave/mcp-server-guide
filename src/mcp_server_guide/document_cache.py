"""Universal category document cache system."""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DocumentCacheEntry:
    """Cache entry for document metadata."""

    exists: bool
    matched: Optional[List[str]]  # None for non-existent, List for glob matches


class CategoryDocumentCache:
    """Universal document metadata cache for all categories."""

    _cache: Dict[str, Dict[str, DocumentCacheEntry]] = {}
    _lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def get(cls, category: str, document: str) -> Optional[DocumentCacheEntry]:
        """Get cached document entry."""
        async with cls._lock:
            return cls._cache.get(category, {}).get(document)

    @classmethod
    async def set(cls, category: str, document: str, exists: bool, matched: Optional[List[str]]) -> None:
        """Set cached document entry."""
        async with cls._lock:
            if category not in cls._cache:
                cls._cache[category] = {}
            cls._cache[category][document] = DocumentCacheEntry(exists, matched)

    @classmethod
    async def invalidate_category(cls, category: str) -> None:
        """Invalidate all cache entries for a category."""
        async with cls._lock:
            cls._cache.pop(category, None)

    @classmethod
    async def clear_all(cls) -> None:
        """Clear all cache entries."""
        async with cls._lock:
            cls._cache.clear()
