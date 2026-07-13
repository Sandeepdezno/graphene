import { useEffect, useRef, useState } from "react";
import { api } from "../../shared/api-client";
import type { components } from "../../shared/api-client";

type GraphData = components["schemas"]["GraphResponse"];
type LoadState = "loading" | "empty" | "error" | "ready";

// Deliberately unstyled (GRAPH-D0.5): plain circles + lines on a raw canvas,
// no rendering library. Real physics/styling arrive in Sprint 2.
function draw(canvas: HTMLCanvasElement, data: GraphData): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Colors come from design tokens — no hardcoded hex in components.
  const css = getComputedStyle(document.documentElement);
  const nodeColor = css.getPropertyValue("--accent").trim();
  const edgeColor = css.getPropertyValue("--confidence-direct").trim();
  const textColor = css.getPropertyValue("--text-primary").trim();

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const radius = Math.min(canvas.width, canvas.height) * 0.32;

  const positions = new Map<string, { x: number; y: number }>();
  data.nodes.forEach((node, i) => {
    const angle = (i / data.nodes.length) * Math.PI * 2 - Math.PI / 2;
    positions.set(node.id, {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    });
  });

  // Edges first, so nodes sit on top.
  ctx.strokeStyle = edgeColor;
  ctx.lineWidth = 1.5;
  data.relationships.forEach((rel) => {
    const from = positions.get(rel.source_id);
    const to = positions.get(rel.target_id);
    if (!from || !to) return;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
  });

  // Nodes + labels.
  ctx.font = "12px Inter, sans-serif";
  ctx.textAlign = "center";
  data.nodes.forEach((node) => {
    const pos = positions.get(node.id);
    if (!pos) return;
    ctx.fillStyle = nodeColor;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = textColor;
    ctx.fillText(node.name, pos.x, pos.y - 14);
  });
}

export function GraphExplorerPage() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [state, setState] = useState<LoadState>("loading");

  useEffect(() => {
    let cancelled = false;
    async function load(): Promise<void> {
      const { data, error } = await api.GET("/api/v1/graph", {
        params: { query: { limit: 500 } },
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
      const canvas = canvasRef.current;
      if (canvas) draw(canvas, data);
      setState("ready");
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="relative h-full w-full">
      <canvas ref={canvasRef} className="block h-full w-full" />
      {state !== "ready" && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <p className="text-sm tracking-wide text-muted">
            {state === "loading"
              ? "Loading graph…"
              : state === "empty"
                ? "No graph loaded"
                : "Graph unavailable"}
          </p>
        </div>
      )}
    </div>
  );
}
