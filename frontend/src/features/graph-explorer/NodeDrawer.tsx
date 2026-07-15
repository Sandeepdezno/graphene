import { useEffect, useState } from "react";
import { api } from "../../shared/api-client";
import type { components } from "../../shared/api-client";
import { ImpactPanel } from "../impact-analysis/Panel";
import type { ImpactData } from "../impact-analysis/Panel";

type NodeDetail = components["schemas"]["NodeDetailResponse"];
type Neighbor = components["schemas"]["NodeNeighbor"];

// Verbatim from docs/04-demo-bible.md — the designed empty-state beat.
const EMPTY_STATE_COPY =
  "No dependencies recorded for this node — this is exactly the kind of undocumented logic Graphene is built to surface once connected to live SAP.";

const LABEL_DOT: Record<string, string> = {
  Program: "bg-node-program",
  Table: "bg-node-table",
  FunctionModule: "bg-node-function-module",
  BAdI: "bg-node-badi",
  Job: "bg-node-job",
  Transport: "bg-node-transport",
};

const TYPE_ORDER = ["CALLS", "READS", "WRITES", "IMPLEMENTS", "EXECUTES", "CHANGED", "CREATED"];

function groupByType(neighbors: Neighbor[]): [string, Neighbor[]][] {
  const map = new Map<string, Neighbor[]>();
  for (const n of neighbors) {
    const arr = map.get(n.relationship_type) ?? [];
    arr.push(n);
    map.set(n.relationship_type, arr);
  }
  return [...map.entries()].sort(
    (a, b) => TYPE_ORDER.indexOf(a[0]) - TYPE_ORDER.indexOf(b[0]),
  );
}

function DirectionIcon({ direction }: { direction: string }) {
  // out: this node → neighbor; in: neighbor → this node (arrow flipped).
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      className={`h-3.5 w-3.5 shrink-0 text-muted ${direction === "in" ? "rotate-180" : ""}`}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14m-6-6l6 6-6 6" />
    </svg>
  );
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const inferred = confidence === "inferred";
  return (
    <span
      className={[
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium",
        inferred
          ? "border-dashed border-confidence-inferred text-confidence-inferred"
          : "border-confidence-direct text-confidence-direct",
      ].join(" ")}
    >
      {confidence}
    </span>
  );
}

function ConfidenceMarker({ confidence }: { confidence: string }) {
  const inferred = confidence === "inferred";
  return (
    <span
      title={confidence}
      className={`w-4 shrink-0 border-t ${
        inferred ? "border-dashed border-confidence-inferred" : "border-confidence-direct"
      }`}
    />
  );
}

function EmptyState() {
  return (
    <div className="rounded-xl border border-hairline bg-surface-raised p-4">
      <div className="mb-2 flex items-center gap-2 text-muted">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="h-4 w-4">
          <circle cx="12" cy="12" r="9" />
          <path strokeLinecap="round" d="M12 8v4m0 3h.01" />
        </svg>
        <span className="text-[11px] font-semibold uppercase tracking-wide">Empty state</span>
      </div>
      <p className="text-sm leading-relaxed text-muted">{EMPTY_STATE_COPY}</p>
    </div>
  );
}

type NodeDrawerProps = {
  nodeId: string | null;
  impactOpen: boolean;
  impact: ImpactData | null;
  onShowImpact: () => void;
  onHideImpact: () => void;
  onClose: () => void;
  onNavigate: (id: string) => void;
};

export function NodeDrawer({
  nodeId,
  impactOpen,
  impact,
  onShowImpact,
  onHideImpact,
  onClose,
  onNavigate,
}: NodeDrawerProps) {
  const [detail, setDetail] = useState<NodeDetail | null>(null);
  const open = nodeId != null;

  useEffect(() => {
    if (nodeId == null) return;
    let cancelled = false;
    async function load(): Promise<void> {
      const { data } = await api.GET("/api/v1/graph/node/{id}", {
        params: { path: { id: nodeId as string } },
      });
      if (!cancelled && data) setDetail(data);
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [nodeId]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const node = detail?.node;
  const neighbors = detail?.neighbors ?? [];
  const groups = groupByType(neighbors);

  return (
    <aside
      aria-hidden={!open}
      className={[
        "absolute right-0 top-0 z-10 flex h-full w-[400px] flex-col border-l border-hairline bg-surface transition-transform duration-300",
        open ? "translate-x-0" : "translate-x-full",
      ].join(" ")}
    >
      {node && impactOpen ? (
        <ImpactPanel nodeId={node.name} impact={impact} onBack={onHideImpact} />
      ) : node ? (
        <>
          <div className="border-b border-hairline p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="truncate text-base font-semibold text-ink">{node.name}</h2>
                <div className="mt-1.5 flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold text-canvas ${
                      LABEL_DOT[node.label] ?? "bg-accent"
                    }`}
                  >
                    {node.label}
                  </span>
                  <ConfidenceBadge confidence={node.confidence} />
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="shrink-0 text-lg leading-none text-muted transition-colors hover:text-ink"
              >
                ×
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {node.description && <p className="text-sm text-ink">{node.description}</p>}
            {node.business_meaning && (
              <p className="mt-2 text-sm text-muted">{node.business_meaning}</p>
            )}

            {neighbors.length > 0 && (
              <button
                type="button"
                onClick={onShowImpact}
                className="mt-4 w-full rounded-lg bg-accent px-3 py-2.5 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
              >
                What breaks if I modify this?
              </button>
            )}

            <div className="mt-5">
              {neighbors.length === 0 ? (
                <EmptyState />
              ) : (
                <div className="space-y-4">
                  <h3 className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                    Connections ({neighbors.length})
                  </h3>
                  {groups.map(([type, items]) => (
                    <div key={type}>
                      <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-muted">
                        {type}
                      </div>
                      <ul className="space-y-0.5">
                        {items.map((c) => (
                          <li key={`${c.direction}-${c.relationship_type}-${c.name}`}>
                            <button
                              type="button"
                              onClick={() => onNavigate(c.id)}
                              className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm text-ink transition-colors hover:bg-surface-raised"
                            >
                              <DirectionIcon direction={c.direction} />
                              <span
                                className={`h-2 w-2 shrink-0 rounded-full ${
                                  LABEL_DOT[c.label] ?? "bg-accent"
                                }`}
                              />
                              <span className="min-w-0 flex-1 truncate">{c.name}</span>
                              <ConfidenceMarker confidence={c.confidence} />
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      ) : null}
    </aside>
  );
}
