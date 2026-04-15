"""
Redis-backed Reflex Memory Adapter for SCIA

Wraps the core ReflexMemory with Redis persistence so that
patterns and cached responses survive service restarts.

The MemoryOrchestratorV2 expects this class with:
    initialize(), close(), store(content, context), retrieve(query)
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .reflex_memory import ReflexMemory

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


@dataclass
class ReflexEntry:
    """A stored reflex memory entry with Redis persistence."""
    trace_id: str
    content: str
    context: Dict[str, Any]
    timestamp: str
    reflex_response: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "content": self.content,
            "context": self.context,
            "timestamp": self.timestamp,
            "reflex_response": self.reflex_response,
        }


class ReflexMemoryRedis:
    """Redis-backed reflex memory that satisfies MemoryOrchestratorV2 interface."""

    REDIS_PREFIX = "scia:reflex:"

    def __init__(self, redis_url: str = "redis://localhost:6379",
                 max_patterns: int = 1000):
        self.redis_url = redis_url
        self._redis = None
        self._reflex = ReflexMemory(max_patterns=max_patterns)
        self._local_store: Dict[str, ReflexEntry] = {}

    async def initialize(self):
        """Connect to Redis. Falls back to in-memory if unavailable."""
        if aioredis is not None:
            try:
                self._redis = aioredis.from_url(
                    self.redis_url, decode_responses=True
                )
                await self._redis.ping()
            except Exception:
                self._redis = None

    async def close(self):
        """Shut down Redis connection."""
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    async def store(self, content: str, context: Dict[str, Any]) -> str:
        """Store content in reflex memory.  Returns a trace_id."""
        trace_id = self._make_trace_id(content)

        reflex_response = await self._reflex.get_reflex_response(
            content, context
        )

        entry = ReflexEntry(
            trace_id=trace_id,
            content=content,
            context=context,
            timestamp=datetime.now().isoformat(),
            reflex_response=str(reflex_response) if reflex_response else None,
        )

        if self._redis is not None:
            key = f"{self.REDIS_PREFIX}{trace_id}"
            await self._redis.set(key, json.dumps(entry.to_dict()), ex=3600)
        else:
            self._local_store[trace_id] = entry

        if self._reflex.learning_enabled:
            self._reflex.learn_from_interaction(
                content,
                reflex_response or content,
                context,
            )

        return trace_id

    async def retrieve(self, query: str, limit: int = 10) -> List[ReflexEntry]:
        """Retrieve entries matching *query* from Redis or local store."""
        results: List[ReflexEntry] = []
        query_lower = query.lower()

        if self._redis is not None:
            cursor = "0"
            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor,
                    match=f"{self.REDIS_PREFIX}*",
                    count=100,
                )
                for key in keys:
                    raw = await self._redis.get(key)
                    if raw:
                        data = json.loads(raw)
                        if (query_lower in data.get("content", "").lower()
                                or query_lower in str(data.get("context", "")).lower()):
                            results.append(ReflexEntry(**data))
                            if len(results) >= limit:
                                return results
                if cursor == "0" or cursor == 0:
                    break
        else:
            for entry in self._local_store.values():
                if (query_lower in entry.content.lower()
                        or query_lower in str(entry.context).lower()):
                    results.append(entry)
                    if len(results) >= limit:
                        break

        return results

    @staticmethod
    def _make_trace_id(content: str) -> str:
        raw = content + str(datetime.now().timestamp())
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
