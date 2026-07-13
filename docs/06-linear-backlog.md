# Graphene — Linear Backlog (Investor Demo, Sprints 0–5)

**Tier legend:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform. Every ticket below is 🎬-scoped unless otherwise noted. Format assumes Claude Code Opus as the implementer working directly against `02-system-architecture.md` and `03-graph-schema.md`.

---

## Sprint 0 — Architecture Scaffold & "Hello Graph"

**GRAPH-D0.1 — Domain models + ports**
- *Objective:* Define the domain layer: node models (`Program`, `Table`, `FunctionModule`, `BAdI`, `Job`, `Transport`) with `source`/`confidence`/`last_updated` fields (confidence binary: `direct` \| `inferred`), plus abstract interfaces `GraphRepository`, `SourceImporter`, `LLMProvider`.
- *Context:* The hexagonal core everything else plugs into. Keep it dependency-free — no FastAPI, no Neo4j driver, no framework imports here.
- *Acceptance Criteria:* Models instantiate with zero framework imports; interfaces define method signatures only; unit tests cover instantiation of each model.
- *Files likely affected:* `backend/domain/models/*.py`, `backend/domain/graph_ports.py`, `backend/domain/importer_ports.py`, `backend/domain/llm_ports.py`
- *Dependencies:* None
- *Definition of Done:* `pytest backend/domain/` passes; no import of `neo4j`, `fastapi`, or `ollama` anywhere under `domain/`.

**GRAPH-D0.2 — Neo4j adapter + FastAPI skeleton + health route**
- *Objective:* Implement `GraphRepository` against the Neo4j driver (connect + health-check only); stand up FastAPI with DI wiring the adapter to the port; expose `/health`.
- *Context:* Proves the adapter pattern works before any real feature is built on top of it.
- *Acceptance Criteria:* `/health` returns 200 with Neo4j connection status; app boots with `uvicorn` with no manual wiring outside `dependencies.py`.
- *Files likely affected:* `backend/adapters/graph_neo4j/`, `backend/api/main.py`, `backend/api/dependencies.py`, `backend/api/routes/health.py`
- *Dependencies:* D0.1
- *Definition of Done:* Local Neo4j running via docker-compose; `curl localhost:8000/health` returns 200.

**GRAPH-D0.3 — OpenAPI schema baseline + typed frontend client**
- *Objective:* Auto-generated `/docs` with every v1 route stubbed (501 for unbuilt ones); generate a typed TS client from that schema.
- *Context:* Cheap now, prevents frontend/backend contract drift for the rest of the build.
- *Acceptance Criteria:* `/docs` lists every route from `02-system-architecture.md`'s API table; generated client compiles with zero `any` types.
- *Files likely affected:* `backend/api/routes/*.py` (stubs), `backend/api/schemas/*.py`, `frontend/src/shared/api-client/`
- *Dependencies:* D0.2
- *Definition of Done:* `npm run generate-client` produces a compiling client against the live `/docs` schema.

**GRAPH-D0.4 — React app skeleton + dark theme tokens**
- *Objective:* Vite + React + TS + Tailwind scaffold with design tokens wired as CSS variables; routing shell; nav rail.
- *Context:* Establishes the visual foundation so every later screen is styled correctly from first paint.
- *Acceptance Criteria:* App boots, renders empty dark-themed layout; tokens are CSS variables, not hardcoded hex in components.
- *Files likely affected:* `frontend/src/app/`, `frontend/src/shared/design-system/tokens.css`
- *Dependencies:* None (parallel to D0.1–D0.3)
- *Definition of Done:* Visual check confirms dark background, correct font loaded.

**GRAPH-D0.5 — "Hello Graph" seed + bare canvas render**
- *Objective:* Manually seed 5 nodes/edges directly into Neo4j; render them via a minimal `/graph` endpoint on a bare canvas.
- *Context:* This sprint's actual "working product" bar — proof the full stack round-trips correctly before real feature work begins.
- *Acceptance Criteria:* Refreshing the page fetches and renders the 5 seeded nodes from a live API call, not mock data.
- *Files likely affected:* `backend/api/routes/graph.py` (minimal), `frontend/src/features/graph-explorer/` (bare version)
- *Dependencies:* D0.1, D0.2, D0.3, D0.4
- *Definition of Done:* Restarting the backend, then refreshing the frontend, still shows the 5 nodes — proves it reads from Neo4j, not stale state.

