from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .base import Confidence


class RelationshipType(StrEnum):
    READS = "READS"
    WRITES = "WRITES"
    CALLS = "CALLS"
    IMPLEMENTS = "IMPLEMENTS"
    EXECUTES = "EXECUTES"
    CHANGED = "CHANGED"
    CREATED = "CREATED"


@dataclass
class Relationship:
    """A directed edge between two nodes, identified by node name.

    Carries the same provenance model as nodes (03-graph-schema.md): ``source``,
    ``confidence`` and ``derived_from`` answer "how do we know this?".
    """

    source_name: str
    target_name: str
    type: RelationshipType
    source: str
    confidence: Confidence
    derived_from: str
    last_updated: datetime
