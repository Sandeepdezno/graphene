"""Enums shared across API schemas, mirroring 03-graph-schema.md."""

from __future__ import annotations

from enum import StrEnum


class ConfidenceEnum(StrEnum):
    DIRECT = "direct"
    INFERRED = "inferred"


class SourceEnum(StrEnum):
    """Provenance of a node/relationship."""

    EXCEL_IMPORT = "excel_import"
    INFERRED = "inferred"
    SAP_RFC = "sap_rfc"  # future (🚀)


class NodeLabel(StrEnum):
    PROGRAM = "Program"
    TABLE = "Table"
    FUNCTION_MODULE = "FunctionModule"
    BADI = "BAdI"
    JOB = "Job"
    TRANSPORT = "Transport"
    USER = "User"


class RelationshipType(StrEnum):
    READS = "READS"
    WRITES = "WRITES"
    CALLS = "CALLS"
    IMPLEMENTS = "IMPLEMENTS"
    EXECUTES = "EXECUTES"
    CHANGED = "CHANGED"
    CREATED = "CREATED"


class Direction(StrEnum):
    """A neighbor's relationship direction relative to the focus node."""

    IN = "in"
    OUT = "out"


class ImportStage(StrEnum):
    """Staged status of an import job.

    Shaped like a real queue's status contract (see CLAUDE.md) so the in-memory
    implementation can be swapped later without touching the frontend.
    """

    QUEUED = "queued"
    PARSING = "parsing"
    INFERRING = "inferring"
    WRITING = "writing"
    COMPLETE = "complete"
    FAILED = "failed"
