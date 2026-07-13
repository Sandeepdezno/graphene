"""Unit tests: instantiation of every domain node model (GRAPH-D0.1)."""

from __future__ import annotations

from datetime import datetime

import pytest

from domain.models import (
    BAdI,
    Confidence,
    FunctionModule,
    Job,
    NodeModel,
    Program,
    Table,
    Transport,
)

ALL_MODELS = [Program, Table, FunctionModule, BAdI, Job, Transport]


def _build(cls: type[NodeModel]) -> NodeModel:
    return cls(
        name=f"{cls.__name__}_1",
        description="a test node",
        business_meaning="what it means to the business",
        source="excel_import",
        confidence=Confidence.DIRECT,
        last_updated=datetime(2026, 7, 13, 12, 0, 0),
    )


@pytest.mark.parametrize("cls", ALL_MODELS, ids=lambda c: c.__name__)
def test_model_instantiates(cls: type[NodeModel]) -> None:
    node = _build(cls)
    assert isinstance(node, cls)
    assert isinstance(node, NodeModel)
    assert node.name == f"{cls.__name__}_1"
    assert node.business_meaning == "what it means to the business"
    assert node.source == "excel_import"
    assert node.confidence == Confidence.DIRECT
    assert isinstance(node.last_updated, datetime)


@pytest.mark.parametrize("cls", ALL_MODELS, ids=lambda c: c.__name__)
def test_model_accepts_inferred_confidence(cls: type[NodeModel]) -> None:
    node = cls(
        name="n",
        description="d",
        business_meaning="b",
        source="inference",
        confidence=Confidence.INFERRED,
        last_updated=datetime.now(),
    )
    assert node.confidence == Confidence.INFERRED


def test_confidence_is_a_string_enum_not_bool() -> None:
    # Binary, but stored as a string so a third tier is addable without migration.
    assert Confidence.DIRECT == "direct"
    assert Confidence.INFERRED == "inferred"
    assert isinstance(Confidence.DIRECT, str)
    assert not isinstance(Confidence.DIRECT, bool)
    assert [c.value for c in Confidence] == ["direct", "inferred"]
