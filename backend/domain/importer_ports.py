"""Port: import domain nodes/relationships from an external source.

Abstract interface only — no logic. Concrete importers (e.g. Excel, SAP RFC)
live under ``backend/adapters/``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SourceImporter(ABC):
    """Turn a raw external source into domain nodes and relationships."""

    @abstractmethod
    def parse(self, content: bytes) -> Any:
        """Parse raw source bytes into domain nodes and relationships."""
        ...
