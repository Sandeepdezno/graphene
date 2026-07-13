"""Seed the 'Hello Graph' dataset directly into Neo4j (GRAPH-D0.5).

Inserts 5 realistic SAP nodes and 4 relationships so the full stack can be
proven to round-trip before any real import pipeline exists. Idempotent: uses
MERGE, so re-running does not create duplicates.

Run (with Neo4j up via docker-compose):
    ./backend/.venv/bin/python backend/scripts/seed_hello_graph.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "graphene-dev")

NOW = datetime.now(timezone.utc).isoformat()

NODES = [
    {
        "label": "Program",
        "name": "Z_PRICE_ENGINE",
        "description": "Core pricing calculation program",
        "business_meaning": "Calculates customer-specific prices for sales orders",
    },
    {
        "label": "Table",
        "name": "ZTABLE_PRICING",
        "description": "Pricing conditions master table",
        "business_meaning": "Stores the pricing rules and condition records",
    },
    {
        "label": "Table",
        "name": "ZTABLE_PRICE_LOG",
        "description": "Pricing calculation audit log",
        "business_meaning": "Audit trail of every price the engine computes",
    },
    {
        "label": "FunctionModule",
        "name": "Z_FM_VALIDATE_PRICE",
        "description": "Price validation function module",
        "business_meaning": "Validates computed prices against business rules",
    },
    {
        "label": "Job",
        "name": "ZJOB_NIGHTLY_PRICING",
        "description": "Nightly pricing batch job",
        "business_meaning": "Recalculates all prices overnight",
    },
]

# (source_name, relationship_type, target_name)
EDGES = [
    ("Z_PRICE_ENGINE", "READS", "ZTABLE_PRICING"),
    ("Z_PRICE_ENGINE", "WRITES", "ZTABLE_PRICE_LOG"),
    ("Z_PRICE_ENGINE", "CALLS", "Z_FM_VALIDATE_PRICE"),
    ("ZJOB_NIGHTLY_PRICING", "EXECUTES", "Z_PRICE_ENGINE"),
]


def seed() -> None:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            for node in NODES:
                # Label cannot be parameterized in Cypher; it comes from our own
                # constant list (not user input), so interpolation is safe here.
                session.run(
                    f"MERGE (x:{node['label']} {{name: $name}}) "
                    "SET x.description = $description, "
                    "x.business_meaning = $business_meaning, "
                    "x.source = $source, x.confidence = $confidence, "
                    "x.last_updated = $last_updated",
                    name=node["name"],
                    description=node["description"],
                    business_meaning=node["business_meaning"],
                    source="excel_import",
                    confidence="direct",
                    last_updated=NOW,
                )
            for src, rel_type, tgt in EDGES:
                session.run(
                    "MATCH (a {name: $src}), (b {name: $tgt}) "
                    f"MERGE (a)-[r:{rel_type}]->(b) "
                    "SET r.source = $source, r.confidence = $confidence, "
                    "r.derived_from = $derived_from, r.last_updated = $last_updated",
                    src=src,
                    tgt=tgt,
                    source="excel_import",
                    confidence="direct",
                    derived_from="hello-graph seed",
                    last_updated=NOW,
                )
        print(f"Seeded {len(NODES)} nodes and {len(EDGES)} relationships into {URI}")
    except Exception as exc:  # noqa: BLE001 - surface a clear message to the operator
        print(f"Seeding failed: {exc}", file=sys.stderr)
        print(
            "Is Neo4j running? Start it with: docker compose up -d",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    finally:
        driver.close()


if __name__ == "__main__":
    seed()
