"""Unit tests for the Excel importer (GRAPH-D1.2).

Expected counts are hardcoded from docs/flagship-blast-radius.md - the human
validation artifact - NOT computed from the parser under test.
"""

from __future__ import annotations

import io
from collections import Counter
from pathlib import Path

import pytest
from openpyxl import Workbook

from adapters.importer_excel import ExcelImporter, ImporterValidationError
from domain.models import Confidence

FLAGSHIP_XLSX = Path(__file__).resolve().parents[4] / "demo-data" / "flagship.xlsx"

# --- hardcoded from docs/flagship-blast-radius.md ---
EXPECTED_NODES_PER_LABEL = {
    "Program": 49,
    "Table": 95,
    "FunctionModule": 36,
    "BAdI": 6,
    "Job": 18,
    "Transport": 10,
}
EXPECTED_DIRECT_EDGES_PER_TYPE = {
    "READS": 166,
    "WRITES": 95,
    "CALLS": 70,
    "IMPLEMENTS": 6,
    "EXECUTES": 23,
    "CHANGED": 26,
}
EXPECTED_TOTAL_NODES = 214
EXPECTED_TOTAL_DIRECT_EDGES = 386
EXPECTED_INFERRED_EDGES = 36


def _parse_flagship():
    return ExcelImporter().parse(FLAGSHIP_XLSX.read_bytes())


def test_flagship_counts_match_validation_artifact():
    result = _parse_flagship()

    nodes_per_label = Counter(node.__class__.__name__ for node in result.nodes)
    assert dict(nodes_per_label) == EXPECTED_NODES_PER_LABEL
    assert len(result.nodes) == EXPECTED_TOTAL_NODES

    direct = [r for r in result.relationships if r.confidence is Confidence.DIRECT]
    inferred = [r for r in result.relationships if r.confidence is Confidence.INFERRED]

    direct_per_type = Counter(r.type.value for r in direct)
    assert dict(direct_per_type) == EXPECTED_DIRECT_EDGES_PER_TYPE
    assert len(direct) == EXPECTED_TOTAL_DIRECT_EDGES

    assert len(inferred) == EXPECTED_INFERRED_EDGES

    # provenance sanity: every direct edge is stamped from the excel import
    assert all(r.source == "excel_import" for r in direct)
    assert all(r.source == "inferred" for r in inferred)


def test_sparse_node_has_zero_edges():
    result = _parse_flagship()

    by_name = {n.name: n for n in result.nodes}
    assert "Z_LEGACY_REBATE_CALC" in by_name
    assert by_name["Z_LEGACY_REBATE_CALC"].__class__.__name__ == "Program"

    touching = [
        r
        for r in result.relationships
        if "Z_LEGACY_REBATE_CALC" in (r.source_name, r.target_name)
    ]
    assert touching == []


def _workbook_bytes(sheets: dict[str, list[str]]) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)
    for name, header in sheets.items():
        ws = wb.create_sheet(name)
        ws.append(header)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


VALID_HEADERS = {
    "Programs": ["Program", "Description", "BusinessMeaning", "Reads", "Writes", "Calls"],
    "FunctionModules": [
        "FunctionModule", "Description", "BusinessMeaning", "Reads", "Writes", "Calls",
    ],
    "BAdIs": ["BAdI", "Description", "BusinessMeaning", "ImplementedBy"],
    "Jobs": ["Job", "Description", "BusinessMeaning", "Executes"],
    "Transports": ["Transport", "Description", "Changed"],
}


def test_missing_column_raises_named_validation_error():
    sheets = {k: list(v) for k, v in VALID_HEADERS.items()}
    sheets["Programs"].remove("Calls")  # break one column
    with pytest.raises(ImporterValidationError, match=r"Programs.*Calls"):
        ExcelImporter().parse(_workbook_bytes(sheets))


def test_missing_sheet_raises_named_validation_error():
    sheets = {k: list(v) for k, v in VALID_HEADERS.items() if k != "Transports"}
    with pytest.raises(ImporterValidationError, match=r"Transports"):
        ExcelImporter().parse(_workbook_bytes(sheets))
