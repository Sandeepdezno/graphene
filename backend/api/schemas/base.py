"""Shared base for API schemas.

``extra="forbid"`` makes the generated OpenAPI emit ``additionalProperties:
false``, which keeps the generated TypeScript client free of loose index
signatures (and therefore free of ``any``).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")
