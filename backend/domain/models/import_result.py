from __future__ import annotations

from dataclasses import dataclass, field

from .base import NodeModel
from .relationship import Relationship


@dataclass
class ImportResult:
    """What a SourceImporter returns: domain nodes plus relationships.

    Relationships include both direct (``confidence="direct"``) and inferred
    (``confidence="inferred"``) edges; callers distinguish by the field.
    """

    nodes: list[NodeModel] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
