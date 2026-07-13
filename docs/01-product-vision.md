# Graphene — Product Vision

**Tier legend used across all Graphene documents:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform

## Mission

Build an AI-powered SAP System Intelligence Platform. **The Knowledge Graph is the product. AI is only the interface.** This is not an SAP chatbot.

## The Problem

Large SAP systems accumulate thousands of custom programs, hundreds of custom tables, custom BAdIs, transports, jobs, and undocumented dependencies — with the actual business logic often trapped inside consultants' heads rather than anywhere written down. Nobody can easily answer questions like:

- What breaks if I change this program?
- Which transport changed this object?
- Which jobs execute this?
- Which programs use this table?
- Why is this business process failing?

This becomes acutely painful ahead of the mandatory S/4HANA migration wave, when every one of these unknowns turns into migration risk.

## What We're Building (and Deliberately Not Building)

- **Not** an SAP chatbot with a friendly interface bolted on.
- **Is** a knowledge graph of the SAP estate, with AI as a grounded query/explanation layer over it — the AI never answers from its own memory, only from the graph.
- **Long-term:** a Knowledge Graph Operating System (KGOS) — SAP is the first connector, not the whole product. This is the closing note of the pitch, not the opener (see `04-demo-bible.md`).

## Positioning

| Angle | Why it's a real differentiator |
|---|---|
| **Vendor-neutral** | SAP's own tooling (Custom Code Migration app, Readiness Check) inherently steers customers toward SAP's own roadmap and timeline. We don't. |
| **Graph-native, not report-native** | Competitors (consulting engagements, SNP, Panaya, Rimini Street) typically hand over a PDF or spreadsheet. We hand over an explorable, queryable system. |
| **Fast time-to-value** | Excel-to-graph in an afternoon vs. a multi-week consulting discovery engagement. |
| **Honest about confidence** | Every relationship in the graph carries a source and a confidence level (direct vs. inferred). This is not a caveat we hide — it's the trust mechanism that makes the whole product credible. See `03-graph-schema.md`. |

## Competitive Landscape

SNP, Panaya, Rimini Street, SAP's own Custom Code Migration app and Readiness Check, and every Big 4 consulting practice already sell "what happens if I touch this" analysis for S/4 migrations — and all of them are adding AI chat layers too. Differentiation has to be sharper than "AI over SAP data"; it rests on vendor-neutrality, graph-native exploration, and speed, stated explicitly rather than left for the audience to infer.

## Target Customer & Business Model Hypothesis

- **Land:** fixed-fee "Migration Readiness Audit" — one SAP system, ~2-week turnaround.
- **Expand:** annual "Living Documentation" subscription per SAP system, once the audit has proven value.

This is a hypothesis, not a finalized model — but it needs to be stated explicitly in any investor conversation, since "how does this make money" is a guaranteed question.

## Known Open Risks

- **SAP reality is messier than a clean graph model suggests.** Dynamic calls (`CALL FUNCTION` with a variable name), BAdI implementations selected at runtime, and table access routed through views/BAPIs can't all be resolved statically. Phase 1 (demo + early MVP) handles statically-resolvable dependencies with full confidence; dynamic/runtime-resolved dependencies are explicitly flagged as inferred/low-confidence, never silently hidden.
- **Founder-market fit.** This is a trust sale into enterprise IT. Without SAP consulting/implementation credibility on the founding team (or a formally engaged advisor), this is the first question in any funding conversation — needs to be addressed in parallel with product work, not after.
- **No security/access model yet.** Fine-grained graph RBAC by SAP authorization object is a stated roadmap item (🚀), not something the demo or early MVP builds.

## Long-Term Vision — KGOS

Eventually: SAP ECC, SAP S/4, transport intelligence, root-cause analysis, documentation generation, migration intelligence, enterprise search, and knowledge discovery — generalizing the same graph-native approach beyond SAP to other enterprise systems. This is the ambitious close of the story, told only after the narrow SAP wedge has been proven.
