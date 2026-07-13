from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class Program(NodeModel):
    """An ABAP program / report."""
