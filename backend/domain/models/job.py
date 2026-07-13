from __future__ import annotations

from dataclasses import dataclass

from .base import NodeModel


@dataclass
class Job(NodeModel):
    """A background job."""
