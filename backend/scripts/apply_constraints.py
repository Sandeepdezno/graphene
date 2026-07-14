"""Apply Neo4j schema constraints (GRAPH-D1.5).

A uniqueness constraint on ``name`` per node label, so duplicate-name writes are
rejected (not silently overwritten) and re-imports (MERGE on name) stay
idempotent.

Run:
    ./backend/.venv/bin/python backend/scripts/apply_constraints.py
"""

from __future__ import annotations

import os
import sys

from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "graphene-dev")

LABELS = ["Program", "Table", "FunctionModule", "BAdI", "Job", "Transport"]


def apply() -> None:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            for label in LABELS:
                name = f"{label.lower()}_name_unique"
                session.run(
                    f"CREATE CONSTRAINT {name} IF NOT EXISTS "
                    f"FOR (n:{label}) REQUIRE n.name IS UNIQUE"
                )
                print(f"  constraint {name} applied")
        print(f"Applied {len(LABELS)} uniqueness constraints to {URI}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to apply constraints: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        driver.close()


if __name__ == "__main__":
    apply()
