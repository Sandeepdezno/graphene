"""Batched UNWIND-based writer for the Neo4j adapter (GRAPH-D1.5).

Nodes are MERGEd on (label, name) and relationships on (source, target, type),
so re-importing the same workbook upserts cleanly - properties are refreshed,
nothing is duplicated. Node labels and relationship types come from our own
domain enums/classes (never user input), so interpolating them into the Cypher
is safe.

``last_updated`` is written as an ISO-8601 string (rather than a Neo4j temporal)
so it round-trips straight back into the Pydantic ``datetime`` API schema.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from neo4j import Driver

from domain.models import NodeModel, Relationship


def _node_row(node: NodeModel) -> dict[str, str]:
    return {
        "name": node.name,
        "description": node.description,
        "business_meaning": node.business_meaning,
        "source": node.source,
        "confidence": str(node.confidence),
        "last_updated": node.last_updated.isoformat(),
    }


def _rel_row(rel: Relationship) -> dict[str, str]:
    return {
        "source": rel.source_name,
        "target": rel.target_name,
        "provenance": rel.source,
        "confidence": str(rel.confidence),
        "derived_from": rel.derived_from,
        "last_updated": rel.last_updated.isoformat(),
    }


def write_nodes(driver: Driver, nodes: Sequence[NodeModel]) -> None:
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for node in nodes:
        by_label[node.__class__.__name__].append(_node_row(node))

    with driver.session() as session:
        for label, rows in by_label.items():
            session.run(
                f"UNWIND $rows AS row "
                f"MERGE (n:{label} {{name: row.name}}) "
                "SET n.description = row.description, "
                "n.business_meaning = row.business_meaning, "
                "n.source = row.source, n.confidence = row.confidence, "
                "n.last_updated = row.last_updated",
                rows=rows,
            )


def write_relationships(driver: Driver, relationships: Sequence[Relationship]) -> None:
    with driver.session() as session:
        # Map name -> primary label from the nodes just written, so endpoint
        # MATCHes can be label-qualified and hit the per-label uniqueness index
        # (a label-less MATCH would full-scan and blow the write-time budget).
        label_of: dict[str, str] = {
            record["name"]: record["label"]
            for record in session.run(
                "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label"
            )
        }

        # Group by (type, source_label, target_label) so each batch is one
        # index-backed UNWIND query.
        by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
        for rel in relationships:
            source_label = label_of.get(rel.source_name)
            target_label = label_of.get(rel.target_name)
            if source_label is None or target_label is None:
                continue  # dangling endpoint (should not happen after write_nodes)
            by_key[(rel.type.value, source_label, target_label)].append(_rel_row(rel))

        for (rel_type, source_label, target_label), rows in by_key.items():
            session.run(
                "UNWIND $rows AS row "
                f"MATCH (a:{source_label} {{name: row.source}}) "
                f"MATCH (b:{target_label} {{name: row.target}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r.source = row.provenance, r.confidence = row.confidence, "
                "r.derived_from = row.derived_from, r.last_updated = row.last_updated",
                rows=rows,
            )
