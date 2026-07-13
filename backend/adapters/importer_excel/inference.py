"""Relationship inference for the Excel importer.

Implements exactly the one rule documented in docs/excel-schema.md:

    if A CALLS B and B WRITES T, then A gets an inferred WRITES edge to T.

No other inference. Inferred edges are stamped source="inferred",
confidence="inferred", derived_from="transitive: A->B->T", and are deduplicated
against existing direct edges (and against each other).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from domain.models import Confidence, Relationship, RelationshipType


def infer_transitive_writes(
    direct: list[Relationship], now: datetime
) -> list[Relationship]:
    writes_by_source: dict[str, set[str]] = defaultdict(set)
    direct_write_keys: set[tuple[str, str]] = set()
    calls: list[tuple[str, str]] = []

    for rel in direct:
        if rel.type is RelationshipType.WRITES:
            writes_by_source[rel.source_name].add(rel.target_name)
            direct_write_keys.add((rel.source_name, rel.target_name))
        elif rel.type is RelationshipType.CALLS:
            calls.append((rel.source_name, rel.target_name))

    seen: set[tuple[str, str]] = set()
    inferred: list[Relationship] = []
    for a, b in calls:
        for t in writes_by_source.get(b, ()):
            if (a, t) in direct_write_keys or (a, t) in seen:
                continue
            seen.add((a, t))
            inferred.append(
                Relationship(
                    source_name=a,
                    target_name=t,
                    type=RelationshipType.WRITES,
                    source="inferred",
                    confidence=Confidence.INFERRED,
                    derived_from=f"transitive: {a}→{b}→{t}",
                    last_updated=now,
                )
            )
    return inferred
