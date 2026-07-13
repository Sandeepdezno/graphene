"""Graph read routes.

``/graph`` has a minimal real implementation as of GRAPH-D0.5 (reads live from
Neo4j). ``/graph/node/{id}`` remains stubbed until Sprint 2 (GRAPH-D2.1).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from ..dependencies import get_graph_repository
from ..schemas import (
    GraphResponse,
    NodeDetailResponse,
    NodeSchema,
    RelationshipSchema,
)
from domain.graph_ports import GraphRepository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["graph"])

# Server-side cap so a client-supplied `limit` can't trigger an unbounded read.
MAX_GRAPH_LIMIT = 1000


@router.get("/graph", response_model=GraphResponse)
def get_graph(
    limit: int = Query(
        500, ge=1, description="Max nodes to return (capped at the server maximum)."
    ),
    repo: GraphRepository = Depends(get_graph_repository),
) -> GraphResponse:
    effective_limit = min(limit, MAX_GRAPH_LIMIT)
    try:
        result = repo.get_graph(effective_limit)
    except Exception as exc:  # Neo4j unreachable / query failure
        # Log the detail server-side; return a generic message to the client so
        # internal infrastructure details aren't leaked.
        logger.exception("Graph read failed")
        raise HTTPException(status_code=503, detail="Graph store unavailable") from exc

    nodes = [NodeSchema(**n) for n in result["nodes"]]
    relationships = [RelationshipSchema(**r) for r in result["relationships"]]
    total = result["total_count"]
    returned = len(nodes)
    truncated = total > returned
    return GraphResponse(
        nodes=nodes,
        relationships=relationships,
        returned_count=returned,
        total_count=total,
        limit=effective_limit,
        truncated=truncated,
        truncation_warning=(
            f"Showing {returned} of {total} nodes" if truncated else None
        ),
    )


@router.get("/graph/node/{id}", response_model=NodeDetailResponse)
def get_node(id: str) -> NodeDetailResponse:
    raise HTTPException(
        status_code=501, detail="GET /graph/node/{id} is built in GRAPH-D2.1"
    )
