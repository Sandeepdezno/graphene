"""Graphene FastAPI application entrypoint.

`backend/` is the source root (top-level packages: domain, adapters, api).
Run with: ``PYTHONPATH=backend uvicorn api.main:app`` from the repository root.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from .dependencies import get_graph_repository
from .routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    # Close the Neo4j driver held by the singleton repository on shutdown.
    repo = get_graph_repository()
    close = getattr(repo, "close", None)
    if callable(close):
        close()


app = FastAPI(title="Graphene API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
