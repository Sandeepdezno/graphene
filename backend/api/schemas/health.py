"""Health-check schema."""

from __future__ import annotations

from .base import Schema


class Neo4jStatus(Schema):
    connected: bool
    uri: str | None = None


class HealthResponse(Schema):
    status: str
    neo4j: Neo4jStatus
