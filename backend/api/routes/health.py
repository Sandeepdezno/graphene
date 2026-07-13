"""GET /api/v1/health — liveness plus Neo4j readiness.

Returns 200 whenever the app is up; the Neo4j connection state is reported in
the body (``neo4j.connected``) rather than via the HTTP status code.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_graph_repository
from ...domain.graph_ports import GraphRepository

router = APIRouter(tags=["health"])


@router.get("/health")
def health(repo: GraphRepository = Depends(get_graph_repository)) -> dict:
    connected = repo.health_check()
    return {
        "status": "ok" if connected else "degraded",
        "neo4j": {
            "connected": connected,
            "uri": getattr(repo, "uri", None),
        },
    }
