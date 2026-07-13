# Graphene — System Architecture

**Tier legend:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform

This document reflects the **current, scope-cut architecture** — i.e. after trimming the original full design down to exactly what the Investor Demo needs, while preserving the seams required for Production MVP and Long-Term Platform to grow out of it without a rewrite. See `05-development-roadmap.md` for how this gets built over time.

## Guiding rule (non-negotiable)

**The LLM never queries Neo4j directly.** Every graph read goes through the Context Builder, which selects a bounded query template, executes it, and returns a summarized subgraph. This single rule is what makes the Ollama→Claude swap and the Excel→SAP-RFC swap safe and demonstrable rather than aspirational.

## System overview

```
┌─────────────┐     ┌──────────────────────────────────────────┐     ┌─────────────┐
│   React UI   │◄──►│                FastAPI Backend             │◄──►│    Neo4j     │
│ (TypeScript, │HTTP│  ┌────────────┐  ┌─────────────────────┐  │Bolt│   Graph DB   │
│  Tailwind)   │/SSE│  │   API      │  │   Context Builder    │  │    │              │
└─────────────┘     │  │  (routes)  │─►│ (query planning,     │  │    └─────────────┘
                     │  └─────┬──────┘  │  traversal, summary,│  │
                     │        │         │  prompt assembly)    │  │
                     │        ▼         └──────────┬───────────┘  │
                     │  ┌────────────┐              │              │
                     │  │  Domain    │              ▼              │
                     │  │  Services  │   ┌─────────────────────┐  │
                     │  │ (ports)    │   │   LLM Adapter Port   │  │
                     │  └─────┬──────┘   │  (Ollama — built;     │  │
                     │        │          │   Claude/GPT/Gemini —  │  │
                     │        ▼          │   interface only)     │  │
                     │  ┌────────────┐   └─────────────────────┘  │
                     │  │ Importer   │                             │
                     │  │ Adapter    │                             │
                     │  │ Port       │                             │
                     │  │ (Excel —   │                             │
                     │  │  built;    │                             │
                     │  │  SAP RFC — │                             │
                     │  │  interface │                             │
                     │  │  only)     │                             │
                     │  └────────────┘                             │
                     └──────────────────────────────────────────────┘
```

## Backend — Hexagonal (Ports & Adapters), demo-scoped

```
backend/
├── domain/                        # Pure business logic, zero framework deps
│   ├── models/                    # Program, Table, FunctionModule, BAdI, Job, Transport
│   ├── graph_ports.py             # GraphRepository interface
│   ├── importer_ports.py          # SourceImporter interface
│   ├── llm_ports.py               # LLMProvider interface — kept strictly provider-agnostic
│   └── services/
│       ├── impact_analysis.py     # blast-radius traversal + risk score
│       ├── search_service.py
│       └── context_builder/       # intent → query template → traversal → summarize → prompt
├── adapters/
│   ├── graph_neo4j/                 # implements GraphRepository — 🎬🏗️ built
│   ├── importer_excel/              # implements SourceImporter — 🎬🏗️ built
│   ├── importer_sap_rfc/            # implements SourceImporter — 🚀 interface stub only
│   ├── llm_ollama/                  # implements LLMProvider — 🎬🏗️ built
│   └── llm_claude/                  # implements LLMProvider — 🚀 not implemented; port alone carries the story
├── api/
│   ├── routes/                      # import.py, graph.py, search.py, impact.py, chat.py, health.py
│   ├── schemas/                     # Pydantic request/response models
│   └── dependencies.py              # DI wiring: hardcoded adapter bindings for now, not a config-driven registry
└── main.py
```

**Deliberate simplification:** no general adapter registry or config-driven adapter loader — `dependencies.py` hardcodes which adapter is wired in. Building a generic plugin system before there's a second real adapter to plug in is premature; the port interfaces are the part worth getting right early, not the loading mechanism.

## Frontend architecture

