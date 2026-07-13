"""Graph read routes.

``/graph`` has a minimal real implementation as of GRAPH-D0.5 (reads live from
Neo4j). ``/graph/node/{id}`` remains stubbed until Sprint 2 (GRAPH-D2.1).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_graph_repository
from ..schemas import (
    GraphResponse,
    NodeDetailResponse,
    NodeSchema,
    RelationshipSchema,
)
from ...domain.graph_ports import GraphRepository

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def get_graph(
    limit: int = 500,
    repo: GraphRepository = Depends(get_graph_repository),
) -> GraphResponse:
    try:
        result = repo.get_graph(limit)
    except Exception as exc:  # Neo4j unreachable / query failure
        raise HTTPException(
            status_code=503, detail=f"Graph store unavailable: {exc}"
        ) from exc

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
        limit=limit,
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
