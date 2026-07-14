import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../shared/api-client";
import type { components } from "../../shared/api-client";

type JobStatus = components["schemas"]["JobStatusResponse"];

const STAGE_ORDER = ["parsing", "inferring", "writing", "complete"] as const;

type ProcessingProps = {
  jobId: string;
  onRetry: () => void;
};

type RowState = "done" | "active" | "pending";

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" className="h-4 w-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

export function Processing({ jobId, onRetry }: ProcessingProps) {
  const navigate = useNavigate();
  const [status, setStatus] = useState<JobStatus | null>(null);

  // Poll the status endpoint every 300ms until the job settles.
  useEffect(() => {
    let active = true;
    const timer = setInterval(async () => {
      const { data } = await api.GET("/api/v1/import/{job_id}/status", {
        params: { path: { job_id: jobId } },
      });
      if (!active || !data) return;
      setStatus(data);
      if (data.status === "complete" || data.status === "failed") {
        clearInterval(timer);
      }
    }, 300);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [jobId]);

  // On complete: brief pause so the final count registers, then to the explorer.
  useEffect(() => {
    if (status?.status !== "complete") return;
    const t = setTimeout(() => navigate("/explorer"), 800);
    return () => clearTimeout(t);
  }, [status?.status, navigate]);

  if (status?.status === "failed") {
    return (
      <div className="flex h-full w-full items-center justify-center p-8">
        <div className="w-full max-w-md rounded-2xl border border-hairline bg-surface p-8 text-center">
          <p className="text-base font-medium text-risk-high">Import failed</p>
          <p className="mt-2 text-sm text-muted">{status.error ?? "Something went wrong."}</p>
          <button
            type="button"
            onClick={onRetry}
            className="mt-6 rounded-lg border border-hairline bg-surface-raised px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  const stage = status?.status ?? "parsing";
  const activeIndex = STAGE_ORDER.indexOf(stage as (typeof STAGE_ORDER)[number]);
  const hasCounts = status?.node_count != null && status?.edge_count != null;

  const rows = [
    { label: "Parsing sheets" },
    { label: "Resolving relationships" },
    { label: "Building graph" },
    {
      label: hasCounts
        ? `${status?.node_count} nodes, ${status?.edge_count} edges`
        : "Finalizing graph",
    },
  ];

  function rowState(i: number): RowState {
    if (stage === "complete") return "done";
    if (i < activeIndex) return "done";
    if (i === activeIndex) return "active";
    return "pending";
  }

  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      <div className="w-full max-w-md rounded-2xl border border-hairline bg-surface p-8">
        <h2 className="mb-6 text-base font-semibold text-ink">Building your graph</h2>
        <ul className="space-y-4">
          {rows.map((row, i) => {
            const state = rowState(i);
            return (
              <li key={i} className="flex items-center gap-3">
                <span
                  className={[
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border",
                    state === "done"
                      ? "border-risk-low bg-risk-low text-canvas"
                      : state === "active"
                        ? "border-accent bg-accent text-canvas animate-pulse"
                        : "border-hairline text-transparent",
                  ].join(" ")}
                >
                  {state === "done" ? (
                    <CheckIcon />
                  ) : (
                    <span className="h-1.5 w-1.5 rounded-full bg-current" />
                  )}
                </span>
                <span
                  className={[
                    "text-sm",
                    state === "done"
                      ? "text-ink"
                      : state === "active"
                        ? "font-medium text-accent animate-pulse"
                        : "text-muted",
                    i === 3 && state === "done" ? "font-semibold text-ink" : "",
                  ].join(" ")}
                >
                  {row.label}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