---

## Sprint 1 — Excel Import

**GRAPH-D1.1 — Excel sheet contract + flagship dataset**
- *Objective:* Write the spec for expected sheet/column structure and, in the same ticket, curate the flagship demo workbook against it.
- *Context:* The contract and the flagship dataset are designed together so the demo scenario is provably rich before any pipeline code exists — see the validation gate in `04-demo-bible.md` and `05-development-roadmap.md`.
- *Acceptance Criteria:* Written schema doc; `flagship.xlsx` checked in; manual walk confirms the target node's blast radius meets the demo bar.
- *Files likely affected:* `docs/excel-schema.md`, `demo-data/flagship.xlsx`
- *Dependencies:* None
- *Definition of Done:* A human can trace the flagship node's full blast radius by reading the spreadsheet alone, and it's genuinely interesting.

**GRAPH-D1.2 — Excel parser + relationship inference**
- *Objective:* Parse the workbook per D1.1's contract into domain nodes/edges; tag `source=excel_import`, `confidence=direct` for explicit rows and `confidence=inferred` for derived/transitive relationships.
- *Context:* The engine behind the "we tell you what we don't know" trust narrative — keep the rule simple per `03-graph-schema.md`'s binary model.
- *Acceptance Criteria:* Parsing `flagship.xlsx` produces the exact expected node/edge count and confidence split, verified against a hand-computed expectation.
- *Files likely affected:* `backend/adapters/importer_excel/parser.py`, `backend/adapters/importer_excel/inference.py`
- *Dependencies:* D1.1, D0.1
- *Definition of Done:* Unit test asserts exact node/edge/confidence counts against the flagship file.

**GRAPH-D1.3 — Import endpoint + lightweight async job**
- *Objective:* `POST /import/excel` accepts upload, validates against D1.1's contract, runs the build as a background task using an in-memory job dict; `GET /import/{job_id}/status` reports stage.
- *Context:* Delivers the processing-animation wow moment with minimum infra — intentionally not production-grade queueing (see `05-development-roadmap.md` Phase 2).
- *Acceptance Criteria:* Status transitions visibly through `parsing → inferring → writing → complete`; malformed files return a clear validation error.
- *Files likely affected:* `backend/api/routes/import.py`, `backend/domain/services/import_job.py`
- *Dependencies:* D1.2, D0.2
- *Definition of Done:* Uploading `flagship.xlsx` completes the full status sequence and the graph is queryable afterward.

**GRAPH-D1.4 — Upload UI + processing stage ticker**
- *Objective:* Dropzone component with file-type validation; processing screen that polls D1.3's status endpoint and animates the stage ticker per `04-demo-bible.md`'s 0:30–1:00 beat.
- *Context:* First visible wow-moment component in the actual demo flow.
- *Acceptance Criteria:* Non-`.xlsx` rejected client-side; stage ticker updates within 500ms of a backend stage change; auto-navigates to the graph explorer on completion.
- *Files likely affected:* `frontend/src/features/import/Dropzone.tsx`, `frontend/src/features/import/Processing.tsx`
- *Dependencies:* D1.3, D0.4
- *Definition of Done:* Live walkthrough of the demo bible's 0:00–1:15 beats works end to end against the flagship file.

**GRAPH-D1.5 — Bulk graph write + schema constraints**
- *Objective:* Neo4j uniqueness constraints per node label; efficient batched (`UNWIND`-based) writer for D1.2's parser output, replacing D0.5's manual seed path.
- *Context:* Tune write time to roughly match the processing animation's pacing from D1.4 — not artificially slow, not embarrassingly instant.
- *Acceptance Criteria:* Writing the full flagship dataset completes in under 2 seconds; duplicate-name writes are rejected, not silently overwritten.
- *Files likely affected:* `backend/adapters/graph_neo4j/writer.py`, Cypher migration script
- *Dependencies:* D0.2, D1.2
- *Definition of Done:* Re-running the import against the same file twice either upserts cleanly or errors clearly — no duplicate nodes.

