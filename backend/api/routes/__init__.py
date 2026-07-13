"""API route modules, aggregated into a single v1 router."""

from __future__ import annotations

from fastapi import APIRouter

from . import chat, graph, health, impact, imports, search

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(imports.router)
api_router.include_router(graph.router)
api_router.include_router(search.router)
api_router.include_router(impact.router)
api_router.include_router(chat.router)

__all__ = ["api_router"]
