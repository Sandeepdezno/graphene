"""Impact-analysis route (GRAPH-D3.2). Thin wiring over the domain service."""

from __future__ import annotations

import logging
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_impact_service
from ..schemas import AffectedGroup, AffectedItem, ImpactResponse
from domain.services.impact_analysis import ImpactAnalysisService, NodeNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["impact"])

# Stable group order for the response.
LABEL_ORDER = ["Program", "Table", "FunctionModule", "BAdI", "Job", "Transport"]


@router.get("/impact/{node_id}", response_model=ImpactResponse)
def impact(
    node_id: str,
    service: ImpactAnalysisService = Depends(get_impact_service),
) -> ImpactResponse:
    try:
        result = service.analyze(node_id)
    except NodeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown node: {node_id}") from exc
    except Exception as exc:  # Neo4j unreachable / query failure
        logger.exception("impact analysis failed")
        raise HTTPException(status_code=503, detail="Graph store unavailable") from exc

    by_label: dict[str, list[AffectedItem]] = defaultdict(list)
    for node in result.affected:
        by_label[node.label].append(
            AffectedItem(
                id=node.id,
                name=node.id,  # node id == name in the graph
                label=node.label,
                hop_distance=node.hop_distance,
                confidence=node.confidence.value,
            )
        )

    groups = [
        AffectedGroup(label=label, items=by_label[label], count=len(by_label[label]))
        for label in LABEL_ORDER
        if label in by_label
    ]

    return ImpactResponse(
        node_id=result.node_id,
        risk_score=result.risk_score,
        total_affected=len(result.affected),
        affected_groups=groups,
        explanation=result.explanation,
    )
