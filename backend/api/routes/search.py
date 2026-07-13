"""Search route (stubbed at GRAPH-D0.3; built in GRAPH-D2.5)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import SearchResponse

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(q: str) -> SearchResponse:
    raise HTTPException(status_code=501, detail="GET /search is built in GRAPH-D2.5")
