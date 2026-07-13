"""Search schemas."""

from __future__ import annotations

from .base import Schema
from .enums import NodeLabel


class SearchResultItem(Schema):
    id: str
    name: str
    label: NodeLabel
    description: str
    score: float


class SearchResponse(Schema):
    query: str
    results: list[SearchResultItem]
    count: int
