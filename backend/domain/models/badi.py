from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class BAdI(NodeModel):
    """A Business Add-In (BAdI) enhancement."""
