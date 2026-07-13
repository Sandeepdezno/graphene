"""Graph read routes (stubbed at GRAPH-D0.3; built in Sprint 2)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import GraphResponse, NodeDetailResponse

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def get_graph(limit: int = 500) -> GraphResponse:
    raise HTTPException(status_code=501, detail="GET /graph is built in GRAPH-D2.1")


@router.get("/graph/node/{id}", response_model=NodeDetailResponse)
def get_node(id: str) -> NodeDetailResponse:
    raise HTTPException(
        status_code=501, detail="GET /graph/node/{id} is built in GRAPH-D2.1"
    )
