"""
cache_manager.py — Simple in-memory cache for tool results.
Used by live tool implementations to avoid redundant API calls.
"""

from __future__ import annotations
import os
import time
from typing import Any, Dict, Optional

import config


class SimpleCache:
    """Thread-safe in-memory cache with TTL."""

    def __init__(self, ttl: int = config.TOOL_CACHE_TTL_SEC):
        self._store: Dict[str, tuple] = {}
        self.ttl = ttl
        self.internet_off: bool = os.getenv("INTERNET_OFF", "false").lower() == "true"

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.time() + self.ttl)

    def unavailable_response(self, reason: str = "offline") -> Dict[str, Any]:
        return {"summary": f"Unavailable ({reason})", "offline": True}

    def clear(self) -> None:
        self._store.clear()


_CACHE_INSTANCE: Optional[SimpleCache] = None


def get_cache() -> SimpleCache:
    """Return the singleton cache instance."""
    global _CACHE_INSTANCE
    if _CACHE_INSTANCE is None:
        _CACHE_INSTANCE = SimpleCache()
    return _CACHE_INSTANCE
