# CLAUDE.md — Graphene Investor Demo

You are the sole implementer of Graphene, an SAP System Intelligence Platform, scoped to a
7–8 minute investor demo. You work ticket-by-ticket against the backlog. Do not build
anything beyond the current ticket's scope.

## Source-of-truth documents (read before starting any ticket)

- `docs/02-system-architecture.md` — system design, API contracts, directory layout
- `docs/03-graph-schema.md` — Neo4j node labels, relationship types, confidence model
- `docs/04-demo-bible.md` — the demo script every timing/animation spec traces back to
- `docs/06-linear-backlog.md` — the tickets (GRAPH-D0.1 … D5.3), each with Definition of Done

If a ticket and an architecture doc conflict, stop and ask rather than guessing.

## Non-negotiable rules

1. **The LLM never queries Neo4j directly.** All graph reads for AI chat go through the
   Context Builder: intent classification → bounded Cypher query template → traversal →
   subgraph summarization → prompt assembly. Never generate free-form Cypher from an LLM.
2. **`backend/domain/` has zero framework imports.** No `fastapi`, `neo4j`, `ollama`,
   `pydantic` (dataclasses are fine), or any adapter code under `domain/`. Ports are
   abstract interfaces with method signatures only.
3. **Confidence is a binary string enum:** `"direct" | "inferred"`. Stored as a string,
   never a boolean (a third tier must be addable later without migration).
4. **DI is hardcoded in `backend/api/dependencies.py`.** No plugin registry, no
   config-driven adapter loading.
5. **`LLMProvider` interface is strictly provider-agnostic.** No Ollama-specific
   parameters may leak into the interface signature.
6. **Import job is an in-memory dict**, not Celery/Redis — but its API contract
   (`job_id`, staged status enum `parsing → inferring → writing → complete`) must be
   shaped exactly like a real queue's would be.
7. **Fully local.** No cloud services, no external network dependency at runtime:
   Ollama, Neo4j (Docker), FastAPI, Vite dev server only.
8. **Design tokens are CSS variables** in `frontend/src/shared/design-system/tokens.css`.
   Never hardcode hex colors inside components.

## Stack

- Backend: Python 3.12, FastAPI, neo4j driver, pytest. Hexagonal (ports & adapters).
- Frontend: Vite + React + TypeScript + Tailwind. Typed API client generated from OpenAPI.
- Graph rendering: react-force-graph (pending Sprint 2 spike confirmation).
- LLM: local Ollama, SSE streaming.
- DB: Neo4j via `docker-compose.yml` at repo root.

## Explicitly out of scope (do not build, even if it seems helpful)

Claude/GPT adapter implementations (interface stub only) · SAP RFC importer (stub
returning 501) · real job queue · three-tier confidence · filter drawer (single toggle
only) · dashboard/history page · settings pages · auth · pagination/virtualization ·
adapter plugin registry · `visibility` enforcement.

## Working conventions

- One ticket per session. State the ticket ID, restate its Definition of Done, implement,
  then verify the DoD literally (run the test, run the curl, describe the manual check).
- Every sprint must end with something visibly working per the sprint exit bar in
  `docs/06-linear-backlog.md` — never leave a sprint as disconnected scaffolding.
- Write unit tests where a ticket's acceptance criteria name them (D0.1, D1.2, D3.1);
  don't add speculative test coverage elsewhere.
- Timing specs in tickets (600ms fly-to, 1.5–2.5s settle, sub-100ms search, <2s bulk
  write) are demo-script budgets, not suggestions — measure them.
- Commit at the end of each ticket with message `GRAPH-DX.Y: <summary>`.

## Repo layout target

```
graphene/
├── CLAUDE.md
├── docker-compose.yml          # Neo4j
├── docs/                       # the four source-of-truth docs above
├── demo-data/flagship.xlsx     # curated flagship dataset (D1.1)
├── backend/
│   ├── domain/{models/, graph_ports.py, importer_ports.py, llm_ports.py, services/}
│   ├── adapters/{graph_neo4j/, importer_excel/, llm_ollama/}
│   ├── api/{routes/, schemas/, dependencies.py}
│   └── main.py
└── frontend/src/{app/, features/, shared/}
```
