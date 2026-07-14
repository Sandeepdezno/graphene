import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../../shared/api-client";
import { GraphEngine } from "../../shared/graph-engine";
import type {
  GraphEdgeInput,
  GraphEngineHandle,
  GraphNodeInput,
} from "../../shared/graph-engine";
import { Legend } from "./Legend";
import { NodeDrawer } from "./NodeDrawer";
import { ConfidenceToggle } from "./ConfidenceToggle";
import { SearchOverlay } from "../search/SearchOverlay";

const FADE_MS = 300;

const FLAGSHIP_NODE_ID = "Z_PRICE_ENGINE";

type LoadState = "loading" | "empty" | "error" | "ready";

export function GraphExplorerPage() {
  const [state, setState] = useState<LoadState>("loading");
  const [nodes, setNodes] = useState<GraphNodeInput[]>([]);
  const [edges, setEdges] = useState<GraphEdgeInput[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showInferred, setShowInferred] = useState(true);
  const [inferredOpacity, setInferredOpacity] = useState(1);
  const engineRef = useRef<GraphEngineHandle>(null);
  const highlightNodeIds = useMemo(
    () => (selectedId ? new Set([selectedId]) : undefined),
    [selectedId],
  );

  // Fade inferred edges in/out over ~300ms (opacity only — no relayout).
  useEffect(() => {
    const to = showInferred ? 1 : 0;
    const from = inferredOpacity;
    if (from === to) return;
    const start = performance.now();
    let raf = 0;
    const tick = () => {
      const t = Math.min(1, (performance.now() - start) / FADE_MS);
      setInferredOpacity(from + (to - from) * t);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // Intentionally keyed only on the toggle; `from` captures the current value.
  }, [showInferred]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    let cancelled = false;
    async function load(): Promise<void> {
      const { data, error } = await api.GET("/api/v1/graph", {
        params: { query: { limit: 1000 } },
      });
      if (cancelled) return;
      if (error || !data) {
        setState("error");
        return;
      }
      if (data.nodes.length === 0) {
        setState("empty");
        return;
      }
      setNodes(data.nodes.map((n) => ({ id: n.id, name: n.name, label: n.label })));
      setEdges(
        data.relationships.map((r) => ({
          id: r.id,
          source: r.source_id,
          target: r.target_id,
          type: r.type,
          confidence: r.confidence,
        })),
      );
      setState("ready");
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state !== "ready") {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-sm tracking-wide text-muted">
          {state === "loading"
            ? "Loading graph…"
            : state === "empty"
              ? "No graph loaded"
              : "Graph unavailable"}
        </p>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <GraphEngine
        ref={engineRef}
        nodes={nodes}
        edges={edges}
        focusRegionNodeId={FLAGSHIP_NODE_ID}
        highlightNodeIds={highlightNodeIds}
        inferredEdgeOpacity={inferredOpacity}
        onNodeClick={(id) => setSelectedId(id)}
        onBackgroundClick={() => setSelectedId(null)}
      />
      <ConfidenceToggle
        checked={showInferred}
        onChange={setShowInferred}
        drawerOpen={selectedId != null}
      />
      <Legend />
      <NodeDrawer
        nodeId={selectedId}
        onClose={() => setSelectedId(null)}
        onNavigate={(id) => {
          void engineRef.current?.flyToNode(id);
          setSelectedId(id);
        }}
      />
      <SearchOverlay
        onSelect={(id) => {
          void engineRef.current?.flyToNode(id);
          setSelectedId(id);
        }}
      />
    </div>
  );
}
