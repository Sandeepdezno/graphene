"""Import routes (GRAPH-D1.3).

``import`` is a reserved word, so this module is ``imports.py`` rather than the
doc's ``import.py``.
"""

from __future__ import annotations

import logging
import time

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from ..dependencies import get_excel_importer, get_import_job_store
from ..schemas import ImportJobResponse, JobStatusResponse
from adapters.importer_excel import ExcelImporter, ImporterValidationError
from domain.models import ImportResult
from domain.services.import_job import ImportJobStore, ImportStage

logger = logging.getLogger(__name__)
router = APIRouter(tags=["import"])

# Demo pacing so the staged animation (D1.4, demo bible 0:30-1:00) is visible;
# write-time pacing is tuned for real in GRAPH-D1.5.
STAGE_PAUSE_SECONDS = 1.0


def _run_import_pipeline(
    content: bytes,
    job_id: str,
    store: ImportJobStore,
    importer: ExcelImporter,
) -> None:
    """Background pipeline: parse -> infer -> write, advancing the job stage."""
    try:
        # Job is created at stage=parsing; do the parse work under that stage.
        time.sleep(STAGE_PAUSE_SECONDS)
        nodes, direct = importer.parse_direct(content)

        store.advance(job_id, ImportStage.INFERRING)
        time.sleep(STAGE_PAUSE_SECONDS)
        inferred = importer.infer(direct)
        result = ImportResult(nodes=nodes, relationships=direct + inferred)

        store.advance(job_id, ImportStage.WRITING)
        time.sleep(STAGE_PAUSE_SECONDS)
        # TODO(GRAPH-D1.5): persist via the GraphRepository bulk writer. Until that
        # lands, the write phase is stub-logged and the job still reaches complete.
        logger.info(
            "import %s: parsed %d nodes, %d relationships (writer lands in GRAPH-D1.5)",
            job_id,
            len(nodes),
            len(result.relationships),
        )

        # Headline counts for the ticker: node total + DIRECT edges (matches the
        # demo script's "214 nodes, 386 edges"; inferred edges are added on top).
        store.set_counts(job_id, len(nodes), len(direct))
        store.advance(job_id, ImportStage.COMPLETE)
    except Exception as exc:  # noqa: BLE001 - any failure marks the job failed
        logger.exception("import %s failed", job_id)
        store.fail(job_id, str(exc))


@router.post("/import/excel", response_model=ImportJobResponse)
async def import_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    store: ImportJobStore = Depends(get_import_job_store),
    importer: ExcelImporter = Depends(get_excel_importer),
) -> ImportJobResponse:
    filename = file.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=422, detail="Only .xlsx workbooks are accepted."
        )

    content = await file.read()
    try:
        importer.validate(content)  # synchronous structure check
    except ImporterValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # not a readable .xlsx (e.g. corrupt / renamed file)
        raise HTTPException(
            status_code=422, detail=f"Could not read .xlsx workbook: {exc}"
        ) from exc

    job = store.create()
    background_tasks.add_task(_run_import_pipeline, content, job.job_id, store, importer)
    return ImportJobResponse(job_id=job.job_id, status=job.stage)


@router.get("/import/{job_id}/status", response_model=JobStatusResponse)
def import_status(
    job_id: str,
    store: ImportJobStore = Depends(get_import_job_store),
) -> JobStatusResponse:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id: {job_id}")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.stage,
        error=job.error,
        node_count=job.node_count,
        edge_count=job.edge_count,
    )


@router.post("/import/sap-rfc", response_model=ImportJobResponse)
def import_sap_rfc() -> ImportJobResponse:
    # 🚀 Long-term platform - intentionally not implemented.
    raise HTTPException(status_code=501, detail="POST /import/sap-rfc is not implemented")
