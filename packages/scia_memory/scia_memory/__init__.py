"""
SCIA Memory — Standalone Package

Drop this folder into any SCIA system to add adaptive memory capabilities:
- ReflexMemory: instant pattern-based threat detection and learning
- RegenerativeMemory: self-improving graph-based long-term memory
- AdvancedMemorySystem: 5-tier memory (short/long/working/episodic/semantic)
- ReflexMemoryRedis: Redis-backed persistence for reflex patterns
- MemoryOrchestratorV2: unified interface bridging all memory layers
- SCIAFramePersistence: SeedFlow frame storage with SQLite caching
- SCIAMemoryOrchestratorAPI: REST API server for frame operations

Usage:
    from scia_memory import MemoryOrchestratorV2
    orchestrator = MemoryOrchestratorV2(redis_url="redis://localhost:6379")
    await orchestrator.initialize()
    await orchestrator.process_input("content", {"importance": 0.9})

    from scia_memory import ReflexMemory
    reflex = ReflexMemory()
    response = await reflex.get_reflex_response("hello")

    from scia_memory import RegenerativeMemory
    regen = RegenerativeMemory()
    node_id = await regen.store_memory("important data", tags={"critical"})

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

from .memory_system import AdvancedMemorySystem, MemoryEntry
from .reflex_memory import ReflexMemory, ReflexPattern
from .regenerative_memory import RegenerativeMemory, MemoryNode
from .reflex_memory_redis import ReflexMemoryRedis, ReflexEntry
from .memory_system_v2 import MemoryOrchestratorV2

__all__ = [
    "AdvancedMemorySystem",
    "MemoryEntry",
    "ReflexMemory",
    "ReflexPattern",
    "RegenerativeMemory",
    "MemoryNode",
    "ReflexMemoryRedis",
    "ReflexEntry",
    "MemoryOrchestratorV2",
]

__version__ = "2.1.0"
__author__ = "William Darnell Jernigan IV"
