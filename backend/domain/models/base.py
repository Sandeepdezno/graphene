"""Shared base types for Graphene domain node models.

Pure domain layer — standard library only. No framework imports (no FastAPI,
Neo4j, Ollama, or Pydantic) may appear anywhere under ``domain/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Confidence(StrEnum):
    """Binary confidence for a node/relationship's provenance.

    Stored as a string (never a boolean) so a third tier can be added later
    without a data migration.
    """

    DIRECT = "direct"
    INFERRED = "inferred"


@dataclass
class NodeModel:
    """Fields shared by every Graphene graph node."""

    name: str
    description: str
    business_meaning: str
    source: str
    confidence: Confidence
    last_updated: datetime
