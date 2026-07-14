"""In-memory import-job store (GRAPH-D1.3).

A plain dict keyed by ``job_id`` - deliberately NOT Celery/Redis (CLAUDE.md
rule 6). Its shape (``job_id``, ``stage``, ``error``) is exactly what a real
queue's status contract would expose, so the implementation can be swapped for
a durable queue later without the frontend changing.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class ImportStage(StrEnum):
    PARSING = "parsing"
    INFERRING = "inferring"
    WRITING = "writing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ImportJob:
    job_id: str
    stage: ImportStage
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ImportJobStore:
    """Process-wide, in-memory store of import jobs."""

    def __init__(self) -> None:
        self._jobs: dict[str, ImportJob] = {}

    def create(self) -> ImportJob:
        job = ImportJob(job_id=uuid.uuid4().hex, stage=ImportStage.PARSING)
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> ImportJob | None:
        return self._jobs.get(job_id)

    def advance(self, job_id: str, stage: ImportStage) -> None:
        self._jobs[job_id].stage = stage

    def fail(self, job_id: str, error: str) -> None:
        job = self._jobs[job_id]
        job.stage = ImportStage.FAILED
        job.error = error
