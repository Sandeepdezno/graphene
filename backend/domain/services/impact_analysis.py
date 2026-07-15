"""Impact analysis: blast-radius traversal + risk score (GRAPH-D3.1).

Pure domain logic - standard library only, no ``neo4j`` / ``fastapi`` imports
(CLAUDE.md rule 2). Graph data arrives via the ``GraphRepository`` port.

TRAVERSAL - the outbound impact set ("if I change X, what consumes/depends on it").
The direction rules below are derived from docs/flagship-blast-radius.md, which is
the source of truth for what "impacted" means. Per focus-node label:

    | Focus node        | Follows                                  | Skips                     |
    |-------------------|------------------------------------------|---------------------------|
    | Program           | WRITES->, CALLS->, IMPLEMENTS->, <-EXECUTES | READS (inputs), <-CHANGED |
    | FunctionModule    | WRITES->, CALLS->                        | READS (inputs)            |
    | Table             | <-READS (its consumers)                  | <-WRITES, <-CHANGED       |
    | Job / BAdI / Transport | (terminal)                          | everything                |

Per relationship type, the traversal direction and its rationale:

    - WRITES     : forward  (writer -> table)    - changing the writer changes the table's data
    - CALLS      : forward  (caller -> callee)   - the callee is part of X's execution footprint
    - IMPLEMENTS : forward  (program -> BAdI)     - changing the implementation changes the BAdI
    - EXECUTES   : backward (job -> program; from a program, reach the job) - the job fails if X breaks
    - READS      : backward (reader -> table; from a table, reach the reader) - a consumer breaks
                                                   when the table's data changes
    - CHANGED    : never traversed               - transports are change history, not dependents

Per affected node we carry: the shortest hop distance; the path confidence = the
minimum confidence along the shortest path (a node whose shortest path uses an
inferred edge is "inferred-impacted"); and the node label. Cycles are handled by
shortest-hop BFS with a visited set. A node with no outbound impact (e.g. the
sparse Z_LEGACY_REBATE_CALC) yields an empty radius - never an error.

RISK SCORE (0-100, deterministic):

    score = min(100, round( sum over affected nodes of
                              TYPE_WEIGHT[label] * PROXIMITY[hop] * CONFIDENCE[conf] ))

    TYPE_WEIGHT : Job 10, Transport 10, Program 8, FunctionModule 6, BAdI 6, Table 4
    PROXIMITY   : hop 1 -> 1.0, hop 2 -> 0.6, hop 3 -> 0.4, hop >=4 -> 0.25
    CONFIDENCE  : direct 1.0, inferred 1.1  (a small uncertainty premium)

In one sentence: add up every affected object, weighted by how operationally
critical its type is (jobs and transports weigh most), scaled by how close it is
in the dependency chain (closer counts more), plus a small premium for inferred
links, capped at 100.

Properties: deterministic (fixed weights); monotonic (every affected node adds a
strictly positive term, so more impact never lowers the score); bounded [0, 100].
For the flagship node Z_PRICE_ENGINE this yields 74.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

from domain.graph_ports import GraphRepository
from domain.models import Confidence


class NodeNotFoundError(Exception):
    """Raised when the analyzed node id is not present in the graph."""


# Singular nouns for the plain-language explanation.
LABEL_NOUN: dict[str, str] = {
    "Program": "program",
    "Table": "table",
    "FunctionModule": "function module",
    "BAdI": "BAdI",
    "Job": "job",
    "Transport": "transport",
}

# Fetch the whole (demo-scale) graph through the port for in-memory traversal.
_WHOLE_GRAPH = 1_000_000

TYPE_WEIGHT: dict[str, int] = {
    "Job": 10,
    "Transport": 10,
    "Program": 8,
    "FunctionModule": 6,
    "BAdI": 6,
    "Table": 4,
}
PROXIMITY: dict[int, float] = {1: 1.0, 2: 0.6, 3: 0.4}
PROXIMITY_FAR = 0.25
CONFIDENCE_FACTOR: dict[Confidence, float] = {
    Confidence.DIRECT: 1.0,
    Confidence.INFERRED: 1.1,
}


@dataclass(frozen=True)
class ImpactedNode:
    id: str
    label: str
    hop_distance: int
    confidence: Confidence


@dataclass
class ImpactResult:
    node_id: str
    affected: list[ImpactedNode] = field(default_factory=list)
    risk_score: int = 0
    explanation: str = ""


def _min_confidence(a: Confidence, b: Confidence) -> Confidence:
    # A path is only as trustworthy as its weakest edge.
    return Confidence.INFERRED if Confidence.INFERRED in (a, b) else Confidence.DIRECT


def _max_confidence(a: Confidence, b: Confidence) -> Confidence:
    # Between two equal-length paths, prefer the direct one.
    return Confidence.DIRECT if Confidence.DIRECT in (a, b) else Confidence.INFERRED


class ImpactAnalysisService:
    """Computes the outbound blast radius and risk score for a node."""

    def __init__(self, repo: GraphRepository) -> None:
        self._repo = repo

    def analyze(self, node_id: str) -> ImpactResult:
        graph = self._repo.get_graph(_WHOLE_GRAPH)
        label_of = {n["id"]: n["label"] for n in graph["nodes"]}
        if node_id not in label_of:
            raise NodeNotFoundError(node_id)

        # Adjacency, keyed for the direction rules documented above.
        out_writes: dict[str, list[tuple[str, Confidence]]] = defaultdict(list)
        out_calls: dict[str, list[tuple[str, Confidence]]] = defaultdict(list)
        out_implements: dict[str, list[tuple[str, Confidence]]] = defaultdict(list)
        table_readers: dict[str, list[tuple[str, Confidence]]] = defaultdict(list)
        program_execs: dict[str, list[tuple[str, Confidence]]] = defaultdict(list)

        for rel in graph["relationships"]:
            src, tgt = rel["source_id"], rel["target_id"]
            conf = Confidence(rel["confidence"])
            rtype = rel["type"]
            if rtype == "WRITES":
                out_writes[src].append((tgt, conf))
            elif rtype == "CALLS":
                out_calls[src].append((tgt, conf))
            elif rtype == "IMPLEMENTS":
                out_implements[src].append((tgt, conf))
            elif rtype == "READS":
                table_readers[tgt].append((src, conf))
            elif rtype == "EXECUTES":
                program_execs[tgt].append((src, conf))
            # CHANGED: never traversed.

        def successors(node: str) -> list[tuple[str, Confidence]]:
            label = label_of.get(node)
            if label in ("Program", "FunctionModule"):
                out = list(out_writes.get(node, ())) + list(out_calls.get(node, ()))
                if label == "Program":
                    out += list(out_implements.get(node, ()))
                    out += list(program_execs.get(node, ()))  # jobs that execute it
                return out
            if label == "Table":
                return list(table_readers.get(node, ()))
            return []  # Job / BAdI / Transport are terminal

        affected = _traverse(node_id, successors, label_of)
        return ImpactResult(
            node_id=node_id,
            affected=affected,
            risk_score=_risk_score(affected),
            explanation=_explanation(node_id, affected),
        )


def _traverse(start, successors, label_of) -> list[ImpactedNode]:
    # Shortest-hop BFS; at equal hop, prefer the direct path's confidence.
    best: dict[str, tuple[int, Confidence]] = {start: (0, Confidence.DIRECT)}
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        hop, conf = best[node]
        for neighbor, edge_conf in successors(node):
            if neighbor == start:
                continue
            new_hop = hop + 1
            new_conf = _min_confidence(conf, edge_conf)
            if neighbor not in best:
                best[neighbor] = (new_hop, new_conf)
                queue.append(neighbor)
            else:
                seen_hop, seen_conf = best[neighbor]
                if new_hop == seen_hop:
                    improved = _max_confidence(seen_conf, new_conf)
                    if improved is not seen_conf:
                        best[neighbor] = (seen_hop, improved)
                        queue.append(neighbor)  # re-propagate improved confidence

    return sorted(
        (
            ImpactedNode(id=nid, label=label_of[nid], hop_distance=hop, confidence=conf)
            for nid, (hop, conf) in best.items()
            if nid != start
        ),
        key=lambda n: (n.hop_distance, n.id),
    )


def _risk_score(affected: list[ImpactedNode]) -> int:
    total = 0.0
    for node in affected:
        total += (
            TYPE_WEIGHT.get(node.label, 0)
            * PROXIMITY.get(node.hop_distance, PROXIMITY_FAR)
            * CONFIDENCE_FACTOR[node.confidence]
        )
    return min(100, round(total))


def _noun(label: str, count: int) -> str:
    noun = LABEL_NOUN.get(label, label.lower())
    return noun if count == 1 else f"{noun}s"


def _explanation(node_id: str, affected: list[ImpactedNode]) -> str:
    n = len(affected)
    if n == 0:
        return (
            f"Modifying {node_id} affects no downstream objects — nothing recorded "
            "depends on it."
        )

    counts = Counter(node.label for node in affected)
    n_types = len(counts)
    # Highlight the two largest groups (by count, then label).
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:2]
    highlight = " and ".join(f"{count} {_noun(label, count)}" for label, count in top)

    text = (
        f"Modifying {node_id} affects {n} downstream object{'' if n == 1 else 's'} "
        f"across {n_types} type{'' if n_types == 1 else 's'}, including {highlight}."
    )

    inferred = sum(1 for node in affected if node.confidence is Confidence.INFERRED)
    if inferred:
        text += (
            f" {inferred} dependenc{'y is' if inferred == 1 else 'ies are'} inferred "
            "rather than explicitly documented."
        )
    return text
