// The graph canvas is intentionally empty at GRAPH-D0.4 — rendering arrives in
// Sprint 2 (GRAPH-D2.2). This establishes the dark canvas surface only.
export function GraphExplorerPage() {
  return (
    <div className="flex h-full w-full items-center justify-center">
      <p className="text-sm tracking-wide text-muted">No graph loaded</p>
    </div>
  );
}