---

## Sprint 2 — Graph Explorer + Search

**GRAPH-D2.1 — Bounded graph read + node detail read**
- *Objective:* `GET /graph` (capped, truncation warning if exceeded) and `GET /graph/node/{id}` (node + neighbors + relationship confidence), replacing D0.5's minimal version.
- *Context:* The real data layer the entire Explorer UI sits on.
- *Acceptance Criteria:* Full flagship graph returns within the cap with no truncation; node detail includes confidence per relationship.
- *Files likely affected:* `backend/api/routes/graph.py`, `backend/adapters/graph_neo4j/reader.py`
- *Dependencies:* D1.5
- *Definition of Done:* Both endpoints documented and passing in `/docs`.

**GRAPH-D2.2 — Graph rendering engine + node-type colors + legend**
- *Objective:* Wrap the chosen graph library with pan/zoom and styling hooks; apply node-type color tokens; build the legend modal.
- *Context:* The product's visual identity — match the design tokens exactly, don't approximate.
- *Acceptance Criteria:* Renders the full flagship graph at 60fps pan/zoom; colors match tokens exactly; legend opens/closes correctly.
- *Files likely affected:* `frontend/src/shared/graph-engine/`, `frontend/src/features/graph-explorer/Legend.tsx`
- *Dependencies:* D2.1, D0.4
- *Definition of Done:* Side-by-side visual check against the design token spec, pixel-matched.

**GRAPH-D2.3 — Settle animation + camera fly-to**
- *Objective:* Force-directed initial layout animation (1.5–2.5s); programmatic camera fly-to for any node id, completing within 600ms.
- *Context:* This is Wow Moment #3 from `04-demo-bible.md` — the timing numbers are the rehearsed demo script's timing budget, not arbitrary.
- *Acceptance Criteria:* Settle timing and fly-to timing both measured and within spec on the actual demo hardware.
- *Files likely affected:* `frontend/src/shared/graph-engine/animation.ts`, `frontend/src/shared/graph-engine/camera.ts`
- *Dependencies:* D2.2
- *Definition of Done:* Timed manual test on the laptop that will run the demo.

**GRAPH-D2.4 — Node detail drawer (including empty-state)**
- *Objective:* Slide-in drawer with name/description/business meaning/confidence badge/connections; include the empty/no-dependencies state copy from `04-demo-bible.md`.
- *Context:* Closes the gap where an investor clicking a sparse node would otherwise hit a dead end.
- *Acceptance Criteria:* Drawer renders correctly for both a richly-connected node and a zero-connection node, with the specific empty-state copy.
- *Files likely affected:* `frontend/src/features/graph-explorer/NodeDrawer.tsx`
- *Dependencies:* D2.1, D2.2
- *Definition of Done:* Manual test clicking both a hub node and an intentionally sparse node in the flagship dataset.

**GRAPH-D2.5 — Search endpoint + ⌘K overlay**
- *Objective:* `GET /search?q=` fuzzy match; keyboard-triggered overlay with arrow-key nav, wired to D2.3's fly-to and D2.4's drawer on selection.
- *Context:* Delivers the 1:15–2:00 beat of the demo script.
- *Acceptance Criteria:* Sub-100ms search response; selecting a result flies the camera and opens the drawer in one motion.
- *Files likely affected:* `backend/api/routes/search.py`, `frontend/src/features/search/SearchOverlay.tsx`
- *Dependencies:* D2.1, D2.3, D2.4
- *Definition of Done:* Live timed test of the 1:15–2:00 demo beat against the flagship dataset.

**GRAPH-D2.6 — "Show inferred relationships" toggle**
- *Objective:* Single switch (not a full filter drawer) that hides/shows `confidence=inferred` edges in the current view, with a fade transition.
- *Context:* Delivers the 4:00–4:15 trust-narrative beat.
- *Acceptance Criteria:* Toggling hides only inferred edges, fades rather than hard-cuts, re-toggling restores them correctly.
- *Files likely affected:* `frontend/src/features/graph-explorer/ConfidenceToggle.tsx`
- *Dependencies:* D2.2
- *Definition of Done:* Live timed test of the 4:00–4:15 demo beat.

