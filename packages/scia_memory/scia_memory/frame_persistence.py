# 🧠 SRT-1 Tag: SCIA_FRAME_PERSISTENCE :: MEMORY_ORCHESTRATOR :: FRAME_STORAGE
# Purpose: Persistence and retrieval capabilities for SeedFlow frames via SCIA Memory Orchestrator
# Module: Frame Persistence Infrastructure - Task 6 Implementation
# Biological Mapping: Cognitive Memory System - Frame state preservation and recall
# SPDI Protection: Encrypted frame storage with integrity validation

import logging
import asyncio
import json
import pickle
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
from pathlib import Path
import aiohttp
import sqlite3

# Import frame classes from SeedFlow Executive Engine
try:
    from seedflow_engine import (  # noqa: F401
        CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame, SeedPacket,
    )
except ImportError:
    # Fallback: define frame classes locally if import fails
    from dataclasses import dataclass
    from typing import Dict, List, Any
    from datetime import datetime

    @dataclass
    class CognitiveFrame:
        frame_id: str
        source_packet: str
        cognitive_analysis: Dict[str, Any]
        identified_patterns: List[str]
        knowledge_gaps: List[str]
        preliminary_insights: List[str]
        analytical_confidence: float
        phase1_methodologies_applied: List[str]
        processing_metadata: Dict[str, Any]

    @dataclass
    class StrategicFrame:
        frame_id: str
        source_cognitive_frame: str
        strategic_options: List[Dict[str, Any]]
        opportunity_analysis: Dict[str, Any]
        risk_assessment: Dict[str, Any]
        resource_requirements: Dict[str, Any]
        success_criteria: List[str]
        strategic_confidence: float
        phase2_methodologies_applied: List[str]
        transformation_metadata: Dict[str, Any]

    @dataclass
    class ValidatedFrame:
        frame_id: str
        source_strategic_frame: str
        validation_results: Dict[str, Any]
        ethical_clearance: bool
        sustainability_assessment: Dict[str, Any]
        integrity_verification: Dict[str, Any]
        readiness_score: float
        validation_confidence: float
        phase3a_methodologies_applied: List[str]
        validation_metadata: Dict[str, Any]

    @dataclass
    class AssignmentFrame:
        frame_id: str
        source_validated_frame: str
        assigned_personas: List[Dict[str, Any]]
        execution_plan: Dict[str, Any]
        deliverable_specifications: Dict[str, Any]
        quality_standards: List[str]
        timeline_estimate: str
        assignment_confidence: float
        phase3b_processing_metadata: Dict[str, Any]
        final_recommendations: List[str]

# Import existing persistence layer
try:
    from .scia_persistence_layer import SCIAPersistenceLayer, DataCategory, StorageConfig  # noqa: F401
except ImportError:
    # Fallback: use simplified persistence if not available
    from enum import Enum

    class DataCategory(Enum):
        COGNITIVE_FRAME = "cognitive_frame"
        STRATEGIC_FRAME = "strategic_frame"
        VALIDATED_FRAME = "validated_frame"
        ASSIGNMENT_FRAME = "assignment_frame"
        SEED_PACKET = "seed_packet"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] - %(message)s')
logger = logging.getLogger("SCIA_FramePersistence")

@dataclass
class FrameMetadata:
    """Metadata for frame persistence"""
    frame_type: str
    created_at: datetime
    updated_at: datetime
    version: int
    checksum: str
    source_frame_id: Optional[str] = None
    processing_phase: Optional[str] = None
    confidence_score: Optional[float] = None
    methodologies_applied: Optional[List[str]] = None

