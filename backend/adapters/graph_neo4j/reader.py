"""Read side of the Neo4j adapter (GRAPH-D2.1).

Nodes are identified by ``name`` (unique per label; unique across the flagship
dataset), so the API's node id == node name. Returns plain dicts keyed to the
API schema fields; the route maps them to Pydantic models.
"""

from __future__ import annotations

from typing import Any

from neo4j import Driver


def read_graph(driver: Driver, limit: int) -> dict[str, Any]:
    """Return up to ``limit`` nodes plus the relationships among them."""
    with driver.session() as session:
        node_records = session.run(
            "MATCH (n) RETURN n.name AS id, labels(n)[0] AS label, "
            "properties(n) AS props LIMIT $limit",
            limit=limit,
        ).data()
        total_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rel_records = session.run(
            "MATCH (a)-[r]->(b) RETURN elementId(r) AS id, type(r) AS type, "
            "a.name AS source_id, b.name AS target_id, properties(r) AS props"
        ).data()

    nodes = [{"id": r["id"], "label": r["label"], **r["props"]} for r in node_records]
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


def search_nodes(driver: Driver, query: str, limit: int) -> list[dict[str, Any]]:
    """Case-insensitive substring match over node names; prefix matches rank
    first, then alphabetical. Returns id/name/label."""
    with driver.session() as session:
        records = session.run(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($q) "
            "RETURN n.name AS id, n.name AS name, labels(n)[0] AS label, "
            "CASE WHEN toLower(n.name) STARTS WITH toLower($q) THEN 0 ELSE 1 END AS rank "
            "ORDER BY rank ASC, n.name ASC LIMIT $limit",
            q=query,
            limit=limit,
        ).data()
    return [{"id": r["id"], "name": r["name"], "label": r["label"]} for r in records]


def read_node(driver: Driver, name: str) -> dict[str, Any] | None:
    """Return a node's full properties plus its neighbors, or None if unknown.

    A node with no relationships returns an empty ``neighbors`` list (the demo's
    empty-state beat), never an error.
    """
    with driver.session() as session:
        record = session.run(
            "MATCH (n {name: $name}) "
            "RETURN labels(n)[0] AS label, properties(n) AS props LIMIT 1",
            name=name,
        ).single()
        if record is None:
            return None

        neighbor_records = session.run(
            "MATCH (n {name: $name})-[r]->(m) "
            "RETURN m.name AS name, labels(m)[0] AS label, type(r) AS type, "
            "'out' AS direction, r.confidence AS confidence, "
            "r.derived_from AS derived_from "
            "UNION ALL "
            "MATCH (n {name: $name})<-[r]-(m) "
            "RETURN m.name AS name, labels(m)[0] AS label, type(r) AS type, "
            "'in' AS direction, r.confidence AS confidence, "
            "r.derived_from AS derived_from",
            name=name,
        ).data()

    node = {"id": name, "label": record["label"], **record["props"]}
    neighbors = [
        {
            "id": nr["name"],
            "name": nr["name"],
            "label": nr["label"],
            "relationship_type": nr["type"],
            "direction": nr["direction"],
            "confidence": nr["confidence"],
            "derived_from": nr["derived_from"],
        }
        for nr in neighbor_records
    ]
    return {"node": node, "neighbors": neighbors}
