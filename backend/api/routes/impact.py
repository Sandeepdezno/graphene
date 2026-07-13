"""Impact-analysis route (stubbed at GRAPH-D0.3; built in GRAPH-D3.2)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import ImpactResponse

router = APIRouter(tags=["impact"])


@router.get("/impact/{node_id}", response_model=ImpactResponse)
def impact(node_id: str) -> ImpactResponse:
    raise HTTPException(
        status_code=501, detail="GET /impact/{node_id} is built in GRAPH-D3.2"
    )
