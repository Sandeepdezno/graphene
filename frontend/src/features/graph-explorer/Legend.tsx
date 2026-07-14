import { useState } from "react";

const NODE_TYPES = [
  { label: "Program", dot: "bg-node-program" },
  { label: "Table", dot: "bg-node-table" },
  { label: "Function Module", dot: "bg-node-function-module" },
  { label: "BAdI", dot: "bg-node-badi" },
  { label: "Job", dot: "bg-node-job" },
  { label: "Transport", dot: "bg-node-transport" },
] as const;

export function Legend() {
  const [open, setOpen] = useState(true);

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="absolute bottom-4 left-4 rounded-lg border border-hairline bg-surface px-3 py-1.5 text-xs font-medium text-muted transition-colors hover:text-ink"
      >
        Legend
      </button>
    );
  }

  return (
    <div className="absolute bottom-4 left-4 w-48 rounded-xl border border-hairline bg-surface p-3 text-xs">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-semibold text-ink">Legend</span>
        <button
          type="button"
          onClick={() => setOpen(false)}
          aria-label="Close legend"
          className="text-muted transition-colors hover:text-ink"
        >
          ×
        </button>
      </div>

      <ul className="space-y-1.5">
        {NODE_TYPES.map((t) => (
          <li key={t.label} className="flex items-center gap-2 text-muted">
            <span className={`h-2.5 w-2.5 rounded-full ${t.dot}`} />
            {t.label}
          </li>
        ))}
      </ul>

      <div className="mt-3 space-y-1.5 border-t border-hairline pt-2">
        <div className="flex items-center gap-2 text-muted">
          <span className="w-6 border-t border-confidence-direct" />
          direct
        </div>
        <div className="flex items-center gap-2 text-muted">
          <span className="w-6 border-t border-dashed border-confidence-inferred" />
          inferred
        </div>
      </div>
    </div>
  );
}