---

## Sprint 3 — Impact Analysis (the flagship feature)

**GRAPH-D3.1 — Blast-radius traversal + risk score**
- *Objective:* Domain service computing all nodes reachable outbound from a given node, with hop-distance and confidence carried; risk score (0–100) from blast-radius size × confidence mix.
- *Context:* The core logic behind the demo's biggest moment — correctness matters more here than almost anywhere else, since Sprint 4's AI chat answers are grounded in this exact traversal.
- *Acceptance Criteria:* Traversal output matches a hand-computed expected set for the flagship node exactly; risk score formula documented and deterministic.
- *Files likely affected:* `backend/domain/services/impact_analysis.py`
- *Dependencies:* D1.5, D0.1
- *Definition of Done:* Unit test against the flagship node's known expected blast radius passes exactly.

**GRAPH-D3.2 — Impact endpoint**
- *Objective:* `GET /impact/{node_id}` returns affected nodes grouped by type, risk score, plain-language explanation.
- *Context:* Straightforward wiring of D3.1 into the API layer.
- *Acceptance Criteria:* Response shape matches `02-system-architecture.md`'s API contract.
- *Files likely affected:* `backend/api/routes/impact.py`
- *Dependencies:* D3.1
- *Definition of Done:* Documented and passing in `/docs`.

**GRAPH-D3.3 — Impact panel UI + risk gauge**
- *Objective:* Panel with animated risk gauge, grouped affected-items list (Program/Table/Job/Transport), explanation text.
- *Context:* Delivers the 2:30–4:00 beat — the demo's emotional peak before the AI chat.
- *Acceptance Criteria:* Gauge animates on load; list grouping matches the IA spec exactly.
- *Files likely affected:* `frontend/src/features/impact-analysis/Panel.tsx`
- *Dependencies:* D3.2, D0.4
- *Definition of Done:* Live timed test of the 2:30–4:00 demo beat.

**GRAPH-D3.4 — Graph dim/highlight sync**
- *Objective:* Non-affected nodes dim to 15% opacity, affected nodes color-code by risk tier, synced to the panel opening/closing.
- *Context:* This is Wow Moment #2 — the visual payoff of D3.1's correctness.
- *Acceptance Criteria:* Visual state matches the graph styling spec exactly; reverts cleanly when the panel closes.
- *Files likely affected:* `frontend/src/features/graph-explorer/` (highlight state integration)
- *Dependencies:* D3.3, D2.2
- *Definition of Done:* Live timed test, including closing the panel and confirming the graph returns to its default state.

---

## Sprint 4 — AI Chat

**GRAPH-D4.1 — Ollama adapter (streaming)**
- *Objective:* Implement `LLMProvider` against local Ollama with SSE-compatible streaming. Claude adapter is explicitly not built this sprint — only the interface exists from D0.1.
- *Context:* A single working LLM path is sufficient for the demo; the port abstraction alone carries the "future: Claude/GPT/Gemini" story.
- *Acceptance Criteria:* Streams tokens from a test prompt with no buffering delay beyond actual generation.
- *Files likely affected:* `backend/adapters/llm_ollama/`
- *Dependencies:* D0.1
- *Definition of Done:* Manual test streaming a real response end to end.

**GRAPH-D4.2 — Intent classification + query templates**
- *Objective:* Classify a user question into a query-template category (impact / search / general); map to a bounded Cypher query template. **No free-form Cypher generated by the LLM, ever.**
- *Context:* This constraint is what keeps the AI chat grounded and safe — non-negotiable, not a nice-to-have.
- *Acceptance Criteria:* All three rehearsed demo questions route correctly and consistently.
- *Files likely affected:* `backend/domain/services/context_builder/intent.py`, `.../query_templates.py`
- *Dependencies:* D0.1, D3.1 (impact template reuses the blast-radius service)
- *Definition of Done:* Each of the three rehearsed questions produces the correct template selection in a test.

