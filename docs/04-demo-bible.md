# Graphene — Demo Bible

**Tier legend:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform. Everything in this document is 🎬 by definition — it's the literal script for the 7–8 minute investor demo.

## Narrative arc

Problem (SAP dependency risk is invisible and expensive) → Proof (watch it become visible, live, from a spreadsheet) → Trust (the system tells you what it's confident about) → Payoff (AI reasoning grounded in a real graph, not a hallucinating chatbot) → Platform (this generalizes past SAP).

## Flagship scenario

**Flagship node:** `Z_PRICE_ENGINE` (swap to whatever the real curated dataset uses — the structure below doesn't change).

**Before any UI polish work happens:** validate that this node's blast radius is genuinely compelling — at least ~6–10 downstream nodes across at least 3 node types, with a mix of direct and inferred edges. If it isn't, pick a different flagship node or enrich the dataset *before* investing further build time. This check gates everything else in this document.

## Click-by-click walkthrough

| Time | Screen | Action | Graph state | Wow moment? |
|---|---|---|---|---|
| 0:00–0:30 | Landing | Presenter narrates the problem, no clicking — "SAP systems have thousands of undocumented dependencies. Nobody can safely answer 'what breaks if I change this.'" | Empty canvas, single upload CTA | — |
| 0:30–1:00 | Landing → Processing | Drag `flagship.xlsx` in | Stage ticker: "Parsing sheets → Resolving relationships → Building graph → 214 nodes, 386 edges" | Minor — sets up the big one |
| 1:00–1:15 | Processing → Explorer | Graph physically animates into position, camera auto-frames, then auto-zooms to the flagship cluster | Full graph visible, settling animation (1.5–2.5s) | **Wow #3** |
| 1:15–2:00 | Explorer | ⌘K, type `Z_PRICE`, one fuzzy result, click | Camera flies to node (600ms), node selected | — |
| 2:00–2:30 | Node detail drawer | Drawer slides in: name, business meaning, confidence badge, connection count | Drawer open, node highlighted | — |
| 2:30–4:00 | Impact Analysis panel | Click "What breaks if I modify this?" | Non-affected nodes dim to 15%; blast radius lights up color-coded by risk tier; risk score gauge animates in; affected list groups by type | **Wow #2** |
| 4:00–4:15 | Confidence toggle | Click "Show inferred relationships" switch off | Inferred (dashed, lower-confidence) edges disappear from the blast radius, direct-only view remains | Reinforces trust narrative |
| 4:15–6:00 | AI Chat panel | Ask, verbatim: *"Why is this risky?"* | Answer streams in; as node names are mentioned, corresponding graph nodes highlight in real time, synced to the text | **Wow #1 (the big one)** |
| 6:00–6:45 | AI Chat panel | Second question, verbatim: *"What's the safest way to test a change here?"* | Answer references the same highlighted subgraph, demonstrating reasoning *about* the graph, not around it | Reinforces Wow #1 |
| 6:45–7:15 | Zoom back out | Camera returns to full-graph view | Summary card: risk score, node count, confidence breakdown (direct vs. inferred) | — |
| 7:15–8:00 | Close | Presenter delivers the platform close: "This works today on Excel. In production, the Excel importer becomes an SAP RFC connector — same graph, same UI, zero changes above this layer. That's the platform." | Static, presenter-led | Ties directly to the "architecture scales" investor goal |

## Exact AI questions to rehearse (never improvise on stage)

1. **"Why is this risky?"** — primary flagship question, must land perfectly.
2. **"What's the safest way to test a change here?"** — secondary, shows reasoning depth.
3. **"What tables does this program write to?"** — simple factual fallback for if an investor wants to ask their own question live; keep this one bulletproof.

## Expected AI answer shapes (rehearse against, don't script verbatim)

- **Q1:** should name the risk score, name 2–3 of the most consequential downstream nodes by name, and explicitly distinguish direct vs. inferred dependencies — this is what proves grounding.
- **Q2:** should reference specific downstream Jobs/Transports from the blast radius, not generic testing advice. Generic advice means the Context Builder's subgraph summarization isn't feeding enough grounding and needs tuning before demo day.
- **Q3:** should list exactly the tables from the flagship dataset's `WRITES` edges — nothing more, nothing fabricated.

## Handling the edge case: sparse/empty node

If an investor clicks a node with genuinely no recorded dependencies (worth including intentionally in the dataset), the UI shows a designed empty state, not a dead end: *"No dependencies recorded for this node — this is exactly the kind of undocumented logic Graphene is built to surface once connected to live SAP."*

## Fallback plan

| Failure mode | Detection | Fallback |
|---|---|---|
| Ollama slow/times out mid-question | No token after ~3s | Presenter says "let me pull up a run from this morning" and switches to a pre-recorded screen capture of the exact same question/answer/highlight sequence, cued in a second browser tab |
| Ollama gives a wrong/off-narrative answer | Presenter judgment, live | Same as above — never let a bad live answer stand uncorrected |
| Graph fails to render / browser issue | Visual, immediate | Switch to a static screenshot deck (one image per beat above) with presenter narrating over it — rehearsed, not treated as a last resort |
| Network dependency of any kind | Immediate | Everything runs fully local (Ollama, Neo4j, FastAPI, React dev server) specifically so network is never a dependency — confirm explicitly before demo day |
| Investor asks an unscripted question mid-flow | Live | Answer verbally without touching the keyboard, or defer: "great question — let's dig into that after, I want to show you the rest of this flow first" |

## Timing

Hard 8-minute cap for the scripted flow; budget 5 extra minutes for live Q&A after. Rehearse with a visible timer until it reliably lands at 7:30–8:00. If consistently running long, cut Q2 before cutting anything visual.

## Presenter notes

- Narrate *while* things load — never stand in silence during the processing animation or graph settle.
- Say the risk score number out loud when it appears.
- On the "Excel → SAP RFC" close, physically gesture at an architecture slide if a second screen is available — this is the one moment worth a visual aid outside the app itself.
- If asked "is this real SAP data," answer immediately and honestly: *"This is a representative sample dataset — the graph engine and every interaction you just saw is real and runs identically against live SAP metadata once the RFC connector replaces the Excel importer."* Rehearse this exact answer so it doesn't come out defensive.
