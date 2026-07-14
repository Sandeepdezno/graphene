"""Port: persistence and retrieval for the knowledge graph.

Abstract interface only — no logic. Concrete adapters (e.g. Neo4j) live under
``backend/adapters/`` and must never be imported here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from .models import NodeModel, Relationship


class GraphRepository(ABC):
    """Store and read the Graphene knowledge graph."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the backing graph store is reachable."""
        ...

    @abstractmethod
    def write_nodes(self, nodes: Sequence[NodeModel]) -> None:
        """Persist domain nodes to the graph."""
        ...

    @abstractmethod
    def write_relationships(self, relationships: Sequence[Relationship]) -> None:
        """Persist relationships between existing nodes."""
        ...

    @abstractmethod
    def get_graph(self, limit: int) -> Any:
        """Return up to ``limit`` nodes with their relationships."""
        ...

    @abstractmethod
    def get_node(self, node_id: str) -> Any:
        """Return a node with its neighbors and per-relationship confidence."""
        ...

    @abstractmethod
    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Match nodes by name; returns id/name/label dicts, prefix matches first."""
        ...
