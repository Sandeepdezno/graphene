"""Impact-analysis (blast radius) schemas."""

from __future__ import annotations

from .base import Schema
from .enums import ConfidenceEnum, NodeLabel


class AffectedItem(Schema):
    id: str
    name: str
    label: NodeLabel
    hop_distance: int
    confidence: ConfidenceEnum


class AffectedGroup(Schema):
    """Affected items grouped by node type."""

    label: NodeLabel
    items: list[AffectedItem]
    count: int


class ImpactResponse(Schema):
    node_id: str
    risk_score: int  # 0-100
    total_affected: int
    affected_groups: list[AffectedGroup]
    explanation: str
