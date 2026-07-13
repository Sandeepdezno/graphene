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

    def get_graph(self, limit: int) -> dict[str, Any]:
        """Minimal graph read (GRAPH-D0.5): nodes up to ``limit`` plus the
        relationships among them, as plain dicts keyed to the API schema
        fields. The bounded/typed version arrives in GRAPH-D2.1.
        """
        with self._driver.session() as session:
            node_records = session.run(
                "MATCH (n) RETURN elementId(n) AS id, labels(n)[0] AS label, "
                "properties(n) AS props LIMIT $limit",
                limit=limit,
            ).data()
            total_count = session.run(
                "MATCH (n) RETURN count(n) AS c"
            ).single()["c"]
            rel_records = session.run(
                "MATCH (a)-[r]->(b) RETURN elementId(r) AS id, type(r) AS type, "
                "elementId(a) AS source_id, elementId(b) AS target_id, "
                "properties(r) AS props"
            ).data()

        nodes = [
            {"id": r["id"], "label": r["label"], **r["props"]} for r in node_records
        ]
        node_ids = {n["id"] for n in nodes}
        relationships = [
            {
                "id": r["id"],
                "type": r["type"],
                "source_id": r["source_id"],
                "target_id": r["target_id"],
                **r["props"],
            }
            for r in rel_records
            if r["source_id"] in node_ids and r["target_id"] in node_ids
        ]
        return {
            "nodes": nodes,
            "relationships": relationships,
            "total_count": total_count,
        }

    def get_node(self, node_id: str) -> Any:
        raise NotImplementedError("get_node lands in GRAPH-D2.1")

    def search(self, query: str) -> Sequence[NodeModel]:
        raise NotImplementedError("search lands in GRAPH-D2.5")
