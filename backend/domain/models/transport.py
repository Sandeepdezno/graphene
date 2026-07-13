from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class Transport(NodeModel):
    """A transport request (change moving across SAP landscapes)."""
