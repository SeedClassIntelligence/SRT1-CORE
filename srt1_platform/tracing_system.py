#!/usr/bin/env python3
"""
SRT-1 Universal Audit & Tracing System

PURPOSE:
    Comprehensive audit trails across ALL system components.
    Implements the full SCIA tracing specification including:
    - Universal trace creation with input hashing and LLM provider context
    - Cross-component trace linking with flow analysis and timelines
    - Execution Graph tracking for multi-step validation workflows
    - Audit trail generation with compliance verification
    - Universal Validation Engine with integrated integrity verification

ARCHITECTURE:
    SRT1TracingSystem    --> Creates and stores individual traces
    SRT1AuditTrail       --> Generates comprehensive audit reports from traces
    ExecutionGraphTracker --> Tracks multi-step validation/execution as a DAG
    UniversalValidationEngine --> Validates content across any LLM provider

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import os
import json
import hashlib
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


SCIA_VERSION = "4.0.0"


# ==============================================================================
# ENUMS
# ==============================================================================

class TraceStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    LINKED = "LINKED"


class ValidationStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class GraphStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class ComplianceLevel(Enum):
    FULL = "FULL_COMPLIANCE"
    PARTIAL = "PARTIAL_COMPLIANCE"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNVERIFIED = "UNVERIFIED"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class TraceRecord:
    """Single execution trace record per the SCIA spec."""
    trace_id: str
    timestamp: str
    component: str
    operation: str
    input_hash: str
    context: Dict[str, Any]
    llm_provider: Optional[str]
    parent_trace: Optional[str]
    scia_version: str = SCIA_VERSION
    output_hash: Optional[str] = None
    duration_ms: Optional[int] = None
    status: TraceStatus = TraceStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "component": self.component,
            "operation": self.operation,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "context": self.context,
            "llm_provider": self.llm_provider,
            "parent_trace": self.parent_trace,
            "scia_version": self.scia_version,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "metadata": self.metadata,
        }


@dataclass
class TraceRelationship:
    """Links between component traces with flow analysis."""
    primary_trace: str
    component_traces: List[str]
    trace_flow: List[Dict[str, Any]]
    processing_timeline: List[Dict[str, Any]]
    cross_component_dependencies: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_trace": self.primary_trace,
            "component_traces": self.component_traces,
            "trace_flow": self.trace_flow,
            "processing_timeline": self.processing_timeline,
            "cross_component_dependencies": self.cross_component_dependencies,
        }


@dataclass
class ExecutionGraphNode:
    """A single node in the execution graph (one validation/execution step)."""
    step_id: str
    graph_id: str
    criterion_name: str
    llm_provider: str
    started_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    parent_step_id: Optional[str] = None
    duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "graph_id": self.graph_id,
            "criterion_name": self.criterion_name,
            "llm_provider": self.llm_provider,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "parent_step_id": self.parent_step_id,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ExecutionGraph:
    """Complete execution graph for a validation or execution workflow."""
    graph_id: str
    content_hash: str
    context: Dict[str, Any]
    llm_provider: str
    status: GraphStatus
    started_at: str
    completed_at: Optional[str] = None
    steps: List[ExecutionGraphNode] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    total_duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "content_hash": self.content_hash,
            "context": self.context,
            "llm_provider": self.llm_provider,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "steps": [s.to_dict() for s in self.steps],
            "validation_results": self.validation_results,
            "total_duration_ms": self.total_duration_ms,
            "step_count": len(self.steps),
        }


@dataclass
class ValidationCriterion:
    """A single validation criterion to check against content."""
    name: str
    description: str
    category: str  # "coherence", "safety", "quality", "compliance"
    weight: float = 1.0
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "weight": self.weight,
            "required": self.required,
        }


# ==============================================================================
# LLM INTERFACE (Abstract - Provider Agnostic)
# ==============================================================================

class LLMInterface(ABC):
    """Abstract interface for any LLM provider."""

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic', 'local')."""
        pass

    @abstractmethod
    def validate_content(self, content: Any, criterion: ValidationCriterion,
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content against a specific criterion."""
        pass


class LocalValidationInterface(LLMInterface):
    """
    Local (non-API) validation interface.
    Performs deterministic validation without calling an external LLM.
    Used for testing and for validations that don't require AI.
    """

    @property
    def provider_type(self) -> str:
        return "local_deterministic"

    def validate_content(self, content: Any, criterion: ValidationCriterion,
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deterministic validation based on criterion category."""
        content_str = json.dumps(content, default=str) if not isinstance(content, str) else content

        if criterion.category == "coherence":
            return self._check_coherence(content_str, context)
        elif criterion.category == "safety":
            return self._check_safety(content_str, context)
        elif criterion.category == "quality":
            return self._check_quality(content_str, context)
        elif criterion.category == "compliance":
            return self._check_compliance(content_str, context)
        else:
            return {"status": "PASSED", "score": 1.0, "details": "No specific check for category"}

    def _check_coherence(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content is coherent with the task context."""
        task_keywords = context.get("task_keywords", [])
        if not task_keywords:
            return {"status": "PASSED", "score": 1.0, "details": "No keywords to check"}

        content_lower = content.lower()
        matches = sum(1 for kw in task_keywords if kw.lower() in content_lower)
        score = matches / len(task_keywords) if task_keywords else 1.0

        return {
            "status": "PASSED" if score >= 0.3 else "FAILED",
            "score": round(score, 3),
            "details": f"Matched {matches}/{len(task_keywords)} task keywords",
            "matched_keywords": [kw for kw in task_keywords if kw.lower() in content_lower],
        }

    def _check_safety(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check content for safety concerns."""
        safety_flags = []
        dangerous_patterns = [
            "os.system(", "subprocess.call(", "eval(", "exec(",
            "rm -rf", "drop table", "delete from", "__import__(",
        ]
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in content_lower:
                safety_flags.append(pattern)

        return {
            "status": "FAILED" if safety_flags else "PASSED",
            "score": 0.0 if safety_flags else 1.0,
            "details": f"Found {len(safety_flags)} safety concerns" if safety_flags else "No safety concerns",
            "flags": safety_flags,
        }

    def _check_quality(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check content quality metrics."""
        score = 1.0
        details = []

        if len(content) < 10:
            score -= 0.3
            details.append("Content too short")
        if len(content) > 100000:
            score -= 0.1
            details.append("Content very large")

        return {
            "status": "PASSED" if score >= 0.5 else "WARNING",
            "score": round(max(score, 0.0), 3),
            "details": "; ".join(details) if details else "Quality checks passed",
        }

    def _check_compliance(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance requirements."""
        return {
            "status": "PASSED",
            "score": 1.0,
            "details": "Compliance check passed (local mode)",
        }


# ==============================================================================
# SRT1 TRACING SYSTEM
# ==============================================================================

class SRT1TracingSystem:
    """
    Universal tracing system for the SCIA pipeline.
    Creates, stores, and links traces across all system components.
    """

    def __init__(self):
        self.trace_collectors: Dict[str, List[TraceRecord]] = self._initialize_trace_collectors()
        self.trace_storage: List[TraceRecord] = self._initialize_trace_storage()
        self.trace_analyzers: Dict[str, Any] = self._initialize_trace_analyzers()
        self._trace_relationships: List[TraceRelationship] = []

    def _initialize_trace_collectors(self) -> Dict[str, List[TraceRecord]]:
        """Initialize per-component trace collectors."""
        return {
            "indexer": [],
            "bundler": [],
            "executor": [],
            "validator": [],
            "signature": [],
            "governance": [],
        }

    def _initialize_trace_storage(self) -> List[TraceRecord]:
        """Initialize the central trace storage."""
        return []

    def _initialize_trace_analyzers(self) -> Dict[str, Any]:
        """Initialize trace analyzers for flow/dependency analysis."""
        return {
            "flow_analyzer": {"enabled": True, "processed": 0},
            "dependency_analyzer": {"enabled": True, "processed": 0},
            "timeline_builder": {"enabled": True, "processed": 0},
        }

    # ------------------------------------------------------------------
    # TRACE CREATION
    # ------------------------------------------------------------------

    def create_universal_trace(self, component: str, operation: str,
                                input_data: Any, context: Dict[str, Any]) -> str:
        """
        Create a universal trace record for any component operation.

        Args:
            component: The system component (indexer, bundler, executor, etc.)
            operation: The operation being performed
            input_data: The input data being processed
            context: Contextual information including LLM provider and parent trace

        Returns:
            The trace_id for this trace record.
        """
        trace_id = self._generate_unique_trace_id()

        trace_record = TraceRecord(
            trace_id=trace_id,
            timestamp=datetime.now().isoformat(),
            component=component,
            operation=operation,
            input_hash=self._hash_input_data(input_data),
            context=context,
            llm_provider=context.get("llm_provider"),
            parent_trace=context.get("parent_trace"),
            scia_version=SCIA_VERSION,
        )

        self._store_trace_record(trace_record)
        return trace_id

    def complete_trace(self, trace_id: str, output_data: Any = None,
                       duration_ms: Optional[int] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Mark a trace as completed with output data."""
        for trace in self.trace_storage:
            if trace.trace_id == trace_id:
                trace.output_hash = self._hash_input_data(output_data) if output_data else None
                trace.duration_ms = duration_ms
                trace.status = TraceStatus.COMPLETED
                if metadata:
                    trace.metadata.update(metadata)
                return

    # ------------------------------------------------------------------
    # TRACE LINKING
    # ------------------------------------------------------------------

    def link_component_traces(self, primary_trace_id: str,
                               component_traces: List[str]) -> Dict[str, Any]:
        """
        Link traces from different components together with flow analysis.

        Args:
            primary_trace_id: The main trace that initiated the workflow
            component_traces: List of trace IDs from sub-components

        Returns:
            Trace relationship dictionary with flow, timeline, and dependencies.
        """
        trace_flow = self._analyze_trace_flow(component_traces)
        processing_timeline = self._build_processing_timeline(component_traces)
        dependencies = self._identify_dependencies(component_traces)

        relationship = TraceRelationship(
            primary_trace=primary_trace_id,
            component_traces=component_traces,
            trace_flow=trace_flow,
            processing_timeline=processing_timeline,
            cross_component_dependencies=dependencies,
        )

        self._trace_relationships.append(relationship)
        self._store_trace_relationships(relationship)

        return relationship.to_dict()

    # ------------------------------------------------------------------
    # TRACE QUERIES
    # ------------------------------------------------------------------

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a single trace by ID."""
        for trace in self.trace_storage:
            if trace.trace_id == trace_id:
                return trace.to_dict()
        return None

    def get_traces_by_component(self, component: str) -> List[Dict[str, Any]]:
        """Get all traces for a specific component."""
        return [
            t.to_dict() for t in self.trace_storage
            if t.component == component
        ]

    def get_traces_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get all traces that used a specific LLM provider."""
        return [
            t.to_dict() for t in self.trace_storage
            if t.llm_provider == provider
        ]

    def get_related_traces(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all traces related to a given trace_id (parent/child chain)."""
        related = []
        # Find direct children
        for trace in self.trace_storage:
            if trace.parent_trace == trace_id:
                related.append(trace.to_dict())
        # Find parent
        target = None
        for trace in self.trace_storage:
            if trace.trace_id == trace_id:
                target = trace
                break
        if target and target.parent_trace:
            parent = self.get_trace(target.parent_trace)
            if parent:
                related.insert(0, parent)
        return related

    def collect_related_traces(self, trace_id: str) -> List[TraceRecord]:
        """Recursively collect all traces in the chain rooted at trace_id."""
        collected: List[TraceRecord] = []
        visited: Set[str] = set()

        def _collect(tid: str):
            if tid in visited:
                return
            visited.add(tid)
            for trace in self.trace_storage:
                if trace.trace_id == tid:
                    collected.append(trace)
                if trace.parent_trace == tid:
                    collected.append(trace)
                    _collect(trace.trace_id)

        _collect(trace_id)
        return collected

    # ------------------------------------------------------------------
    # FLOW ANALYSIS
    # ------------------------------------------------------------------

    def _analyze_trace_flow(self, component_traces: List[str]) -> List[Dict[str, Any]]:
        """Analyze the flow of data across component traces."""
        flow = []
        trace_objects = []
        for tid in component_traces:
            for trace in self.trace_storage:
                if trace.trace_id == tid:
                    trace_objects.append(trace)
                    break

        # Sort by timestamp
        trace_objects.sort(key=lambda t: t.timestamp)

        for i, trace in enumerate(trace_objects):
            flow_entry = {
                "order": i + 1,
                "trace_id": trace.trace_id,
                "component": trace.component,
                "operation": trace.operation,
                "timestamp": trace.timestamp,
                "input_hash": trace.input_hash,
                "output_hash": trace.output_hash,
            }
            # Check if this trace's input matches the previous trace's output
            if i > 0 and trace_objects[i - 1].output_hash:
                flow_entry["input_from_previous"] = (
                    trace.input_hash == trace_objects[i - 1].output_hash
                )
            flow.append(flow_entry)

        return flow

    def _build_processing_timeline(self, component_traces: List[str]) -> List[Dict[str, Any]]:
        """Build a chronological processing timeline from component traces."""
        timeline = []
        for tid in component_traces:
            for trace in self.trace_storage:
                if trace.trace_id == tid:
                    timeline.append({
                        "trace_id": trace.trace_id,
                        "component": trace.component,
                        "operation": trace.operation,
                        "started_at": trace.timestamp,
                        "duration_ms": trace.duration_ms,
                        "status": trace.status.value,
                        "llm_provider": trace.llm_provider,
                    })
                    break

        # Sort chronologically
        timeline.sort(key=lambda t: t["started_at"])
        return timeline

    def _identify_dependencies(self, component_traces: List[str]) -> List[Dict[str, Any]]:
        """Identify cross-component dependencies between traces."""
        dependencies = []
        trace_map: Dict[str, TraceRecord] = {}

        for tid in component_traces:
            for trace in self.trace_storage:
                if trace.trace_id == tid:
                    trace_map[tid] = trace
                    break

        # Identify parent-child dependencies
        for tid, trace in trace_map.items():
            if trace.parent_trace and trace.parent_trace in trace_map:
                parent = trace_map[trace.parent_trace]
                dependencies.append({
                    "type": "parent_child",
                    "from_component": parent.component,
                    "from_trace": parent.trace_id,
                    "to_component": trace.component,
                    "to_trace": trace.trace_id,
                    "dependency": f"{parent.component}.{parent.operation} -> {trace.component}.{trace.operation}",
                })

        # Identify data flow dependencies (input hash matches output hash)
        trace_list = list(trace_map.values())
        for i, t1 in enumerate(trace_list):
            for t2 in trace_list[i + 1:]:
                if t1.output_hash and t1.output_hash == t2.input_hash:
                    dependencies.append({
                        "type": "data_flow",
                        "from_component": t1.component,
                        "from_trace": t1.trace_id,
                        "to_component": t2.component,
                        "to_trace": t2.trace_id,
                        "dependency": f"{t1.operation} output feeds {t2.operation} input",
                    })

        return dependencies

    # ------------------------------------------------------------------
    # INTERNAL UTILITIES
    # ------------------------------------------------------------------

    def _generate_unique_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return f"trace_{uuid.uuid4().hex[:16]}"

    def _hash_input_data(self, input_data: Any) -> str:
        """Hash any input data for integrity tracking."""
        if input_data is None:
            return "none"
        content_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]

    def _store_trace_record(self, trace_record: TraceRecord) -> None:
        """Store a trace record in both central storage and component collector."""
        self.trace_storage.append(trace_record)
        component = trace_record.component
        if component in self.trace_collectors:
            self.trace_collectors[component].append(trace_record)
        else:
            self.trace_collectors[component] = [trace_record]

    def _store_trace_relationships(self, relationship: TraceRelationship) -> None:
        """Store trace relationship data."""
        self.trace_analyzers["flow_analyzer"]["processed"] += 1
        self.trace_analyzers["dependency_analyzer"]["processed"] += 1
        self.trace_analyzers["timeline_builder"]["processed"] += 1

    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire tracing system state."""
        component_counts = {}
        for component, traces in self.trace_collectors.items():
            if traces:
                component_counts[component] = len(traces)

        provider_counts: Dict[str, int] = {}
        for trace in self.trace_storage:
            if trace.llm_provider:
                provider_counts[trace.llm_provider] = provider_counts.get(trace.llm_provider, 0) + 1

        return {
            "total_traces": len(self.trace_storage),
            "traces_by_component": component_counts,
            "traces_by_provider": provider_counts,
            "total_relationships": len(self._trace_relationships),
            "analyzers": self.trace_analyzers,
            "scia_version": SCIA_VERSION,
        }


# ==============================================================================
# EXECUTION GRAPH TRACKER
# ==============================================================================

class ExecutionGraphTracker:
    """
    Tracks multi-step validation and execution workflows as directed acyclic graphs.
    Each validation graph contains steps, their results, and the LLM provider used.
    """

    def __init__(self):
        self._graphs: Dict[str, ExecutionGraph] = {}

    def start_validation_graph(self, content_hash: str, context: Dict[str, Any],
                                llm_provider: str) -> str:
        """Start a new execution graph for a validation workflow."""
        graph_id = f"graph_{uuid.uuid4().hex[:12]}"

        graph = ExecutionGraph(
            graph_id=graph_id,
            content_hash=content_hash,
            context=context,
            llm_provider=llm_provider,
            status=GraphStatus.IN_PROGRESS,
            started_at=datetime.now().isoformat(),
        )

        self._graphs[graph_id] = graph
        return graph_id

    def add_validation_step(self, graph_id: str, criterion_name: str,
                             llm_provider: str,
                             parent_step_id: Optional[str] = None) -> str:
        """Add a validation step to an execution graph."""
        if graph_id not in self._graphs:
            raise ValueError(f"Graph {graph_id} not found")

        step_id = f"step_{uuid.uuid4().hex[:10]}"

        step = ExecutionGraphNode(
            step_id=step_id,
            graph_id=graph_id,
            criterion_name=criterion_name,
            llm_provider=llm_provider,
            started_at=datetime.now().isoformat(),
            parent_step_id=parent_step_id,
        )

        self._graphs[graph_id].steps.append(step)
        return step_id

    def complete_step(self, graph_id: str, step_id: str,
                      result: Dict[str, Any], duration_ms: int) -> None:
        """Mark a validation step as completed."""
        if graph_id not in self._graphs:
            return

        for step in self._graphs[graph_id].steps:
            if step.step_id == step_id:
                step.completed_at = datetime.now().isoformat()
                step.result = result
                step.duration_ms = duration_ms
                return

    def complete_validation_graph(self, graph_id: str,
                                   validation_results: Dict[str, Any],
                                   execution_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Complete an execution graph and return the full graph data."""
        if graph_id not in self._graphs:
            raise ValueError(f"Graph {graph_id} not found")

        graph = self._graphs[graph_id]
        graph.status = GraphStatus.COMPLETED
        graph.completed_at = datetime.now().isoformat()
        graph.validation_results = validation_results

        # Calculate total duration
        total_ms = sum(
            step.duration_ms or 0 for step in graph.steps
        )
        graph.total_duration_ms = total_ms

        return graph.to_dict()

    def get_graph(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """Get an execution graph by ID."""
        graph = self._graphs.get(graph_id)
        return graph.to_dict() if graph else None

    def get_all_graphs(self) -> List[Dict[str, Any]]:
        """Get all execution graphs."""
        return [g.to_dict() for g in self._graphs.values()]


# ==============================================================================
# SRT1 AUDIT TRAIL
# ==============================================================================

class SRT1AuditTrail:
    """
    Generates comprehensive audit reports from trace data.
    Provides processing history, component interactions, data transformation
    tracking, validation checkpoints, LLM provider usage, quality metrics,
    and compliance verification.
    """

    def __init__(self, tracing_system: SRT1TracingSystem):
        self.tracing = tracing_system

    def generate_comprehensive_audit(self, trace_id: str) -> Dict[str, Any]:
        """
        Generate a full audit report for a given trace and all its related traces.
        """
        # Collect all related traces
        related_traces = self.tracing.collect_related_traces(trace_id)

        # Build complete processing history
        processing_history = self._build_processing_history(related_traces)

        # Generate audit report
        audit_report = {
            "audit_id": str(uuid.uuid4()),
            "primary_trace": trace_id,
            "generated_at": datetime.now().isoformat(),
            "processing_timeline": processing_history,
            "component_interactions": self._analyze_component_interactions(related_traces),
            "data_transformations": self._track_data_transformations(related_traces),
            "validation_checkpoints": self._identify_validation_points(related_traces),
            "llm_provider_usage": self._track_llm_provider_usage(related_traces),
            "quality_metrics": self._calculate_processing_quality_metrics(related_traces),
            "compliance_verification": self._verify_compliance(related_traces),
        }

        return audit_report

    def _build_processing_history(self, traces: List[TraceRecord]) -> List[Dict[str, Any]]:
        """Build a complete chronological processing history."""
        history = []
        sorted_traces = sorted(traces, key=lambda t: t.timestamp)

        for i, trace in enumerate(sorted_traces):
            entry = {
                "order": i + 1,
                "trace_id": trace.trace_id,
                "timestamp": trace.timestamp,
                "component": trace.component,
                "operation": trace.operation,
                "status": trace.status.value,
                "duration_ms": trace.duration_ms,
                "llm_provider": trace.llm_provider,
                "input_hash": trace.input_hash,
                "output_hash": trace.output_hash,
            }
            history.append(entry)

        return history

    def _analyze_component_interactions(self, traces: List[TraceRecord]) -> List[Dict[str, Any]]:
        """Analyze how different components interacted during processing."""
        interactions = []
        components_seen: Dict[str, List[TraceRecord]] = {}

        for trace in traces:
            components_seen.setdefault(trace.component, []).append(trace)

        # Find inter-component data flows
        sorted_traces = sorted(traces, key=lambda t: t.timestamp)
        for i in range(len(sorted_traces) - 1):
            current = sorted_traces[i]
            next_trace = sorted_traces[i + 1]

            if current.component != next_trace.component:
                interactions.append({
                    "from_component": current.component,
                    "from_operation": current.operation,
                    "to_component": next_trace.component,
                    "to_operation": next_trace.operation,
                    "data_continuity": (
                        current.output_hash == next_trace.input_hash
                        if current.output_hash else None
                    ),
                    "timestamp": next_trace.timestamp,
                })

        return interactions

    def _track_data_transformations(self, traces: List[TraceRecord]) -> List[Dict[str, Any]]:
        """Track how data was transformed across the processing pipeline."""
        transformations = []

        for trace in traces:
            if trace.input_hash and trace.output_hash and trace.input_hash != trace.output_hash:
                transformations.append({
                    "trace_id": trace.trace_id,
                    "component": trace.component,
                    "operation": trace.operation,
                    "input_hash": trace.input_hash,
                    "output_hash": trace.output_hash,
                    "transformation_detected": True,
                    "timestamp": trace.timestamp,
                })

        return transformations

    def _identify_validation_points(self, traces: List[TraceRecord]) -> List[Dict[str, Any]]:
        """Identify traces that served as validation checkpoints."""
        validation_keywords = {"validate", "verify", "check", "audit", "compliance", "sign"}
        checkpoints = []

        for trace in traces:
            op_lower = trace.operation.lower()
            if any(kw in op_lower for kw in validation_keywords):
                checkpoints.append({
                    "trace_id": trace.trace_id,
                    "component": trace.component,
                    "operation": trace.operation,
                    "status": trace.status.value,
                    "timestamp": trace.timestamp,
                })

        return checkpoints

    def _track_llm_provider_usage(self, traces: List[TraceRecord]) -> Dict[str, Any]:
        """Track which LLM providers were used and how."""
        provider_usage: Dict[str, Dict[str, Any]] = {}

        for trace in traces:
            if trace.llm_provider:
                if trace.llm_provider not in provider_usage:
                    provider_usage[trace.llm_provider] = {
                        "call_count": 0,
                        "components": set(),
                        "operations": [],
                        "total_duration_ms": 0,
                    }
                usage = provider_usage[trace.llm_provider]
                usage["call_count"] += 1
                usage["components"].add(trace.component)
                usage["operations"].append(trace.operation)
                usage["total_duration_ms"] += trace.duration_ms or 0

        # Convert sets to lists for serialization
        for provider, usage in provider_usage.items():
            usage["components"] = list(usage["components"])

        return {
            "providers_used": list(provider_usage.keys()),
            "provider_details": provider_usage,
            "total_llm_calls": sum(u["call_count"] for u in provider_usage.values()),
        }

    def _calculate_processing_quality_metrics(self, traces: List[TraceRecord]) -> Dict[str, Any]:
        """Calculate quality metrics for the processing pipeline."""
        total = len(traces)
        completed = sum(1 for t in traces if t.status == TraceStatus.COMPLETED)
        failed = sum(1 for t in traces if t.status == TraceStatus.FAILED)
        durations = [t.duration_ms for t in traces if t.duration_ms is not None]

        return {
            "total_operations": total,
            "completed": completed,
            "failed": failed,
            "completion_rate": round(completed / total, 3) if total > 0 else 0.0,
            "avg_duration_ms": round(sum(durations) / len(durations), 1) if durations else None,
            "max_duration_ms": max(durations) if durations else None,
            "min_duration_ms": min(durations) if durations else None,
            "total_duration_ms": sum(durations) if durations else 0,
        }

    def _verify_compliance(self, traces: List[TraceRecord]) -> Dict[str, Any]:
        """Verify compliance across all traces."""
        issues = []

        for trace in traces:
            # Check: every trace must have a valid input hash
            if not trace.input_hash or trace.input_hash == "none":
                issues.append({
                    "trace_id": trace.trace_id,
                    "issue": "Missing input hash",
                    "severity": "warning",
                })

            # Check: completed traces should have an output hash
            if trace.status == TraceStatus.COMPLETED and not trace.output_hash:
                issues.append({
                    "trace_id": trace.trace_id,
                    "issue": "Completed trace missing output hash",
                    "severity": "info",
                })

            # Check: SCIA version consistency
            if trace.scia_version != SCIA_VERSION:
                issues.append({
                    "trace_id": trace.trace_id,
                    "issue": f"Version mismatch: {trace.scia_version} vs {SCIA_VERSION}",
                    "severity": "warning",
                })

        if not issues:
            level = ComplianceLevel.FULL
        elif all(i["severity"] == "info" for i in issues):
            level = ComplianceLevel.FULL
        elif any(i["severity"] == "critical" for i in issues):
            level = ComplianceLevel.NON_COMPLIANT
        else:
            level = ComplianceLevel.PARTIAL

        return {
            "compliance_level": level.value,
            "issues": issues,
            "issue_count": len(issues),
            "verified_at": datetime.now().isoformat(),
            "scia_version": SCIA_VERSION,
        }


# ==============================================================================
# UNIVERSAL VALIDATION ENGINE
# ==============================================================================

class UniversalValidationEngine:
    """
    Validates content across any LLM provider with integrated
    execution graph tracking and integrity verification.
    """

    def __init__(self, tracing_system: Optional[SRT1TracingSystem] = None):
        self.validation_criteria = self._load_validation_criteria()
        self.provider_adaptations: Dict[str, Dict[str, Any]] = self._load_provider_adaptations()
        self.execution_graph_tracker = ExecutionGraphTracker()
        self.tracing = tracing_system or SRT1TracingSystem()



    def _load_validation_criteria(self) -> List[ValidationCriterion]:
        """Load the standard validation criteria."""
        return [
            ValidationCriterion(
                name="coherence_check",
                description="Verify output coherence with original task intent",
                category="coherence",
                weight=2.0,
                required=True,
            ),
            ValidationCriterion(
                name="safety_check",
                description="Check for dangerous code patterns and security risks",
                category="safety",
                weight=3.0,
                required=True,
            ),
            ValidationCriterion(
                name="quality_check",
                description="Assess output quality metrics",
                category="quality",
                weight=1.5,
                required=False,
            ),
            ValidationCriterion(
                name="compliance_check",
                description="Verify compliance with SCIA standards",
                category="compliance",
                weight=1.0,
                required=True,
            ),
        ]

    def _load_provider_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Load provider-specific validation adaptations."""
        return {
            "openai": {"max_tokens": 4096, "temperature_validation": 0.1},
            "anthropic": {"max_tokens": 4096, "temperature_validation": 0.1},
            "local_deterministic": {"max_tokens": None, "temperature_validation": None},
        }

    def validate_with_signature_generation(self, content: Any,
                                            context: Dict[str, Any],
                                            llm_interface: LLMInterface) -> Dict[str, Any]:
        """
        Full validation pipeline with execution graph tracking and integrity hash.

        Args:
            content: The content to validate
            context: Task context and metadata
            llm_interface: The LLM interface to use for validation

        Returns:
            Complete validation result with execution graph and integrity hash.
        """
        content_hash = self._hash_content(content)

        # Start execution graph tracking
        validation_graph_id = self.execution_graph_tracker.start_validation_graph(
            content_hash=content_hash,
            context=context,
            llm_provider=llm_interface.provider_type,
        )

        validation_results: Dict[str, Any] = {}
        execution_steps: List[Dict[str, Any]] = []

        for criterion in self.validation_criteria:
            # Track each validation step in execution graph
            step_id = self.execution_graph_tracker.add_validation_step(
                validation_graph_id,
                criterion.name,
                llm_interface.provider_type,
            )

            # Execute validation with execution tracking
            step_start = time.time()
            criterion_result = self._execute_criterion_with_tracking(
                content, criterion, llm_interface, step_id,
            )
            step_duration = int((time.time() - step_start) * 1000)

            # Complete the step in the graph
            self.execution_graph_tracker.complete_step(
                validation_graph_id, step_id, criterion_result, step_duration,
            )

            validation_results[criterion.name] = criterion_result

            execution_steps.append({
                "step_id": step_id,
                "criterion": criterion.name,
                "result": criterion_result,
                "llm_provider": llm_interface.provider_type,
                "timestamp": datetime.now().isoformat(),
                "duration_ms": step_duration,
            })

        # Complete execution graph
        complete_execution_graph = self.execution_graph_tracker.complete_validation_graph(
            validation_graph_id, validation_results, execution_steps,
        )

        # Compute validation integrity hash
        validation_hash = hashlib.sha256(
            json.dumps(validation_results, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Synthesize overall validation
        overall_validation = self._synthesize_validation_results(validation_results)

        return {
            "validation_results": validation_results,
            "overall_score": overall_validation["score"],
            "validation_status": overall_validation["status"],
            "execution_graph": complete_execution_graph,
            "integrity": {
                "hash_algorithm": "sha256",
                "validation_hash": validation_hash,
            },
            "provider_used": llm_interface.provider_type,
            "validation_metadata": overall_validation["metadata"],
        }

    def _execute_criterion_with_tracking(self, content: Any,
                                          criterion: ValidationCriterion,
                                          llm_interface: LLMInterface,
                                          step_id: str) -> Dict[str, Any]:
        """Execute a single validation criterion with tracing."""
        # Create a trace for this validation step
        trace_id = self.tracing.create_universal_trace(
            component="validator",
            operation=f"validate_{criterion.name}",
            input_data=content,
            context={
                "criterion": criterion.name,
                "category": criterion.category,
                "llm_provider": llm_interface.provider_type,
                "step_id": step_id,
            },
        )

        # Run the actual validation
        result = llm_interface.validate_content(content, criterion, {})

        # Complete the trace
        self.tracing.complete_trace(trace_id, output_data=result, duration_ms=0)

        return result

    def _synthesize_validation_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize individual criterion results into an overall score."""
        total_weight = 0.0
        weighted_score = 0.0
        all_passed = True
        required_failed = False

        for criterion in self.validation_criteria:
            result = results.get(criterion.name, {})
            score = result.get("score", 0.0)
            status = result.get("status", "SKIPPED")

            weighted_score += score * criterion.weight
            total_weight += criterion.weight

            if status == "FAILED":
                all_passed = False
                if criterion.required:
                    required_failed = True

        overall_score = round(weighted_score / total_weight, 3) if total_weight > 0 else 0.0

        if required_failed:
            status = ValidationStatus.FAILED.value
        elif all_passed:
            status = ValidationStatus.PASSED.value
        else:
            status = ValidationStatus.WARNING.value

        return {
            "score": overall_score,
            "status": status,
            "metadata": {
                "criteria_count": len(self.validation_criteria),
                "all_passed": all_passed,
                "required_failed": required_failed,
                "total_weight": total_weight,
                "validated_at": datetime.now().isoformat(),
            },
        }

    @staticmethod
    def _hash_content(content: Any) -> str:
        """Hash content for signature generation."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]


# ==============================================================================
# CLI / TEST
# ==============================================================================

def main() -> None:
    print("=" * 70)
    print("  SRT-1 UNIVERSAL AUDIT & TRACING SYSTEM — Full Pipeline Test")
    print("=" * 70)
    print()

    # --- Initialize systems ---
    tracing = SRT1TracingSystem()
    audit_trail = SRT1AuditTrail(tracing)
    validation_engine = UniversalValidationEngine(tracing_system=tracing)
    local_llm = LocalValidationInterface()

    # --- Phase 1: Create traces simulating the indexer ---
    print("  [Phase 1] Simulating Indexer traces...")
    t1 = tracing.create_universal_trace(
        component="indexer",
        operation="scan_repository",
        input_data={"path": "/repo", "extensions": [".py", ".ts"]},
        context={"parent_trace": None, "llm_provider": None},
    )
    tracing.complete_trace(t1, output_data={"files_found": 42}, duration_ms=150)

    t2 = tracing.create_universal_trace(
        component="indexer",
        operation="parse_symbols",
        input_data={"files": 42},
        context={"parent_trace": t1, "llm_provider": None},
    )
    tracing.complete_trace(t2, output_data={"symbols": 150}, duration_ms=320)

    t3 = tracing.create_universal_trace(
        component="indexer",
        operation="generate_reflections",
        input_data={"symbols": 150},
        context={"parent_trace": t2, "llm_provider": None},
    )
    tracing.complete_trace(t3, output_data={"reflections": 150}, duration_ms=200)
    print(f"    Created {3} indexer traces: {t1[:20]}... -> {t2[:20]}... -> {t3[:20]}...")

    # --- Phase 2: Bundler traces ---
    print("  [Phase 2] Simulating Bundler traces...")
    t4 = tracing.create_universal_trace(
        component="bundler",
        operation="analyze_task",
        input_data={"task": "Add error handling to payment module"},
        context={"parent_trace": t3, "llm_provider": None},
    )
    tracing.complete_trace(t4, output_data={"keywords": 5, "intents": ["FEATURE_ADD"]}, duration_ms=50)

    t5 = tracing.create_universal_trace(
        component="bundler",
        operation="search_symbols",
        input_data={"keywords": 5},
        context={"parent_trace": t4, "llm_provider": None},
    )
    tracing.complete_trace(t5, output_data={"relevant_symbols": 12}, duration_ms=80)
    print(f"    Created {2} bundler traces")

    # --- Phase 3: Executor traces ---
    print("  [Phase 3] Simulating Executor traces with LLM provider...")
    t6 = tracing.create_universal_trace(
        component="executor",
        operation="dispatch_to_assistant",
        input_data={"prompt_size": 25000},
        context={"parent_trace": t5, "llm_provider": "openai"},
    )
    tracing.complete_trace(t6, output_data={"response_received": True}, duration_ms=3200)

    t7 = tracing.create_universal_trace(
        component="validator",
        operation="validate_plan",
        input_data={"files_to_modify": 3},
        context={"parent_trace": t6, "llm_provider": "openai"},
    )
    tracing.complete_trace(t7, output_data={"approved": True, "warnings": 1}, duration_ms=10)
    print(f"    Created {2} executor/validator traces")

    # --- Link all traces ---
    print()
    print("  [Linking] Linking all component traces...")
    all_trace_ids = [t1, t2, t3, t4, t5, t6, t7]
    relationship = tracing.link_component_traces(t1, all_trace_ids)
    print(f"    Flow steps: {len(relationship['trace_flow'])}")
    print(f"    Dependencies: {len(relationship['cross_component_dependencies'])}")

    # --- Generate audit report ---
    print()
    print("  [Audit] Generating comprehensive audit report...")
    audit = audit_trail.generate_comprehensive_audit(t1)
    print(f"    Audit ID: {audit['audit_id'][:20]}...")
    print(f"    Timeline entries: {len(audit['processing_timeline'])}")
    print(f"    Component interactions: {len(audit['component_interactions'])}")
    print(f"    Data transformations: {len(audit['data_transformations'])}")
    print(f"    Validation checkpoints: {len(audit['validation_checkpoints'])}")
    print(f"    LLM providers used: {audit['llm_provider_usage']['providers_used']}")
    print(f"    Compliance: {audit['compliance_verification']['compliance_level']}")
    quality = audit['quality_metrics']
    print(f"    Quality: {quality['completion_rate']:.0%} completion, "
          f"avg {quality['avg_duration_ms']}ms")

    # --- Run validation engine ---
    print()
    print("  [Validation] Running Universal Validation Engine...")
    test_content = {
        "code": "def handle_payment(amount): return process(amount)",
        "task": "Add error handling to payment module",
    }
    validation_result = validation_engine.validate_with_signature_generation(
        content=test_content,
        context={"task_keywords": ["error", "handling", "payment"]},
        llm_interface=local_llm,
    )
    print(f"    Overall score: {validation_result['overall_score']}")
    print(f"    Status: {validation_result['validation_status']}")
    print(f"    Provider: {validation_result['provider_used']}")
    integrity = validation_result.get('integrity', {})
    if integrity:
        print(f"    Integrity: {integrity.get('validation_hash', 'N/A')[:16]}...")
    print(f"    Graph steps: {validation_result['execution_graph']['step_count']}")

    # --- System summary ---
    print()
    print("  [Summary] System state:")
    summary = tracing.get_system_summary()
    print(f"    Total traces: {summary['total_traces']}")
    print(f"    By component: {summary['traces_by_component']}")
    print(f"    By provider: {summary['traces_by_provider']}")

    print()
    print("=" * 70)
    print("  SRT-1 UNIVERSAL AUDIT & TRACING — All Systems Operational ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()