```
frontend/
├── src/
│   ├── app/                        # routing, layout shell, providers
│   ├── features/
│   │   ├── import/                 # upload flow, processing animation
│   │   ├── graph-explorer/         # canvas, node/edge rendering, zoom/pan, physics, highlight sync
│   │   ├── search/                 # ⌘K overlay, jump-to-node
│   │   ├── impact-analysis/        # risk gauge, affected-items panel
│   │   └── ai-chat/                # streaming chat panel, graph-highlight sync
│   ├── shared/
│   │   ├── design-system/          # tokens, primitives — see design system spec in prior architecture pass
│   │   ├── graph-engine/           # wrapper around the graph rendering library
│   │   └── api-client/             # typed client generated from the OpenAPI schema
│   └── main.tsx
```

## API boundaries (v1)

| Method | Path | Purpose | Notes |
|---|---|---|---|
| `POST` | `/api/v1/import/excel` | Upload Excel, trigger graph build | Backed by an in-memory job dict, not a real queue — see roadmap |
| `GET` | `/api/v1/import/{job_id}/status` | Poll import/build progress | Status contract shaped identically to what a real queue would return, so swapping the implementation later doesn't touch the frontend |
| `GET` | `/api/v1/graph` | Bounded full graph for the explorer view | Capped, with truncation warning if exceeded |
| `GET` | `/api/v1/graph/node/{id}` | Node detail + neighbors + relationship confidence | |
| `GET` | `/api/v1/search?q=` | Fuzzy search over programs/tables/jobs | Sub-100ms target |
| `GET` | `/api/v1/impact/{node_id}` | Blast radius, risk score, grouped affected items | |
| `POST` | `/api/v1/chat` | AI chat over the graph, SSE streamed | Response includes `highlighted_node_ids` synced to the streamed text |
| `GET` | `/api/v1/health` | Liveness/readiness | |
| `POST` | `/api/v1/import/sap-rfc` | *(stub, 501)* | 🚀 |

Every endpoint is documented via OpenAPI/Swagger from day one — cheap now, prevents frontend/backend drift for the rest of the build.

## Confidence & provenance model (summary — full detail in `03-graph-schema.md`)

Every node and relationship carries `source` and `confidence`. Confidence is stored as a string enum (`direct` | `inferred`) rather than a boolean specifically so a production build can reintroduce a finer-grained tier later without a schema migration.

## Scalability path

| Concern | 🎬 Investor Demo | 🏗️ Production MVP | 🚀 Long-Term Platform |
|---|---|---|---|
| Data volume | One curated Excel workbook, small graph | One full SAP system, tens of thousands of nodes | Multi-system, multi-tenant, millions of nodes |
| Tenancy | Single hardcoded tenant | Single-tenant per deployment | Multi-tenant SaaS with graph partitioning |
| LLM | Ollama only, built | Ollama default + Claude opt-in, both real | Multi-provider, per-tenant model choice |
| Import | Manual Excel upload, in-memory job tracking | Excel + scheduled SAP RFC sync, real job queue | Streaming/event-driven connector framework — SAP first, then other ERPs (the KGOS vision) |
| Auth | None | SSO (SAML/OIDC), basic RBAC | Fine-grained graph-level RBAC by SAP authorization object |
| Confidence model | Binary (direct/inferred) | Same, extensible without migration | Possible finer-grained tiering if customer feedback warrants it |

## Engineering trade-offs — where to cut effort now, where not to

| Decision | Cut effort now by | Preserve flexibility by |
|---|---|---|
| Ports/adapters | Hardcoding adapter bindings, no plugin registry | Keeping port interfaces strict and framework-free |
| Import job | In-memory dict, not Celery/Redis | Matching the real-queue API contract (`job_id`, staged status enum) exactly |
| Confidence | Binary tier only | Storing as a string enum, not boolean |
| LLM provider | Building only Ollama | Keeping `LLMProvider` genuinely provider-agnostic — no Ollama-specific parameters leaking into the interface |
| Graph size | No pagination/virtualization at demo scale | Capping via an explicit parameter in the graph-engine wrapper's API, even if unused today |
| Auth | None | Structuring route handlers so adding an auth dependency later is a one-line addition, not a rewrite |
