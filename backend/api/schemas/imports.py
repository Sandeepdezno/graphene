"""Import (Excel / SAP-RFC) request-response schemas."""

from __future__ import annotations

from .base import Schema
from .enums import ImportStage


class ImportJobResponse(Schema):
    """Returned when an import job is accepted."""

    job_id: str
    status: ImportStage


class JobStatusResponse(Schema):
    """Progress of an import job, polled by the frontend."""

    job_id: str
    status: ImportStage
    progress: float = 0.0
    message: str | None = None
    error: str | None = None
    # Populated once the graph is built; drive the ticker's final "N nodes, M edges".
    node_count: int | None = None
    edge_count: int | None = None
