"""Search route (GRAPH-D2.5)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_graph_repository
from ..schemas import SearchResponse, SearchResultItem
from domain.graph_ports import GraphRepository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])

SEARCH_LIMIT = 10


@router.get("/search", response_model=SearchResponse)
def search(
    q: str,
    repo: GraphRepository = Depends(get_graph_repository),
) -> SearchResponse:
    if not q.strip():
        return SearchResponse(query=q, results=[], count=0)

    try:
        rows = repo.search(q, SEARCH_LIMIT)
    except Exception as exc:  # Neo4j unreachable / query failure
        logger.exception("search failed")
        raise HTTPException(status_code=503, detail="Graph store unavailable") from exc

    results = [SearchResultItem(**row) for row in rows]
    return SearchResponse(query=q, results=results, count=len(results))
