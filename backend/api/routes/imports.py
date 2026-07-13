"""Import routes (stubbed at GRAPH-D0.3).

Named ``imports.py`` rather than the doc's ``import.py`` because ``import`` is a
reserved word and cannot be imported as a module.
"""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import ImportJobResponse, JobStatusResponse

router = APIRouter(tags=["import"])


@router.post("/import/excel", response_model=ImportJobResponse)
async def import_excel(file: UploadFile = File(...)) -> ImportJobResponse:
    raise HTTPException(
        status_code=501, detail="POST /import/excel is built in GRAPH-D1.3"
    )


@router.get("/import/{job_id}/status", response_model=JobStatusResponse)
def import_status(job_id: str) -> JobStatusResponse:
    raise HTTPException(
        status_code=501, detail="GET /import/{job_id}/status is built in GRAPH-D1.3"
    )


@router.post("/import/sap-rfc", response_model=ImportJobResponse)
def import_sap_rfc() -> ImportJobResponse:
    # 🚀 Long-term platform — intentionally not implemented.
    raise HTTPException(status_code=501, detail="POST /import/sap-rfc is not implemented")
