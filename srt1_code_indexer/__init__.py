"""
SRT-1 Code Indexer v2.0 - Cognitive Operating System for Software Repositories

Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)

Core Modules:
    SRT                  - Seed Reflection Tool v2.0 (anti-hallucination guardrail)
    SRT1CodeIndexer      - Code reflection & indexing engine v2.0
    AuthorityClient      - External signing authority integration point
"""

from srt1_code_indexer.indexer import SRT1CodeIndexer
from srt1_code_indexer.srt import SRT
from srt1_code_indexer.authority_client import AuthorityClient

__version__ = "2.1.0"
__author__ = "William Darnell Jernigan IV"

__all__ = ["SRT1CodeIndexer", "SRT", "AuthorityClient"]
