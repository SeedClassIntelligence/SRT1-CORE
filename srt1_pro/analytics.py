"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: TRACING_AUDIT
Key Symbols: AnalyticsEngine, __init__, _ensure_dir, _load, _save ... and 6 more

Extracted Purposes:
  - AnalyticsEngine: SRT-1 Pro Analytics Engine
  - _load: Load persisted metrics.
  - _save: Persist metrics to disk.
  ...
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger("srt1.analytics")

class AnalyticsEngine:
    """
    SRT-1 Pro Analytics Engine
    Aggregates trace histories, seed lifecycles, and coherence trends to provide actionable
    insights for the developer dashboard.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._analytics_dir = os.path.join(self.repo_path, ".srt1", "analytics")
        self._db_path = os.path.join(self._analytics_dir, "metrics.json")
        self._ensure_dir()
        self._metrics = self._load()

    def _ensure_dir(self):
        if not os.path.exists(self._analytics_dir):
            os.makedirs(self._analytics_dir, exist_ok=True)
            
    def _load(self) -> Dict[str, Any]:
        """Load persisted metrics."""
        if os.path.exists(self._db_path):
            try:
                with open(self._db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load analytics DB: {e}")
                
        # Default starting metrics
        return {
            "total_seeds_planted": 0,
            "total_operations_logged": 0,
            "coherence_snaps": [],
            "daily_activity": {},
            "template_usage": {}
        }
        
    def _save(self):
        """Persist metrics to disk."""
        try:
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self._metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save analytics DB: {e}")

    def record_seed_planted(self, template_id: Optional[str] = None):
        """Record when a seed is planted and which template was used."""
        self._metrics["total_seeds_planted"] += 1
        
        # Track template usage
        tid = template_id or "custom"
        self._metrics["template_usage"][tid] = self._metrics["template_usage"].get(tid, 0) + 1
        
        self.record_daily_activity("seed_planted")
        self._save()
        
    def record_operation(self):
        """Record an operation being executed."""
        self._metrics["total_operations_logged"] += 1
        self.record_daily_activity("operation_logged")
        self._save()
        
    def record_coherence_snapshot(self, score: int, status: str):
        """Record a coherence score snapshot (e.g., from a forced reflection)."""
        now = datetime.now()
        self._metrics["coherence_snaps"].append({
            "timestamp": now.isoformat(),
            "score": score,
            "status": status
        })
        
        # Keep only the last 1000 snapshots to prevent unbounded growth
        if len(self._metrics["coherence_snaps"]) > 1000:
            self._metrics["coherence_snaps"] = self._metrics["coherence_snaps"][-1000:]
            
        self._save()

    def record_daily_activity(self, activity_type: str):
        """Track basic activity heatmaps by day."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self._metrics["daily_activity"]:
            self._metrics["daily_activity"][today] = {
                "seed_planted": 0,
                "operation_logged": 0
            }
        self._metrics["daily_activity"][today][activity_type] += 1

    # --- Read Queries ---
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Provides high-level stats for the analytics dashboard."""
        
        # Calculate trailing average coherence
        snaps = self._metrics["coherence_snaps"]
        avg_coherence = 0
        if snaps:
            # Avg of last 10 snaps
            recent = snaps[-10:]
            avg_coherence = sum(s["score"] for s in recent) / len(recent)
            
        return {
            "total_seeds": self._metrics.get("total_seeds_planted", 0),
            "total_operations": self._metrics.get("total_operations_logged", 0),
            "avg_coherence": round(avg_coherence, 1),
            "top_templates": dict(sorted(self._metrics.get("template_usage", {}).items(), key=lambda item: item[1], reverse=True)[:5])
        }
        
    def get_trends(self, days=30) -> Dict[str, Any]:
        """Provides time-series trends over the last X days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter snapshots
        trend_snaps = []
        for snap in self._metrics.get("coherence_snaps", []):
            try:
                snap_time = datetime.fromisoformat(snap["timestamp"])
                if snap_time >= cutoff:
                    trend_snaps.append(snap)
            except ValueError:
                pass
                
        # Filter daily activity
        activity = {}
        for day_str, counts in self._metrics.get("daily_activity", {}).items():
            try:
                dt = datetime.strptime(day_str, "%Y-%m-%d")
                if dt >= cutoff:
                    activity[day_str] = counts
            except ValueError:
                pass
                
        return {
            "coherence": trend_snaps,
            "activity": activity
        }