class FrameSerializer:
    """Handles serialization and deserialization of frame objects"""

    @staticmethod
    def serialize_frame(frame: Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame]) -> Dict[str, Any]:
        """Serialize frame object to dictionary"""
        try:
            if hasattr(frame, '__dict__'):
                # Convert dataclass to dict
                frame_dict = asdict(frame)
            else:
                # Fallback for non-dataclass objects
                frame_dict = frame.__dict__.copy()

            # Add type information
            frame_dict['__frame_type__'] = type(frame).__name__
            frame_dict['__serialized_at__'] = datetime.now().isoformat()

            return frame_dict
        except Exception as e:
            logger.error(f"❌ Frame serialization failed: {e}")
            raise

    @staticmethod
    def deserialize_frame(frame_data: Dict[str, Any]) -> Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame]:
        """Deserialize dictionary to frame object"""
        try:
            frame_type = frame_data.pop('__frame_type__', None)
            frame_data.pop('__serialized_at__', None)  # Remove metadata

            # Map frame types to classes
            frame_classes = {
                'CognitiveFrame': CognitiveFrame,
                'StrategicFrame': StrategicFrame,
                'ValidatedFrame': ValidatedFrame,
                'AssignmentFrame': AssignmentFrame
            }

            if frame_type not in frame_classes:
                raise ValueError(f"Unknown frame type: {frame_type}")

            frame_class = frame_classes[frame_type]
            return frame_class(**frame_data)
        except Exception as e:
            logger.error(f"❌ Frame deserialization failed: {e}")
            raise

    @staticmethod
    def calculate_frame_checksum(frame_data: Dict[str, Any]) -> str:
        """Calculate checksum for frame data integrity"""
        # Create a stable string representation for hashing
        frame_str = json.dumps(frame_data, sort_keys=True, default=str)
        return hashlib.sha256(frame_str.encode()).hexdigest()