**GRAPH-D4.3 — Subgraph summarization + prompt assembly**
- *Objective:* Convert the query template's returned subgraph into a token-bounded natural-language context block for the LLM prompt.
- *Context:* What makes Q2 ("safest way to test a change") reference actual Jobs/Transports instead of giving generic advice — tune this specifically against that question during rehearsal.
- *Acceptance Criteria:* Prompt stays under the token budget on the flagship graph; manual review confirms the summarized context contains the specific node names needed for each rehearsed question.
- *Files likely affected:* `backend/domain/services/context_builder/summarizer.py`
- *Dependencies:* D4.2
- *Definition of Done:* All three rehearsed questions produce grounded, correctly-specific answers in manual testing (per `04-demo-bible.md`'s expected-answer shapes).

**GRAPH-D4.4 — Chat streaming endpoint**
- *Objective:* `POST /chat` wires intent → query → summarize → LLM call → SSE stream, including a `highlighted_node_ids` field alongside the streamed text.
- *Context:* `highlighted_node_ids` is what makes Wow Moment #1 possible — needs to arrive in sync with the relevant part of the streamed text, not all at once at the end.
- *Acceptance Criteria:* Response includes correctly-ordered `highlighted_node_ids` corresponding to when each node is mentioned in the stream.
- *Files likely affected:* `backend/api/routes/chat.py`
- *Dependencies:* D4.1, D4.3
- *Definition of Done:* Manual test confirms highlight IDs arrive in an order matching the text.

**GRAPH-D4.5 — Chat panel UI + graph-highlight sync**
- *Objective:* Message thread with token-by-token streaming render; consume `highlighted_node_ids` to highlight graph nodes live as the answer streams.
- *Context:* The single most important ticket in this backlog for investor impact — rehearse this interaction more than any other.
- *Acceptance Criteria:* Highlight timing visibly correlates with the text mentioning that node, on the actual demo hardware.
- *Files likely affected:* `frontend/src/features/ai-chat/ChatPanel.tsx`, graph-engine highlight integration
- *Dependencies:* D4.4, D2.2
- *Definition of Done:* Live timed test of the full 4:15–6:45 demo beats, on demo hardware, at least 5 times consecutively without a glitch.

---

## Sprint 5 — Demo Hardening

**GRAPH-D5.1 — Design token sweep**
- *Objective:* Replace any ad-hoc styling introduced under time pressure in Sprints 1–4 with the actual design tokens.
- *Context:* Housekeeping pass — expected to surface small inconsistencies, not a redesign. First to cut if the timeline compresses (per `05-development-roadmap.md`).
- *Acceptance Criteria:* Visual QA checklist passes for every screen touched during the demo flow.
- *Files likely affected:* Across `frontend/src/features/*`
- *Dependencies:* All Sprint 2–4 UI tickets
- *Definition of Done:* Full demo run-through with no visibly inconsistent styling.

**GRAPH-D5.2 — Canned Q&A rehearsal + guardrails**
- *Objective:* Rehearse the three approved questions until reliably correct; add a graceful-decline behavior for out-of-scope questions instead of a hallucinated answer.
- *Context:* Directly closes the "AI doesn't know" risk and the fallback-plan requirement from `04-demo-bible.md`.
- *Acceptance Criteria:* All three questions pass 5 consecutive manual runs; an intentionally out-of-scope question produces a graceful decline, not a fabricated answer.
- *Files likely affected:* `backend/domain/services/context_builder/*` (prompt tuning)
- *Dependencies:* Sprint 4 complete
- *Definition of Done:* Rehearsal log showing 5/5 pass on each of the three questions plus the decline test.

**GRAPH-D5.3 — Performance pass + fallback asset capture**
- *Objective:* Confirm the full 8-minute flagship flow runs with no visible lag on the actual demo hardware; record the video and capture the screenshot deck specified in `04-demo-bible.md`'s fallback plan.
- *Context:* The last gate before the demo is "ready" — the fallback assets don't exist until this ticket is done.
- *Acceptance Criteria:* Full flow completes within the 7:30–8:00 window on demo hardware, 3 consecutive times; fallback video and screenshot deck saved and tested cold (not right after a successful run).
- *Files likely affected:* N/A (rehearsal + asset capture, not code)
- *Dependencies:* D5.1, D5.2
- *Definition of Done:* Fallback assets exist, are tested, and the presenter has run the full flow end-to-end at least 3 times without intervention.
