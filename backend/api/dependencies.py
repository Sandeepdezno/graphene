"""Dependency injection wiring.

Hardcoded adapter bindings — no plugin registry, no config-driven loading
(see 02-system-architecture.md). Swap an adapter by editing this file.
"""

from __future__ import annotations

from functools import lru_cache

from ..adapters.graph_neo4j import Neo4jGraphRepository
from ..domain.graph_ports import GraphRepository


@lru_cache(maxsize=1)
def get_graph_repository() -> GraphRepository:
    """Return the process-wide GraphRepository, hardcoded to the Neo4j adapter."""
    return Neo4jGraphRepository()
