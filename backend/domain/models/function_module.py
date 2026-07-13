from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class FunctionModule(NodeModel):
    """A function module (including RFC-enabled modules)."""
