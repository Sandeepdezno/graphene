import { useEffect, useRef, useState } from "react";
import { api } from "../../shared/api-client";
import type { components } from "../../shared/api-client";

type SearchResultItem = components["schemas"]["SearchResultItem"];

const LABEL_CHIP: Record<string, string> = {
  Program: "bg-node-program",
  Table: "bg-node-table",
  FunctionModule: "bg-node-function-module",
  BAdI: "bg-node-badi",
  Job: "bg-node-job",
  Transport: "bg-node-transport",
};

type SearchOverlayProps = {
  onSelect: (id: string) => void;
};

export function SearchOverlay({ onSelect }: SearchOverlayProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Cmd+K / Ctrl+K opens the overlay.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
    } else {
      setQuery("");
      setResults([]);
      setActive(0);
    }
  }, [open]);

  // Type-ahead with a 150ms debounce.
  useEffect(() => {
    if (!open) return;
    const q = query.trim();
    if (!q) {
      setResults([]);
      setActive(0);
      return;
    }
    const timer = setTimeout(async () => {
      const { data } = await api.GET("/api/v1/search", { params: { query: { q } } });
      if (data) {
        setResults(data.results);
        setActive(0);
      }
    }, 150);
    return () => clearTimeout(timer);
  }, [query, open]);

  function choose(item: SearchResultItem): void {
    onSelect(item.id);
    setOpen(false);
  }

  function onInputKey(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (e.key === "Escape") {
      e.stopPropagation();
      setOpen(false);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const item = results[active];
      if (item) choose(item);
    }
  }

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      style={{ backgroundColor: "color-mix(in srgb, var(--bg-canvas) 65%, transparent)" }}
      onMouseDown={() => setOpen(false)}
    >
      <div
        className="w-full max-w-lg overflow-hidden rounded-xl border border-hairline bg-surface shadow-2xl"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onInputKey}
          placeholder="Search nodes by name…"
          className="w-full bg-transparent px-4 py-3.5 text-sm text-ink outline-none placeholder:text-muted"
        />

        {results.length > 0 && (
          <ul className="max-h-80 overflow-y-auto border-t border-hairline p-1">
            {results.map((item, i) => (
              <li key={item.id}>
                <button
                  type="button"
                  onMouseEnter={() => setActive(i)}
                  onClick={() => choose(item)}
                  className={[
                    "flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-left text-sm transition-colors",
                    i === active ? "bg-surface-raised" : "",
                  ].join(" ")}
                >
                  <span className={`h-2 w-2 shrink-0 rounded-full ${LABEL_CHIP[item.label] ?? "bg-accent"}`} />
                  <span className="min-w-0 flex-1 truncate text-ink">{item.name}</span>
                  <span
                    className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold text-canvas ${
                      LABEL_CHIP[item.label] ?? "bg-accent"
                    }`}
                  >
                    {item.label}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {query.trim() && results.length === 0 && (
          <div className="border-t border-hairline px-4 py-3 text-sm text-muted">No matches</div>
        )}
      </div>
    </div>
  );
}
