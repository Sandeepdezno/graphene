"""Health-check schema."""

from __future__ import annotations

from .base import Schema


class Neo4jStatus(Schema):
    connected: bool


class HealthResponse(Schema):
    status: str
    neo4j: Neo4jStatus
