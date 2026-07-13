"""AI-chat route (stubbed at GRAPH-D0.3; built in GRAPH-D4.4)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    raise HTTPException(status_code=501, detail="POST /chat is built in GRAPH-D4.4")
