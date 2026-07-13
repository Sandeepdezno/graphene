"""Neo4j adapter implementing GraphRepository.

GRAPH-D0.2 scope: connection management + health check only. The remaining
GraphRepository methods are declared (so the ABC can be instantiated) but raise
``NotImplementedError`` until their own tickets build them.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from neo4j import GraphDatabase

from ...domain.graph_ports import GraphRepository
from ...domain.models import NodeModel

DEFAULT_URI = "bolt://localhost:7687"
DEFAULT_USER = "neo4j"
DEFAULT_PASSWORD = "graphene-dev"


class Neo4jGraphRepository(GraphRepository):
    """GraphRepository backed by a Neo4j 5 instance (see docker-compose.yml)."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self._uri = uri or os.getenv("NEO4J_URI", DEFAULT_URI)
        user = user or os.getenv("NEO4J_USER", DEFAULT_USER)
        password = password or os.getenv("NEO4J_PASSWORD", DEFAULT_PASSWORD)
        # Driver construction is lazy — it does not open a connection here, so
        # the app boots even when Neo4j is down.
        self._driver = GraphDatabase.driver(self._uri, auth=(user, password))

    @property
    def uri(self) -> str:
        return self._uri

    def health_check(self) -> bool:
        """Return True iff the Neo4j server is reachable. Never raises."""
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:  # noqa: BLE001 - health check must never propagate
            return False

    def close(self) -> None:
        self._driver.close()

    # --- Out of scope for GRAPH-D0.2; implemented in later tickets. ---
    def write_nodes(self, nodes: Sequence[NodeModel]) -> None:
        raise NotImplementedError("write_nodes lands in GRAPH-D1.5")

    def write_relationships(self, relationships: Sequence[Any]) -> None:
        raise NotImplementedError("write_relationships lands in GRAPH-D1.5")

    def get_graph(self, limit: int) -> Any:
        raise NotImplementedError("get_graph lands in GRAPH-D2.1")

    def get_node(self, node_id: str) -> Any:
        raise NotImplementedError("get_node lands in GRAPH-D2.1")

    def search(self, query: str) -> Sequence[NodeModel]:
        raise NotImplementedError("search lands in GRAPH-D2.5")
