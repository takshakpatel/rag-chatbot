from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    answer: str
    sources: list[dict]
    query: str
    timestamp: float
    tokens_used: int = 0


class QueryCache:
    """Simple in-memory query cache with TTL.

    Key = hash(query + collection + k).
    """

    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 1000):
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self._cache: dict[str, CacheEntry] = {}

    def _make_key(self, query: str, collection: str, k: int) -> str:
        raw = f"{query.strip().lower()}|{collection}|{k}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, query: str, collection: str = "documents", k: int = 5) -> CacheEntry | None:
        key = self._make_key(query, collection, k)
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() - entry.timestamp > self.ttl:
            del self._cache[key]
            return None
        return entry

    def set(
        self,
        query: str,
        answer: str,
        sources: list[dict],
        collection: str = "documents",
        k: int = 5,
        tokens_used: int = 0,
    ) -> None:
        key = self._make_key(query, collection, k)
        if len(self._cache) >= self.max_entries:
            oldest_key = min(self._cache, key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest_key]

        self._cache[key] = CacheEntry(
            answer=answer,
            sources=sources,
            query=query,
            timestamp=time.time(),
            tokens_used=tokens_used,
        )

    def stats(self) -> dict:
        return {
            "entries": len(self._cache),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl,
        }


# Global singleton
query_cache = QueryCache()
