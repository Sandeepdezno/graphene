# Graphene — Graph Schema (Neo4j)

**Tier legend:** 🎬 Investor Demo · 🏗️ Production MVP · 🚀 Long-Term Platform

## Node labels

`Program`, `Table`, `FunctionModule`, `BAdI`, `Job`, `Transport`, `User`.

## Core properties on every node

| Property | Type | Notes |
|---|---|---|
| `name` | string | e.g. `Z_PRICE_ENGINE` — unique per label, enforced by a Neo4j uniqueness constraint |
| `description` | string | Business-friendly text |
| `business_meaning` | string | Why this exists, in plain language |
| `source` | enum | `excel_import` \| `inferred` \| `sap_rfc` (🚀 future) |
| `confidence` | enum | `direct` \| `inferred` — **binary for the demo/early MVP** (see note below) |
| `last_updated` | datetime | |
| `visibility` | enum | Unused placeholder for future RBAC — 🚀, present in schema now so adding real RBAC later isn't a migration |

## Relationship types

`READS`, `WRITES`, `CALLS`, `IMPLEMENTS`, `EXECUTES`, `CHANGED`, `CREATED`.

Each relationship carries: `source`, `confidence`, `derived_from` (which Excel row / future ABAP statement produced it), and `last_updated` — the same provenance model as nodes, so any edge in the graph can answer "how do we know this?"

## Confidence model

- **`direct`** — an explicit row in the source Excel sheet states this relationship.
- **`inferred`** — derived or transitive (e.g., implied by a chain of direct relationships, or a pattern-matched but not explicitly stated dependency).

This was originally scoped as a three-tier High/Medium/Low model. It's intentionally simplified to two tiers for the demo and early MVP — the trust narrative ("we tell you what we don't know") survives fully on a binary distinction, at a fraction of the inference-engine and UI complexity. Because `confidence` is stored as a string enum rather than a boolean, reintroducing a third tier later is a data-layer-compatible change, not a migration.

## Example: Excel → Graph

`Programs.xlsx`:

| Program | Reads | Writes | Calls |
|---|---|---|---|
| Z_PRICE_ENGINE | ZTABLE_PRICING | ZTABLE_PRICE_LOG | Z_FM_VALIDATE_PRICE |

The importer automatically creates:
- `(Z_PRICE_ENGINE:Program)-[:READS {source: 'excel_import', confidence: 'direct'}]->(ZTABLE_PRICING:Table)`
- `(Z_PRICE_ENGINE:Program)-[:WRITES {source: 'excel_import', confidence: 'direct'}]->(ZTABLE_PRICE_LOG:Table)`
- `(Z_PRICE_ENGINE:Program)-[:CALLS {source: 'excel_import', confidence: 'direct'}]->(Z_FM_VALIDATE_PRICE:FunctionModule)`

Any relationship not explicitly present as a row but derivable by traversal (e.g., transitive impact through a chain of `CALLS`) is written with `confidence: 'inferred'`.

## Constraints

Uniqueness constraint on `name` per node label — a duplicate-name write is rejected, not silently overwritten, which is what makes re-running an import idempotent and safe.

## What's explicitly out of scope for now

- `visibility` is present but unenforced — no query filters on it, no RBAC logic anywhere yet. 🚀
- No relationship weighting/frequency data (e.g., "how often is this called") — the demo dataset doesn't need it; if added later it would live as an additional relationship property, not a schema restructure.
