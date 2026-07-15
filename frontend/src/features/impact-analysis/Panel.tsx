import { useEffect, useState } from "react";
import { api } from "../../shared/api-client";
import type { components } from "../../shared/api-client";

type ImpactResponse = components["schemas"]["ImpactResponse"];

// Tier thresholds (named constants): <40 low, 40–70 medium, >70 high.
const LOW_THRESHOLD = 40;
const HIGH_THRESHOLD = 70;
const GAUGE_SWEEP_MS = 900;

const LABEL_DOT: Record<string, string> = {
  Program: "bg-node-program",
  Table: "bg-node-table",
  FunctionModule: "bg-node-function-module",
  BAdI: "bg-node-badi",
  Job: "bg-node-job",
  Transport: "bg-node-transport",
};

type Tier = "low" | "medium" | "high";

function riskTier(score: number): Tier {
  if (score < LOW_THRESHOLD) return "low";
  if (score > HIGH_THRESHOLD) return "high";
  return "medium";
}

const TIER_STROKE: Record<Tier, string> = {
  low: "var(--risk-low)",
  medium: "var(--risk-medium)",
  high: "var(--risk-high)",
};
const TIER_TEXT: Record<Tier, string> = {
  low: "text-risk-low",
  medium: "text-risk-medium",
  high: "text-risk-high",
};

function RiskGauge({ score }: { score: number }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    setProgress(0);
    const start = performance.now();
    const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
    let raf = 0;
    const tick = () => {
      const t = Math.min(1, (performance.now() - start) / GAUGE_SWEEP_MS);
      setProgress(easeOutCubic(t));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const radius = 80;
  const arcLength = Math.PI * radius;
  const offset = arcLength * (1 - (score / 100) * progress);
  const value = Math.round(score * progress);
  const tier = riskTier(score);

  return (
    <div className="relative mx-auto w-full max-w-[240px]">
      <svg viewBox="0 0 200 108" className="w-full">
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          fill="none"
          strokeWidth="12"
          strokeLinecap="round"
          style={{ stroke: "var(--border)" }}
        />
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          fill="none"
          strokeWidth="12"
          strokeLinecap="round"
          style={{ stroke: TIER_STROKE[tier] }}
          strokeDasharray={arcLength}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
        <span className={`text-6xl font-bold leading-none tabular-nums ${TIER_TEXT[tier]}`}>
          {value}
        </span>
        <span className="mt-1 text-[11px] font-medium uppercase tracking-widest text-muted">
          Risk score
        </span>
      </div>
    </div>
  );
}

type ImpactPanelProps = {
  nodeId: string;
  onBack: () => void;
};

export function ImpactPanel({ nodeId, onBack }: ImpactPanelProps) {
  const [impact, setImpact] = useState<ImpactResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load(): Promise<void> {
      const { data } = await api.GET("/api/v1/impact/{node_id}", {
        params: { path: { node_id: nodeId } },
      });
      if (!cancelled && data) setImpact(data);
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [nodeId]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-hairline p-4">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1 text-sm text-muted transition-colors hover:text-ink"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 6l-6 6 6 6" />
          </svg>
          Back
        </button>
        <span className="min-w-0 flex-1 truncate text-sm font-semibold text-ink">{nodeId}</span>
      </div>

      {impact && (
        <div className="flex-1 overflow-y-auto p-4">
          <div className="pt-3">
            <RiskGauge score={impact.risk_score} />
          </div>

          <p className="mt-5 text-sm leading-relaxed text-ink">{impact.explanation}</p>

          <h3 className="mb-2 mt-6 text-[11px] font-semibold uppercase tracking-wide text-muted">
            Affected objects ({impact.total_affected})
          </h3>
          <div className="space-y-4">
            {impact.affected_groups.map((group) => (
              <div key={group.label}>
                <div className="mb-1.5 flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${LABEL_DOT[group.label] ?? "bg-accent"}`} />
                  <span className="text-xs font-semibold text-ink">{group.label}</span>
                  <span className="rounded-full bg-surface-raised px-1.5 py-0.5 text-[10px] font-medium text-muted">
                    {group.count}
                  </span>
                </div>
                <ul className="space-y-0.5">
                  {group.items.map((item) => (
                    <li key={item.id} className="flex items-center gap-2 px-2 py-1 text-sm text-ink">
                      <span className="min-w-0 flex-1 truncate">{item.name}</span>
                      <span className="shrink-0 rounded bg-surface-raised px-1.5 py-0.5 text-[10px] text-muted">
                        hop {item.hop_distance}
                      </span>
                      <span
                        title={item.confidence}
                        className={`w-4 shrink-0 border-t ${
                          item.confidence === "inferred"
                            ? "border-dashed border-confidence-inferred"
                            : "border-confidence-direct"
                        }`}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
