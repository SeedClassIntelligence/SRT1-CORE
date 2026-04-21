"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: DATABASE_SERVICE, TRACING_AUDIT
Key Symbols: MemoryNode, RegenerativeMemory, __init__, start_regeneration_cycle, store_memory ... and 9 more

Extracted Purposes:
  - MemoryNode: Node in regenerative memory network
  - RegenerativeMemory: Self-improving regenerative memory system
  - start_regeneration_cycle: Start background regeneration cycle. Call from within a running event loop.
  ...
"""
#!/usr/bin/env python3
"""
Regenerative Memory System
Self-improving memory that adapts and evolves
"""

import asyncio
from typing import Dict, Any, List, Set
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MemoryNode:
    """Node in regenerative memory network"""
    id: str
    content: Any
    connections: Set[str] = field(default_factory=set)
    strength: float = 1.0
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    generation: int = 0
    tags: Set[str] = field(default_factory=set)

class RegenerativeMemory:
    """Self-improving regenerative memory system"""

    def __init__(self, max_nodes: int = 5000, regeneration_interval: int = 3600,
                 db_path: str = None):
        self.nodes: Dict[str, MemoryNode] = {}
        self.max_nodes = max_nodes
        self.regeneration_interval = regeneration_interval
        self.connection_threshold = 0.5
        self.regeneration_task = None
        self.db_path = db_path
        self.evolution_stats = {
            'regenerations': 0,
            'connections_formed': 0,
            'nodes_evolved': 0,
            'weak_nodes_removed': 0
        }

    def start_regeneration_cycle(self):
        """Start background regeneration cycle. Call from within a running event loop."""
        async def regeneration_loop():
            while True:
                await asyncio.sleep(self.regeneration_interval)
                await self._regenerate_memory()

        try:
            loop = asyncio.get_running_loop()
            self.regeneration_task = loop.create_task(regeneration_loop())
        except RuntimeError:
            pass

    async def store_memory(self, content: Any, tags: Set[str] = None,
                          node_id: str = None) -> str:
        """Store new memory with regenerative capabilities"""
        if not node_id:
            node_id = self._generate_node_id(content)

        # Create new memory node
        node = MemoryNode(
            id=node_id,
            content=content,
            tags=tags or set(),
            generation=0
        )

        # Find and create connections
        await self._create_connections(node)

        # Store node
        self.nodes[node_id] = node

        # Manage capacity
        if len(self.nodes) > self.max_nodes:
            await self._prune_weak_nodes()

        print(f"🌱 Stored regenerative memory: {node_id}")
        return node_id

    async def retrieve_memory(self, query: str, limit: int = 10) -> List[MemoryNode]:
        """Retrieve memories matching the query, ranked by strength and relevance."""
        results = []
        query_lower = query.lower()

        for node in self.nodes.values():
            content_str = str(node.content).lower()
            tag_str = " ".join(node.tags).lower() if node.tags else ""

            if query_lower in content_str or query_lower in tag_str:
                node.access_count += 1
                node.last_accessed = datetime.now()
                node.strength = min(2.0, node.strength + 0.05)
                results.append(node)

        results.sort(key=lambda n: (n.strength, n.access_count), reverse=True)
        return results[:limit]

    async def _create_connections(self, new_node: MemoryNode):
        """Form connections between the new node and existing related nodes."""
        for existing_node in self.nodes.values():
            similarity = self._compute_similarity(new_node, existing_node)
            if similarity >= self.connection_threshold:
                new_node.connections.add(existing_node.id)
                existing_node.connections.add(new_node.id)
                self.evolution_stats['connections_formed'] += 1

    def _compute_similarity(self, node_a: MemoryNode, node_b: MemoryNode) -> float:
        """Compute similarity between two nodes based on tag overlap and content."""
        if node_a.tags and node_b.tags:
            intersection = len(node_a.tags & node_b.tags)
            union = len(node_a.tags | node_b.tags)
            if union > 0:
                return intersection / union
        content_a = set(str(node_a.content).lower().split())
        content_b = set(str(node_b.content).lower().split())
        if content_a and content_b:
            intersection = len(content_a & content_b)
            union = len(content_a | content_b)
            if union > 0:
                return intersection / union
        return 0.0

    async def _prune_weak_nodes(self):
        """Remove weakest nodes when capacity is exceeded."""
        if len(self.nodes) <= self.max_nodes:
            return

        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: (n.strength, n.access_count, n.last_accessed)
        )

        remove_count = len(self.nodes) - self.max_nodes
        for node in sorted_nodes[:remove_count]:
            for connected_id in node.connections:
                if connected_id in self.nodes:
                    self.nodes[connected_id].connections.discard(node.id)
            del self.nodes[node.id]
            self.evolution_stats['weak_nodes_removed'] += 1

    async def _regenerate_memory(self):
        """Regeneration cycle: strengthen active connections, weaken idle ones, evolve nodes."""
        self.evolution_stats['regenerations'] += 1

        for node in list(self.nodes.values()):
            time_since_access = (datetime.now() - node.last_accessed).total_seconds()

            if time_since_access < 3600:
                node.strength = min(2.0, node.strength + 0.02)
            else:
                decay = min(0.1, time_since_access / 360000)
                node.strength = max(0.1, node.strength - decay)

            if node.access_count > 5 and node.strength > 1.0:
                node.generation += 1
                self.evolution_stats['nodes_evolved'] += 1

        await self._prune_weak_nodes()

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Return current evolution statistics."""
        return {
            **self.evolution_stats,
            'total_nodes': len(self.nodes),
            'avg_strength': (
                sum(n.strength for n in self.nodes.values()) / len(self.nodes)
                if self.nodes else 0.0
            ),
            'avg_connections': (
                sum(len(n.connections) for n in self.nodes.values()) / len(self.nodes)
                if self.nodes else 0.0
            ),
        }

    async def shutdown(self):
        """Cancel background tasks and clean up."""
        if self.regeneration_task:
            self.regeneration_task.cancel()

    def _generate_node_id(self, content: Any) -> str:
        """Generate unique node ID"""
        import hashlib
        content_str = str(content) + str(datetime.now().timestamp())
        return hashlib.md5(content_str.encode()).hexdigest()[:12]
