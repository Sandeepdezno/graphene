# Graphene — Development Roadmap

**Tier legend:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform

## Phase 1 — Investor Demo (🎬, current focus, Sprints 0–5)

Scoped for one implementer (founder + Claude Code Opus), not a large team. Every sprint ends with something visibly working, not internal scaffolding alone. Full ticket detail lives in `06-linear-backlog.md`.

| Sprint | Theme | Ends with (working product) |
|---|---|---|
| **Sprint 0** | Architecture scaffold + "Hello Graph" | Full-stack round trip: a hand-seeded 5-node graph renders in a bare React canvas via the real API |
| **Sprint 1** | Excel import | Real Excel upload produces a real graph in Neo4j, visible via API (still unstyled) |
| **Sprint 2** | Graph Explorer + Search | Polished, searchable Graph Explorer — the visual core of the product |
| **Sprint 3** | Impact Analysis | The flagship "what breaks if I touch this" moment works end to end |
| **Sprint 4** | AI Chat | Full AI chat with graph-highlight sync — the complete flagship narrative is demoable |
| **Sprint 5** | Demo hardening | Polished, rehearsed, with fallback assets captured — see `04-demo-bible.md` |

**Sequencing risk to protect against:** don't let polish (Sprint 5) expand to fill available time. If the real days-until-pitch is short, cut Sprint 5 down to just rehearsal (D5.2) and fallback capture (D5.3), and drop the design-token sweep (D5.1) first.

**Gate before Sprint 2 begins:** the flagship node's blast radius must be validated as genuinely compelling (see `04-demo-bible.md`) — this is a data/content check, not a code task, and it's cheaper to do before UI polish than after.

## Phase 2 — Production MVP (🏗️, after the demo lands)

Not yet ticketed at the Linear level — themes to scope once Phase 1 is proven:

- **Real SAP RFC connector**, implementing the `SourceImporter` port already defined in `02-system-architecture.md` — this is the concrete proof of the "Excel → SAP RFC, zero UI change" pitch claim.
- **Real async job infrastructure** (replacing the in-memory dict from Sprint 1) — the API contract was deliberately shaped to match this from day one.
- **Claude/GPT adapter**, implementing the already-defined `LLMProvider` port for real, alongside Ollama.
- **Auth** — SSO (SAML/OIDC) and basic RBAC.
- **Incremental graph updates** — diff-based sync rather than full rebuild, needed once SAP RFC sync runs on a schedule.
- **Dashboard with real history** — once there's more than one import, the risk-trend view cut from the demo becomes meaningful.
- **Settings pages** — connector configuration, team management, billing.
- **Finer-grained confidence tiering**, if customer feedback shows the binary direct/inferred model is insufficient — the schema already supports this without migration (`03-graph-schema.md`).
- **Pricing/billing implementation** of the land-and-expand hypothesis from `01-product-vision.md`.

## Phase 3 — Long-Term Platform (🚀, KGOS vision)

- Multi-tenant SaaS with graph partitioning.
- Multi-connector framework — SAP first, then other ERPs, generalizing the graph-native approach described in `01-product-vision.md`.
- Fine-grained graph-level RBAC by SAP authorization object, using the `visibility` field already reserved in the schema.
- Multi-provider LLM support, per-tenant model choice.
- Full KGOS capabilities: transport intelligence, root-cause analysis, documentation generation, migration intelligence, enterprise search, knowledge discovery.

## What NOT to build ahead of schedule

Explicitly deferred out of Phase 1, even though earlier drafts of this architecture included them — see the scope-cut rationale in the CTO review that produced this roadmap:

- A general adapter plugin registry (hardcoded DI wiring is sufficient until there's a second real adapter to plug in).
- A real job queue (Celery/Redis) — the API contract is queue-shaped, the implementation doesn't need to be yet.
- A working second LLM adapter — the port abstraction alone carries the multi-provider story for the demo.
- Three-tier confidence — binary is sufficient and migration-free to extend later.
- A full filter drawer — a single toggle covers the demo's trust narrative.
- A dashboard/history view — no data exists yet to make one meaningful.
