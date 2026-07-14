import { useEffect, useRef, useState } from "react";
import { api } from "../../shared/api-client";
import { GraphEngine } from "../../shared/graph-engine";
import type {
  GraphEdgeInput,
  GraphEngineHandle,
  GraphNodeInput,
} from "../../shared/graph-engine";
import { Legend } from "./Legend";

const FLAGSHIP_NODE_ID = "Z_PRICE_ENGINE";

type LoadState = "loading" | "empty" | "error" | "ready";

export function GraphExplorerPage() {
  const [state, setState] = useState<LoadState>("loading");
  const [nodes, setNodes] = useState<GraphNodeInput[]>([]);
  const [edges, setEdges] = useState<GraphEdgeInput[]>([]);
  const engineRef = useRef<GraphEngineHandle>(null);

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
        onNodeClick={(id) => console.debug("node clicked:", id)}
      />
      <Legend />
    </div>
  );
}
