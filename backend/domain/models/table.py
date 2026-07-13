from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class Table(NodeModel):
    """A database table (ABAP Dictionary object)."""
