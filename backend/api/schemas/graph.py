"""Graph node/relationship schemas and the /graph responses."""

from __future__ import annotations

from datetime import datetime

from .base import Schema
from .enums import ConfidenceEnum, NodeLabel, RelationshipType, SourceEnum


class NodeSchema(Schema):
    id: str
    label: NodeLabel
    name: str
    description: str
    business_meaning: str
    source: SourceEnum
    confidence: ConfidenceEnum
    last_updated: datetime
    visibility: str | None = None


class RelationshipSchema(Schema):
    id: str
    type: RelationshipType
    source_id: str
    target_id: str
    source: SourceEnum
    confidence: ConfidenceEnum
    derived_from: str
    last_updated: datetime


class GraphResponse(Schema):
    nodes: list[NodeSchema]
    relationships: list[RelationshipSchema]
    returned_count: int
    total_count: int
    limit: int
    truncated: bool
    truncation_warning: str | None = None


class NodeDetailResponse(Schema):
    node: NodeSchema
    neighbors: list[NodeSchema]
    relationships: list[RelationshipSchema]
