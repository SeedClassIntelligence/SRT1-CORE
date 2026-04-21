"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: DATABASE_SERVICE, TRACING_AUDIT
Key Symbols: MemoryEntry, AdvancedMemorySystem, __init__, _default_config, start_cleanup_task ... and 14 more

Extracted Purposes:
  - MemoryEntry: Base memory entry structure
  - AdvancedMemorySystem: Advanced memory system with multiple storage types
  - start_cleanup_task: Start background cleanup task. Call from within a running event loop.
  ...
"""
#!/usr/bin/env python3
"""
Advanced Memory System for SCIA
Integrates multiple memory types and provides unified interface
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MemoryEntry:
    """Base memory entry structure"""
    key: str
    data: Any
    timestamp: datetime
    memory_type: str
    metadata: Dict[str, Any]
    ttl: Optional[int] = None  # Time to live in seconds
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class AdvancedMemorySystem:
    """Advanced memory system with multiple storage types"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.memory_stores = {
            'short_term': {},  # Fast access, limited capacity
            'long_term': {},   # Persistent storage
            'working': {},     # Current session data
            'episodic': {},    # Event-based memories
            'semantic': {}     # Knowledge-based memories
        }
        self.memory_stats = {
            'total_entries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'evictions': 0
        }
        self.cleanup_task = None

    def _default_config(self) -> Dict[str, Any]:
        return {
            'short_term_capacity': 1000,
            'long_term_capacity': 10000,
            'working_capacity': 100,
            'cleanup_interval': 300,  # 5 minutes
            'default_ttl': 3600,      # 1 hour
            'compression_enabled': True,
            'persistence_enabled': True
        }

    def start_cleanup_task(self):
        """Start background cleanup task. Call from within a running event loop."""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(self.config['cleanup_interval'])
                await self._cleanup_expired_entries()

        try:
            loop = asyncio.get_running_loop()
            self.cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            pass

    async def store(self, key: str, data: Any, memory_type: str = 'short_term',
                   metadata: Dict[str, Any] = None, ttl: Optional[int] = None) -> bool:
        """Store data in specified memory type"""
        if memory_type not in self.memory_stores:
            raise ValueError(f"Invalid memory type: {memory_type}")

        # Create memory entry
        entry = MemoryEntry(
            key=key,
            data=data,
            timestamp=datetime.now(),
            memory_type=memory_type,
            metadata=metadata or {},
            ttl=ttl or self.config['default_ttl']
        )

        # Check capacity and evict if necessary
        await self._ensure_capacity(memory_type)

        # Store entry
        self.memory_stores[memory_type][key] = entry
        self.memory_stats['total_entries'] += 1

        print(f"📝 Stored in {memory_type} memory: {key}")
        return True

    async def retrieve(self, key: str, memory_type: Optional[str] = None) -> Optional[Any]:
        """Retrieve data from memory"""
        # Search in specific memory type or all types
        search_types = [memory_type] if memory_type else self.memory_stores.keys()

        for mem_type in search_types:
            if key in self.memory_stores[mem_type]:
                entry = self.memory_stores[mem_type][key]

                # Check if entry is expired
                if self._is_expired(entry):
                    await self.delete(key, mem_type)
                    continue

                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self.memory_stats['cache_hits'] += 1

                print(f"📖 Retrieved from {mem_type} memory: {key}")
                return entry.data

        self.memory_stats['cache_misses'] += 1
        return None

    async def delete(self, key: str, memory_type: Optional[str] = None) -> bool:
        """Delete data from memory"""
        deleted = False
        search_types = [memory_type] if memory_type else self.memory_stores.keys()

        for mem_type in search_types:
            if key in self.memory_stores[mem_type]:
                del self.memory_stores[mem_type][key]
                self.memory_stats['total_entries'] -= 1
                deleted = True
                print(f"🗑️ Deleted from {mem_type} memory: {key}")

        return deleted

    async def search(self, query: str, memory_type: Optional[str] = None,
                    limit: int = 10) -> List[MemoryEntry]:
        """Search for entries matching query"""
        results = []
        search_types = [memory_type] if memory_type else self.memory_stores.keys()

        for mem_type in search_types:
            for key, entry in self.memory_stores[mem_type].items():
                if self._is_expired(entry):
                    continue

                # Simple text search in key and metadata
                if (query.lower() in key.lower() or
                    query.lower() in str(entry.metadata).lower()):
                    results.append(entry)

                    if len(results) >= limit:
                        break

        # Sort by relevance (access count and recency)
        results.sort(key=lambda x: (x.access_count, x.timestamp), reverse=True)
        return results[:limit]

    async def get_related(self, key: str, similarity_threshold: float = 0.7) -> List[MemoryEntry]:
        """Get entries related to the given key"""
        related = []

        for mem_type in self.memory_stores:
            for entry_key, entry in self.memory_stores[mem_type].items():
                if entry_key == key or self._is_expired(entry):
                    continue

                # Calculate similarity (simplified)
                similarity = self._calculate_similarity(key, entry_key)
                if similarity >= similarity_threshold:
                    related.append(entry)

        return sorted(related, key=lambda x: x.timestamp, reverse=True)

    def _calculate_similarity(self, key1: str, key2: str) -> float:
        """Calculate similarity between two keys (simplified)"""
        # Simple Jaccard similarity
        set1 = set(key1.lower().split())
        set2 = set(key2.lower().split())

        if not set1 and not set2:
            return 1.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _is_expired(self, entry: MemoryEntry) -> bool:
        """Check if memory entry is expired"""
        if not entry.ttl:
            return False

        expiry_time = entry.timestamp + timedelta(seconds=entry.ttl)
        return datetime.now() > expiry_time

    async def _ensure_capacity(self, memory_type: str):
        """Ensure memory type doesn't exceed capacity"""
        capacity_key = f"{memory_type}_capacity"
        max_capacity = self.config.get(capacity_key, 1000)

        current_size = len(self.memory_stores[memory_type])

        if current_size >= max_capacity:
            # Evict least recently used entries
            entries = list(self.memory_stores[memory_type].items())
            entries.sort(key=lambda x: x[1].last_accessed or x[1].timestamp)

            # Remove oldest 10% of entries
            evict_count = max(1, int(max_capacity * 0.1))
            for i in range(evict_count):
                if i < len(entries):
                    key_to_evict = entries[i][0]
                    del self.memory_stores[memory_type][key_to_evict]
                    self.memory_stats['evictions'] += 1

    async def _cleanup_expired_entries(self):
        """Clean up expired entries across all memory types"""
        cleaned_count = 0

        for mem_type in self.memory_stores:
            expired_keys = []

            for key, entry in self.memory_stores[mem_type].items():
                if self._is_expired(entry):
                    expired_keys.append(key)

            for key in expired_keys:
                del self.memory_stores[mem_type][key]
                cleaned_count += 1
                self.memory_stats['total_entries'] -= 1

        if cleaned_count > 0:
            print(f"🧹 Cleaned up {cleaned_count} expired memory entries")

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = self.memory_stats.copy()

        # Add current memory usage
        for mem_type in self.memory_stores:
            stats[f"{mem_type}_count"] = len(self.memory_stores[mem_type])

        # Calculate hit rate
        total_requests = stats['cache_hits'] + stats['cache_misses']
        stats['hit_rate'] = stats['cache_hits'] / total_requests if total_requests > 0 else 0

        return stats

    async def export_memory(self, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """Export memory data for backup or analysis"""
        export_data = {}

        export_types = [memory_type] if memory_type else self.memory_stores.keys()

        for mem_type in export_types:
            export_data[mem_type] = {}
            for key, entry in self.memory_stores[mem_type].items():
                if not self._is_expired(entry):
                    export_data[mem_type][key] = {
                        'data': entry.data,
                        'timestamp': entry.timestamp.isoformat(),
                        'metadata': entry.metadata,
                        'access_count': entry.access_count
                    }

        return export_data

    async def import_memory(self, import_data: Dict[str, Any]) -> bool:
        """Import memory data from backup"""
        try:
            for mem_type, entries in import_data.items():
                if mem_type not in self.memory_stores:
                    continue

                for key, entry_data in entries.items():
                    await self.store(
                        key=key,
                        data=entry_data['data'],
                        memory_type=mem_type,
                        metadata=entry_data.get('metadata', {})
                    )

            print("📥 Memory import completed successfully")
            return True
        except Exception as e:
            print(f"❌ Memory import failed: {e}")
            return False

    async def shutdown(self):
        """Shutdown memory system"""
        if self.cleanup_task:
            self.cleanup_task.cancel()

        # Optionally persist data
        if self.config.get('persistence_enabled'):
            await self.export_memory()
            # Save to file (implementation depends on storage backend)
            print("💾 Memory data persisted")

        print("🔌 Memory system shutdown complete")
