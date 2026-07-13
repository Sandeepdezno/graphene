"""AI-chat schemas.

The live endpoint streams via SSE; ``ChatResponse`` documents the assembled
shape (text plus the node ids the answer highlights) for the OpenAPI contract.
"""

from __future__ import annotations

from .base import Schema


class ChatRequest(Schema):
    message: str
    conversation_id: str | None = None


class ChatResponse(Schema):
    text: str
    highlighted_node_ids: list[str]
