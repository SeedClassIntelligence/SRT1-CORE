"""
SCIA Memory Orchestrator v2

Bridges ReflexMemoryRedis (fast pattern-matching with Redis persistence)
and RegenerativeMemory (self-improving graph-based long-term memory)
into a single query interface for the platform.
"""

from typing import Dict, Any

from .reflex_memory_redis import ReflexMemoryRedis
from .regenerative_memory import RegenerativeMemory


class MemoryOrchestratorV2:
    """Enhanced memory orchestrator with Redis support."""

    def __init__(self, redis_url: str = "redis://localhost:6379",
                 db_path: str = "./data/scia_memory.db"):
        self.reflex_memory = ReflexMemoryRedis(redis_url=redis_url)
        self.regenerative_memory = RegenerativeMemory(db_path=db_path)

    async def initialize(self):
        """Initialize async components."""
        await self.reflex_memory.initialize()
        self.regenerative_memory.start_regeneration_cycle()

    async def close(self):
        """Shut down async components."""
        await self.reflex_memory.close()
        await self.regenerative_memory.shutdown()

    async def process_input(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store content in reflex memory; promote to long-term if high importance."""
        trace_id = await self.reflex_memory.store(content, context)

        if context.get('importance', 0) > 0.8:
            tags = set(context.get('tags', []))
            await self.regenerative_memory.store_memory(content, tags=tags)

        return {'trace_id': trace_id, 'status': 'processed'}

    async def query_integrated_memory(self, query: str) -> Dict[str, Any]:
        """Query both reflex and regenerative memory layers."""
        reflex_results = await self.reflex_memory.retrieve(query)
        regen_results = await self.regenerative_memory.retrieve_memory(query)

        return {
            'immediate_context': [r.to_dict() for r in reflex_results],
            'wisdom_context': [
                {
                    'id': n.id,
                    'content': n.content,
                    'strength': n.strength,
                    'generation': n.generation,
                    'tags': list(n.tags),
                }
                for n in regen_results
            ],
        }
