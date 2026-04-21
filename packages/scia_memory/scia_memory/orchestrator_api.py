"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: API_CONTROLLER
Key Symbols: FrameRequest, FrameResponse, FrameSearchRequest, FrameSearchResponse, LineageResponse ... and 21 more

Extracted Purposes:
  - FrameRequest: Request model for saving frames
  - FrameResponse: Response model for frame operations
  - FrameSearchRequest: Request model for searching frames
  ...
"""
# 🧠 SRT-1 Tag: SCIA_MEMORY_ORCHESTRATOR_API :: REST_ENDPOINTS :: FRAME_MANAGEMENT
# Purpose: REST API server for SCIA Memory Orchestrator frame persistence
# Module: Memory Orchestrator API - Task 6 Implementation
# Biological Mapping: Memory Access Interface - API gateway for frame operations
# SPDI Protection: Authenticated API endpoints with request validation

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager

# Import frame persistence
try:
    from .frame_persistence import SCIAFramePersistence, FrameMetadata  # noqa: F401
    from .frame_persistence import (  # noqa: F401
        CognitiveFrame, StrategicFrame, ValidatedFrame, AssignmentFrame,
    )
except ImportError:
    SCIAFramePersistence = None

# Import existing persistence layer
try:
    from .scia_persistence_layer import SCIAPersistenceLayer, DataCategory  # noqa: F401
except ImportError:
    SCIAPersistenceLayer = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] - %(message)s')
logger = logging.getLogger("SCIA_MemoryOrchestrator")

# =============================================================================
# PYDANTIC MODELS FOR API
# =============================================================================

class FrameRequest(BaseModel):
    """Request model for saving frames"""
    frame_id: str = Field(..., description="Unique identifier for the frame")
    frame_type: str = Field(..., description="Type of frame (CognitiveFrame, StrategicFrame, etc.)")
    frame_data: Dict[str, Any] = Field(..., description="Serialized frame data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    timestamp: Optional[str] = Field(None, description="Timestamp of the request")

class FrameResponse(BaseModel):
    """Response model for frame operations"""
    frame_id: str
    frame_type: str
    frame_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    success: bool = True
    message: Optional[str] = None

class FrameSearchRequest(BaseModel):
    """Request model for searching frames"""
    frame_type: Optional[str] = Field(None, description="Filter by frame type")
    confidence_threshold: Optional[float] = Field(None, description="Minimum confidence score")
    created_after: Optional[str] = Field(None, description="Filter frames created after this date")
    created_before: Optional[str] = Field(None, description="Filter frames created before this date")
    source_frame_id: Optional[str] = Field(None, description="Filter by source frame ID")
    limit: int = Field(100, description="Maximum number of results")

class FrameSearchResponse(BaseModel):
    """Response model for frame search"""
    frames: List[Dict[str, Any]]
    total_count: int
    search_criteria: Dict[str, Any]
    timestamp: str

class LineageResponse(BaseModel):
    """Response model for frame lineage"""
    frame_id: str
    lineage: List[Dict[str, Any]]
    total_frames: int
    timestamp: str

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    uptime: str
    memory_orchestrator: Dict[str, Any]
    frame_persistence: Dict[str, Any]
    timestamp: str

class StatisticsResponse(BaseModel):
    """Response model for statistics"""
    memory_orchestrator: Dict[str, Any]
    frame_persistence: Dict[str, Any]
    api_stats: Dict[str, Any]
    timestamp: str

# =============================================================================
# MEMORY ORCHESTRATOR API SERVER
# =============================================================================

class SCIAMemoryOrchestratorAPI:
    """
    SCIA Memory Orchestrator API Server

    Provides REST API endpoints for frame persistence and retrieval:
    - POST /api/frames - Save frame
    - GET /api/frames/{frame_id} - Load frame
    - GET /api/frames/search - Search frames
    - GET /api/frames/{frame_id}/lineage - Get frame lineage
    - GET /api/health - Health check
    - GET /api/statistics - Get statistics
    """

    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8080,
                 enable_auth: bool = False,
                 local_storage_path: str = "./scia_memory_orchestrator"):
        self.host = host
        self.port = port
        self.enable_auth = enable_auth
        self.local_storage_path = local_storage_path
        self.version = "1.0.0-MEMORY_ORCHESTRATOR_API"
        self.start_time = datetime.now()

        # Initialize components
        self.frame_persistence = None
        self.persistence_layer = None

        # API statistics
        self.api_stats = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'frames_saved': 0,
            'frames_loaded': 0,
            'searches_performed': 0,
            'lineage_requests': 0
        }

        # Initialize FastAPI app
        self.app = self._create_app()

        logger.info(f"🧠 SCIA Memory Orchestrator API v{self.version} initialized")
        logger.info(f"🌐 Server: {self.host}:{self.port}")
        logger.info(f"🔐 Authentication: {'Enabled' if self.enable_auth else 'Disabled'}")

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application"""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self._initialize_components()
            logger.info("🚀 SCIA Memory Orchestrator API started")
            yield
            # Shutdown
            logger.info("🛑 SCIA Memory Orchestrator API shutting down")

        app = FastAPI(
            title="SCIA Memory Orchestrator API",
            description="REST API for SCIA frame persistence and retrieval",
            version=self.version,
            lifespan=lifespan
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add routes
        self._add_routes(app)

        return app

    async def _initialize_components(self):
        """Initialize frame persistence and other components"""
        try:
            # Initialize frame persistence
            if SCIAFramePersistence:
                self.frame_persistence = SCIAFramePersistence(
                    memory_orchestrator_url=f"http://{self.host}:{self.port}",
                    local_storage_path=self.local_storage_path,
                    enable_local_cache=True
                )
                logger.info("✅ Frame persistence initialized")

            # Initialize persistence layer
            if SCIAPersistenceLayer:
                self.persistence_layer = SCIAPersistenceLayer()
                logger.info("✅ Persistence layer initialized")

        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")

    def _add_routes(self, app: FastAPI):
        """Add API routes to FastAPI app"""

        # Authentication dependency
        security = HTTPBearer() if self.enable_auth else None

        def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
            if self.enable_auth and not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            return credentials.credentials if credentials else None

        @app.get("/", response_model=Dict[str, Any])
        async def root():
            """Root endpoint"""
            return {
                "service": "SCIA Memory Orchestrator API",
                "version": self.version,
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "endpoints": {
                    "frames": "/api/frames",
                    "health": "/api/health",
                    "statistics": "/api/statistics"
                }
            }

        @app.post("/api/frames", response_model=FrameResponse)
        async def save_frame(
            request: FrameRequest,
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Save a frame to the memory orchestrator"""
            self.api_stats['requests_total'] += 1

            try:
                if not self.frame_persistence:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Frame persistence not available"
                    )

                # Validate frame data
                if not request.frame_id or not request.frame_type or not request.frame_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing required fields: frame_id, frame_type, frame_data"
                    )

                # Create frame metadata
                FrameMetadata(
                    frame_type=request.frame_type,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=1,
                    checksum="",  # Will be calculated by persistence layer
                    source_frame_id=request.metadata.get('source_frame_id') if request.metadata else None
                )

                # Save to persistence layer directly (since this IS the memory orchestrator)
                if self.persistence_layer:
                    # Map frame type to data category
                    category_mapping = {
                        'CognitiveFrame': DataCategory.SEED_PACKET,  # Closest match
                        'StrategicFrame': DataCategory.EXECUTION_RESULT,
                        'ValidatedFrame': DataCategory.EXECUTION_RESULT,
                        'AssignmentFrame': DataCategory.EXECUTION_RESULT
                    }

                    category = category_mapping.get(request.frame_type, DataCategory.EXECUTION_RESULT)
                    success = await self.persistence_layer.save(
                        entity_id=request.frame_id,
                        entity_type=category,
                        data=request.frame_data,
                        metadata=request.metadata or {}
                    )

                    if success:
                        self.api_stats['requests_successful'] += 1
                        self.api_stats['frames_saved'] += 1

                        return FrameResponse(
                            frame_id=request.frame_id,
                            frame_type=request.frame_type,
                            metadata=request.metadata,
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat(),
                            success=True,
                            message="Frame saved successfully"
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save frame"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Persistence layer not available"
                    )

            except HTTPException:
                self.api_stats['requests_failed'] += 1
                raise
            except Exception as e:
                self.api_stats['requests_failed'] += 1
                logger.error(f"❌ Save frame error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal server error: {str(e)}"
                )

        @app.get("/api/frames/{frame_id}", response_model=FrameResponse)
        async def load_frame(
            frame_id: str,
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Load a frame from the memory orchestrator"""
            self.api_stats['requests_total'] += 1

            try:
                if not self.persistence_layer:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Persistence layer not available"
                    )

                # Try to load from different categories
                categories = [DataCategory.SEED_PACKET, DataCategory.EXECUTION_RESULT,
                            DataCategory.SYSTEM_EVENT, DataCategory.USER_SESSION]

                frame_data = None
                for category in categories:
                    frame_data = await self.persistence_layer.load(frame_id, category)
                    if frame_data:
                        break

                if frame_data:
                    self.api_stats['requests_successful'] += 1
                    self.api_stats['frames_loaded'] += 1

                    return FrameResponse(
                        frame_id=frame_id,
                        frame_type="Unknown",  # Type info may not be preserved
                        frame_data=frame_data,
                        success=True,
                        message="Frame loaded successfully"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Frame {frame_id} not found"
                    )

            except HTTPException:
                self.api_stats['requests_failed'] += 1
                raise
            except Exception as e:
                self.api_stats['requests_failed'] += 1
                logger.error(f"❌ Load frame error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal server error: {str(e)}"
                )

        @app.post("/api/frames/search", response_model=FrameSearchResponse)
        async def search_frames(
            request: FrameSearchRequest,
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Search frames based on criteria"""
            self.api_stats['requests_total'] += 1
            self.api_stats['searches_performed'] += 1

            try:
                if not self.frame_persistence:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Frame persistence not available"
                    )

                # Convert date strings to datetime objects
                created_after = None
                if request.created_after:
                    created_after = datetime.fromisoformat(request.created_after.replace('Z', '+00:00'))

                # Perform search
                results = await self.frame_persistence.search_frames(
                    frame_type=request.frame_type,
                    confidence_threshold=request.confidence_threshold,
                    created_after=created_after,
                    limit=request.limit
                )

                self.api_stats['requests_successful'] += 1

                return FrameSearchResponse(
                    frames=results,
                    total_count=len(results),
                    search_criteria=request.dict(exclude_none=True),
                    timestamp=datetime.now().isoformat()
                )

            except HTTPException:
                self.api_stats['requests_failed'] += 1
                raise
            except Exception as e:
                self.api_stats['requests_failed'] += 1
                logger.error(f"❌ Search frames error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal server error: {str(e)}"
                )

        @app.get("/api/frames/{frame_id}/lineage", response_model=LineageResponse)
        async def get_frame_lineage(
            frame_id: str,
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Get the complete lineage of a frame"""
            self.api_stats['requests_total'] += 1
            self.api_stats['lineage_requests'] += 1

            try:
                if not self.frame_persistence:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Frame persistence not available"
                    )

                lineage = await self.frame_persistence.get_frame_lineage(frame_id)

                self.api_stats['requests_successful'] += 1

                return LineageResponse(
                    frame_id=frame_id,
                    lineage=lineage,
                    total_frames=len(lineage),
                    timestamp=datetime.now().isoformat()
                )

            except HTTPException:
                self.api_stats['requests_failed'] += 1
                raise
            except Exception as e:
                self.api_stats['requests_failed'] += 1
                logger.error(f"❌ Get lineage error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal server error: {str(e)}"
                )

        @app.get("/api/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            uptime = datetime.now() - self.start_time

            # Check component health
            memory_orchestrator_health = {
                'status': 'operational',
                'persistence_layer': self.persistence_layer is not None,
                'uptime_seconds': uptime.total_seconds()
            }

            frame_persistence_health = {
                'status': 'operational' if self.frame_persistence else 'unavailable',
                'local_cache': self.frame_persistence.enable_local_cache if self.frame_persistence else False
            }

            if self.frame_persistence:
                frame_persistence_health.update(self.frame_persistence.get_statistics())

            return HealthResponse(
                status="healthy",
                version=self.version,
                uptime=str(uptime),
                memory_orchestrator=memory_orchestrator_health,
                frame_persistence=frame_persistence_health,
                timestamp=datetime.now().isoformat()
            )

        @app.get("/api/statistics", response_model=StatisticsResponse)
        async def get_statistics(
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Get comprehensive statistics"""
            memory_orchestrator_stats = {
                'version': self.version,
                'uptime': str(datetime.now() - self.start_time),
                'persistence_available': self.persistence_layer is not None
            }

            frame_persistence_stats = {}
            if self.frame_persistence:
                frame_persistence_stats = self.frame_persistence.get_statistics()

            return StatisticsResponse(
                memory_orchestrator=memory_orchestrator_stats,
                frame_persistence=frame_persistence_stats,
                api_stats=self.api_stats.copy(),
                timestamp=datetime.now().isoformat()
            )

        @app.delete("/api/frames/{frame_id}")
        async def delete_frame(
            frame_id: str,
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Delete a frame (if supported by persistence layer)"""
            # Note: This would require implementing delete functionality in the persistence layer
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Frame deletion not yet implemented"
            )

        @app.post("/api/frames/cleanup")
        async def cleanup_old_frames(
            days_old: int = Query(30, description="Delete frames older than this many days"),
            token: str = Depends(get_auth_token) if self.enable_auth else None
        ):
            """Clean up old frames"""
            try:
                if not self.frame_persistence:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Frame persistence not available"
                    )

                deleted_count = await self.frame_persistence.cleanup_old_frames(days_old)

                return {
                    "message": f"Cleaned up {deleted_count} old frames",
                    "deleted_count": deleted_count,
                    "days_old": days_old,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Cleanup failed: {str(e)}"
                )

    async def start_server(self):
        """Start the API server"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    def run_server(self):
        """Run the API server (blocking)"""
        uvicorn.run(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_memory_orchestrator_api(
    host: str = "0.0.0.0",
    port: int = 8080,
    enable_auth: bool = False
) -> SCIAMemoryOrchestratorAPI:
    """Create and return a Memory Orchestrator API instance"""
    return SCIAMemoryOrchestratorAPI(
        host=host,
        port=port,
        enable_auth=enable_auth
    )

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SCIA Memory Orchestrator API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--auth", action="store_true", help="Enable authentication")
    parser.add_argument("--storage", default="./scia_memory_orchestrator", help="Local storage path")

    args = parser.parse_args()

    # Create and run the API server
    api = SCIAMemoryOrchestratorAPI(
        host=args.host,
        port=args.port,
        enable_auth=args.auth,
        local_storage_path=args.storage
    )

    print(f"[START] Starting SCIA Memory Orchestrator API on {args.host}:{args.port}")
    print(f"[DOCS] API Documentation: http://{args.host}:{args.port}/docs")
    print(f"[AUTH] Authentication: {'Enabled' if args.auth else 'Disabled'}")

    try:
        api.run_server()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")

# Export alias for compatibility
MemoryOrchestratorAPI = SCIAMemoryOrchestratorAPI