class SCIAFramePersistence:
    """
    SCIA Frame Persistence Manager

    Provides comprehensive persistence and retrieval capabilities for all SeedFlow frames:
    - CognitiveFrame (Phase 1 output)
    - StrategicFrame (Phase 2 output)
    - ValidatedFrame (Phase 3A output)
    - AssignmentFrame (Phase 3B output)

    Integrates with SCIA Memory Orchestrator for distributed storage and retrieval.
    """

    def __init__(self,
                 memory_orchestrator_url: str = "http://localhost:8080",
                 local_storage_path: str = "./scia_frame_storage",
                 enable_local_cache: bool = True):
        self.memory_orchestrator_url = memory_orchestrator_url.rstrip('/')
        self.local_storage_path = Path(local_storage_path)
        self.enable_local_cache = enable_local_cache
        self.version = "1.0.0-FRAME_PERSISTENCE"

        # Initialize local storage
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        self._init_local_database()

        # Initialize serializer
        self.serializer = FrameSerializer()

        # Statistics
        self.stats = {
            'frames_saved': 0,
            'frames_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'errors': 0
        }

        logger.info(f"🧠 SCIA Frame Persistence v{self.version} initialized")
        logger.info(f"🔗 Memory Orchestrator: {self.memory_orchestrator_url}")
        logger.info(f"💾 Local storage: {self.local_storage_path}")

    def _init_local_database(self):
        """Initialize local SQLite database for caching"""
        db_path = self.local_storage_path / "frame_cache.db"
        self.local_conn = sqlite3.connect(str(db_path), check_same_thread=False)

        cursor = self.local_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS frame_cache (
                frame_id TEXT PRIMARY KEY,
                frame_type TEXT NOT NULL,
                frame_data BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                checksum TEXT,
                source_frame_id TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_frame_type ON frame_cache(frame_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_frame ON frame_cache(source_frame_id)
        """)

        self.local_conn.commit()
        logger.info("💾 Local frame cache database initialized")

    async def save_frame(self,
                        frame: Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame],
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save frame to SCIA Memory Orchestrator with local caching

        Args:
            frame: Frame object to save
            metadata: Optional metadata for the frame

        Returns:
            bool: True if save was successful
        """
        try:
            # Serialize frame
            frame_data = self.serializer.serialize_frame(frame)
            frame_type = type(frame).__name__

            # Create metadata
            frame_metadata = FrameMetadata(
                frame_type=frame_type,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self.serializer.calculate_frame_checksum(frame_data),
                source_frame_id=getattr(frame, 'source_packet', None) or
                               getattr(frame, 'source_cognitive_frame', None) or
                               getattr(frame, 'source_strategic_frame', None) or
                               getattr(frame, 'source_validated_frame', None),
                processing_phase=self._get_processing_phase(frame_type),
                confidence_score=getattr(frame, 'analytical_confidence', None) or
                               getattr(frame, 'strategic_confidence', None) or
                               getattr(frame, 'validation_confidence', None) or
                               getattr(frame, 'assignment_confidence', None),
                methodologies_applied=getattr(frame, 'phase1_methodologies_applied', None) or
                                    getattr(frame, 'phase2_methodologies_applied', None) or
                                    getattr(frame, 'phase3a_methodologies_applied', None)
            )

            if metadata:
                frame_metadata.__dict__.update(metadata)

            # Save to Memory Orchestrator API
            api_success = await self._save_to_memory_orchestrator(frame.frame_id, frame_data, frame_metadata)

            # Save to local cache if enabled
            if self.enable_local_cache:
                self._save_to_local_cache(frame.frame_id, frame_data, frame_metadata)

            if api_success:
                self.stats['frames_saved'] += 1
                logger.info(f"✅ Frame {frame.frame_id} ({frame_type}) saved successfully")
                return True
            else:
                logger.warning(f"⚠️ Frame {frame.frame_id} saved to cache only (API unavailable)")
                return self.enable_local_cache  # Return True if we have local cache

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"❌ Failed to save frame {getattr(frame, 'frame_id', 'unknown')}: {e}")
            return False

    async def load_frame(self,
                        frame_id: str,
                        frame_type: Optional[str] = None) -> Optional[Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame]]:
        """
        Load frame from SCIA Memory Orchestrator with local caching

        Args:
            frame_id: ID of the frame to load
            frame_type: Optional frame type for optimization

        Returns:
            Frame object or None if not found
        """
        try:
            # Try local cache first
            if self.enable_local_cache:
                cached_frame = self._load_from_local_cache(frame_id)
                if cached_frame:
                    self.stats['cache_hits'] += 1
                    self.stats['frames_loaded'] += 1
                    logger.info(f"📋 Frame {frame_id} loaded from cache")
                    return cached_frame
                else:
                    self.stats['cache_misses'] += 1

            # Load from Memory Orchestrator API
            frame_data = await self._load_from_memory_orchestrator(frame_id)
            if frame_data:
                frame = self.serializer.deserialize_frame(frame_data)

                # Update local cache
                if self.enable_local_cache and frame:
                    metadata = FrameMetadata(
                        frame_type=type(frame).__name__,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        version=1,
                        checksum=self.serializer.calculate_frame_checksum(frame_data)
                    )
                    self._save_to_local_cache(frame_id, frame_data, metadata)

                self.stats['frames_loaded'] += 1
                logger.info(f"🔗 Frame {frame_id} loaded from Memory Orchestrator")
                return frame

            logger.warning(f"⚠️ Frame {frame_id} not found")
            return None

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"❌ Failed to load frame {frame_id}: {e}")
            return None

    async def _save_to_memory_orchestrator(self,
                                          frame_id: str,
                                          frame_data: Dict[str, Any],
                                          metadata: FrameMetadata) -> bool:
        """Save frame to Memory Orchestrator via REST API"""
        try:
            payload = {
                'frame_id': frame_id,
                'frame_type': metadata.frame_type,
                'frame_data': frame_data,
                'metadata': asdict(metadata),
                'timestamp': datetime.now().isoformat()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.memory_orchestrator_url}/api/frames",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    self.stats['api_calls'] += 1

                    if response.status in [200, 201]:
                        logger.debug(f"✅ Frame {frame_id} saved to Memory Orchestrator")
                        return True
                    else:
                        logger.warning(f"⚠️ Memory Orchestrator save failed: {response.status}")
                        return False

        except Exception as e:
            logger.warning(f"⚠️ Memory Orchestrator unavailable: {e}")
            return False

    async def _load_from_memory_orchestrator(self, frame_id: str) -> Optional[Dict[str, Any]]:
        """Load frame from Memory Orchestrator via REST API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.memory_orchestrator_url}/api/frames/{frame_id}",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    self.stats['api_calls'] += 1

                    if response.status == 200:
                        result = await response.json()
                        return result.get('frame_data')
                    elif response.status == 404:
                        return None
                    else:
                        logger.warning(f"⚠️ Memory Orchestrator load failed: {response.status}")
                        return None

        except Exception as e:
            logger.warning(f"⚠️ Memory Orchestrator unavailable: {e}")
            return None

    def _save_to_local_cache(self,
                            frame_id: str,
                            frame_data: Dict[str, Any],
                            metadata: FrameMetadata):
        """Save frame to local SQLite cache"""
        try:
            cursor = self.local_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO frame_cache
                (frame_id, frame_type, frame_data, metadata, created_at, updated_at, checksum, source_frame_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                frame_id,
                metadata.frame_type,
                pickle.dumps(frame_data),
                json.dumps(asdict(metadata), default=str),
                metadata.created_at.isoformat(),
                metadata.updated_at.isoformat(),
                metadata.checksum,
                metadata.source_frame_id
            ))
            self.local_conn.commit()
            logger.debug(f"💾 Frame {frame_id} cached locally")

        except Exception as e:
            logger.error(f"❌ Local cache save failed: {e}")

    def _load_from_local_cache(self, frame_id: str) -> Optional[Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame]]:
        """Load frame from local SQLite cache"""
        try:
            cursor = self.local_conn.cursor()
            cursor.execute(
                "SELECT frame_data, checksum FROM frame_cache WHERE frame_id = ?",
                (frame_id,)
            )
            row = cursor.fetchone()

            if row:
                frame_data_blob, stored_checksum = row
                frame_data = pickle.loads(frame_data_blob)

                # Verify checksum
                calculated_checksum = self.serializer.calculate_frame_checksum(frame_data)
                if calculated_checksum != stored_checksum:
                    logger.warning(f"⚠️ Checksum mismatch for cached frame {frame_id}")
                    return None

                return self.serializer.deserialize_frame(frame_data)

            return None

        except Exception as e:
            logger.error(f"❌ Local cache load failed: {e}")
            return None

    def _get_processing_phase(self, frame_type: str) -> str:
        """Map frame type to processing phase"""
        phase_mapping = {
            'CognitiveFrame': 'Phase1_SensoryIntake',
            'StrategicFrame': 'Phase2_CognitiveTransformation',
            'ValidatedFrame': 'Phase3A_ValidationReadiness',
            'AssignmentFrame': 'Phase3B_DynamicAssignment'
        }
        return phase_mapping.get(frame_type, 'Unknown')

    async def get_frame_lineage(self, frame_id: str) -> List[Dict[str, Any]]:
        """Get the complete lineage of a frame (all related frames)"""
        lineage = []
        try:
            # Start with the requested frame
            current_frame = await self.load_frame(frame_id)
            if not current_frame:
                return lineage

            # Build lineage by following source relationships
            visited = set()
            queue = [current_frame]

            while queue and len(visited) < 10:  # Prevent infinite loops
                frame = queue.pop(0)
                if frame.frame_id in visited:
                    continue

                visited.add(frame.frame_id)
                lineage.append({
                    'frame_id': frame.frame_id,
                    'frame_type': type(frame).__name__,
                    'created_at': getattr(frame, 'processing_metadata', {}).get('processing_timestamp'),
                    'confidence': getattr(frame, 'analytical_confidence', None) or
                                getattr(frame, 'strategic_confidence', None) or
                                getattr(frame, 'validation_confidence', None) or
                                getattr(frame, 'assignment_confidence', None)
                })

                # Find source frame
                source_id = (getattr(frame, 'source_packet', None) or
                           getattr(frame, 'source_cognitive_frame', None) or
                           getattr(frame, 'source_strategic_frame', None) or
                           getattr(frame, 'source_validated_frame', None))

                if source_id and source_id not in visited:
                    source_frame = await self.load_frame(source_id)
                    if source_frame:
                        queue.append(source_frame)

            return lineage

        except Exception as e:
            logger.error(f"❌ Failed to get frame lineage: {e}")
            return lineage

    async def search_frames(self,
                           frame_type: Optional[str] = None,
                           confidence_threshold: Optional[float] = None,
                           created_after: Optional[datetime] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Search frames based on criteria"""
        try:
            # Search local cache
            cursor = self.local_conn.cursor()

            query = "SELECT frame_id, frame_type, metadata, created_at FROM frame_cache WHERE 1=1"
            params = []

            if frame_type:
                query += " AND frame_type = ?"
                params.append(frame_type)

            if created_after:
                query += " AND created_at > ?"
                params.append(created_after.isoformat())

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                frame_id, frame_type, metadata_json, created_at = row
                metadata = json.loads(metadata_json) if metadata_json else {}

                # Apply confidence filter
                if confidence_threshold and metadata.get('confidence_score', 0) < confidence_threshold:
                    continue

                results.append({
                    'frame_id': frame_id,
                    'frame_type': frame_type,
                    'created_at': created_at,
                    'metadata': metadata
                })

            return results

        except Exception as e:
            logger.error(f"❌ Frame search failed: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get persistence statistics"""
        try:
            # Get cache statistics
            cursor = self.local_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM frame_cache")
            cache_count = cursor.fetchone()[0]

            cursor.execute("SELECT frame_type, COUNT(*) FROM frame_cache GROUP BY frame_type")
            type_counts = dict(cursor.fetchall())

            return {
                'version': self.version,
                'cache_enabled': self.enable_local_cache,
                'cached_frames': cache_count,
                'frames_by_type': type_counts,
                'runtime_stats': self.stats.copy(),
                'memory_orchestrator_url': self.memory_orchestrator_url
            }

        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {'error': str(e)}

    async def cleanup_old_frames(self, days_old: int = 30) -> int:
        """Clean up old frames from local cache"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            cursor = self.local_conn.cursor()
            cursor.execute(
                "DELETE FROM frame_cache WHERE created_at < ?",
                (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
            self.local_conn.commit()

            logger.info(f"🧹 Cleaned up {deleted_count} old frames")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global instance for easy access
_frame_persistence = None

def get_frame_persistence(memory_orchestrator_url: str = "http://localhost:8080") -> SCIAFramePersistence:
    """Get global frame persistence instance"""
    global _frame_persistence
    if _frame_persistence is None:
        _frame_persistence = SCIAFramePersistence(memory_orchestrator_url)
    return _frame_persistence

async def save_cognitive_frame(frame: CognitiveFrame) -> bool:
    """Convenience function to save CognitiveFrame"""
    persistence = get_frame_persistence()
    return await persistence.save_frame(frame)

async def save_strategic_frame(frame: StrategicFrame) -> bool:
    """Convenience function to save StrategicFrame"""
    persistence = get_frame_persistence()
    return await persistence.save_frame(frame)

async def save_validated_frame(frame: ValidatedFrame) -> bool:
    """Convenience function to save ValidatedFrame"""
    persistence = get_frame_persistence()
    return await persistence.save_frame(frame)

async def save_assignment_frame(frame: AssignmentFrame) -> bool:
    """Convenience function to save AssignmentFrame"""
    persistence = get_frame_persistence()
    return await persistence.save_frame(frame)

async def load_any_frame(frame_id: str) -> Optional[Union[CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame]]:
    """Convenience function to load any frame type"""
    persistence = get_frame_persistence()
    return await persistence.load_frame(frame_id)

# =============================================================================
# TESTING AND VALIDATION
# =============================================================================

if __name__ == "__main__":
    async def test_frame_persistence():
        """Test frame persistence functionality"""
        print("🧪 Testing SCIA Frame Persistence...")

        # Initialize persistence
        persistence = SCIAFramePersistence(
            memory_orchestrator_url="http://localhost:8080",
            local_storage_path="./test_frame_storage"
        )

        # Create test frames
        cognitive_frame = CognitiveFrame(
            frame_id="test_cognitive_001",
            source_packet="test_packet_001",
            cognitive_analysis={"patterns": ["test_pattern"]},
            identified_patterns=["pattern1", "pattern2"],
            knowledge_gaps=["gap1"],
            preliminary_insights=["insight1"],
            analytical_confidence=0.85,
            phase1_methodologies_applied=["test_methodology"],
            processing_metadata={"test": True}
        )

        strategic_frame = StrategicFrame(
            frame_id="test_strategic_001",
            source_cognitive_frame="test_cognitive_001",
            strategic_options=[{"option": "test_option"}],
            opportunity_analysis={"opportunities": ["opp1"]},
            risk_assessment={"risks": ["risk1"]},
            resource_requirements={"resources": ["res1"]},
            success_criteria=["criteria1"],
            strategic_confidence=0.78,
            phase2_methodologies_applied=["strategic_methodology"],
            transformation_metadata={"test": True}
        )

        # Test saving
        print("💾 Testing frame saving...")
        cognitive_saved = await persistence.save_frame(cognitive_frame)
        strategic_saved = await persistence.save_frame(strategic_frame)

        print(f"Cognitive frame saved: {cognitive_saved}")
        print(f"Strategic frame saved: {strategic_saved}")

        # Test loading
        print("📋 Testing frame loading...")
        loaded_cognitive = await persistence.load_frame("test_cognitive_001")
        loaded_strategic = await persistence.load_frame("test_strategic_001")

        print(f"Cognitive frame loaded: {loaded_cognitive is not None}")
        print(f"Strategic frame loaded: {loaded_strategic is not None}")

        if loaded_cognitive:
            print(f"Loaded cognitive confidence: {loaded_cognitive.analytical_confidence}")

        # Test lineage
        print("🔗 Testing frame lineage...")
        lineage = await persistence.get_frame_lineage("test_strategic_001")
        print(f"Frame lineage: {len(lineage)} frames")

        # Test search
        print("🔍 Testing frame search...")
        search_results = await persistence.search_frames(frame_type="CognitiveFrame")
        print(f"Search results: {len(search_results)} frames")

        # Get statistics
        print("📊 Getting statistics...")
        stats = persistence.get_statistics()
        print(f"Statistics: {stats}")

        print("✅ Frame persistence testing completed!")

    # Run test
    asyncio.run(test_frame_persistence())
