"""
SCIA Security Utilities — Standalone Package

Execution tracking, integrity validation, and security utilities
for any SCIA-governed system. This package provides the security
infrastructure that supports SCIA operations.

Components:
- ExecutionGraph: DAG-based execution tracking and flow visualization
- IntegrityValidator: Content hash verification utilities

Usage:
    from scia_security import ExecutionGraph

    graph = ExecutionGraph()
    node_id = graph.start_execution("process_content")
    # ... do work ...
    graph.end_execution(node_id, result="success")
    print(graph.get_execution_summary())

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

from .execution_graph import ExecutionGraph, ExecutionNode
from .integrity import IntegrityValidator

__all__ = [
    "ExecutionGraph",
    "ExecutionNode",
    "IntegrityValidator",
]

__version__ = "2.1.0"
__author__ = "William Darnell Jernigan IV"
