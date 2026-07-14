import { useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { readGraphColors } from "./colors";

export type GraphNodeInput = { id: string; name: string; label: string };
export type GraphEdgeInput = {
  id: string;
  source: string;
  target: string;
  type: string;
  confidence: string;
};

export type GraphEngineProps = {
  nodes: GraphNodeInput[];
  edges: GraphEdgeInput[];
  /** Hard cap on rendered nodes. Present per CLAUDE.md even though the demo graph
   *  is well under it; excess nodes (and their edges) are dropped. */
  maxNodes?: number;
  onNodeClick?: (id: string) => void;
  /** Controlled highlight: these nodes get an accent ring and stay bright. */
  highlightNodeIds?: ReadonlySet<string>;
  /** When true, nodes not in `highlightNodeIds` render at 15% opacity. */
  dim?: boolean;
  /** Edge visibility filter (e.g. hide inferred edges). */
  isEdgeVisible?: (edge: GraphEdgeInput) => boolean;
};

const DEFAULT_MAX_NODES = 1000;
const SETTLE_MS = 2000;

export function GraphEngine({
  nodes,
  edges,
  maxNodes = DEFAULT_MAX_NODES,
  onNodeClick,
  highlightNodeIds,
  dim = false,
  isEdgeVisible,
}: GraphEngineProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const colors = useMemo(() => readGraphColors(), []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const measure = () => setSize({ width: el.clientWidth, height: el.clientHeight });
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Built once per input (stable across highlight/dim/filter changes, so those
  // repaint without reheating the force layout). Radius scales modestly by degree.
  const graphData = useMemo(() => {
    const capped = nodes.slice(0, maxNodes);
    const ids = new Set(capped.map((n) => n.id));
    const links = edges.filter((e) => ids.has(e.source) && ids.has(e.target));

    const degree: Record<string, number> = {};
    for (const e of links) {
      degree[e.source] = (degree[e.source] ?? 0) + 1;
      degree[e.target] = (degree[e.target] ?? 0) + 1;
    }
    return {
      nodes: capped.map((n) => ({ ...n, __r: 2.5 + Math.sqrt(degree[n.id] ?? 0) * 1.1 })),
      links: links.map((e) => ({ ...e })),
    };
  }, [nodes, edges, maxNodes]);

  return (
    <div ref={containerRef} className="h-full w-full">
      {size.width > 0 && (
        <ForceGraph2D
          width={size.width}
          height={size.height}
          graphData={graphData}
          backgroundColor="rgba(0,0,0,0)"
          cooldownTime={SETTLE_MS}
          onNodeClick={(node) => onNodeClick?.((node as { id: string }).id)}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n = node as { id: string; name: string; label: string; __r: number; x: number; y: number };
            const highlighted = highlightNodeIds?.has(n.id) ?? false;
            const dimmed = dim && !highlighted;
            const r = n.__r;

            ctx.globalAlpha = dimmed ? 0.15 : 1;
            ctx.beginPath();
            ctx.arc(n.x, n.y, r, 0, 2 * Math.PI);
            ctx.fillStyle = colors.nodeByLabel[n.label] ?? colors.accent;
            ctx.fill();

            if (highlighted) {
              ctx.globalAlpha = 1;
              ctx.lineWidth = 1.6;
              ctx.strokeStyle = colors.accent;
              ctx.beginPath();
              ctx.arc(n.x, n.y, r + 3, 0, 2 * Math.PI);
              ctx.stroke();
            }

            // Labels only at readable zoom, to avoid clutter when zoomed out.
            if (globalScale > 1.3) {
              ctx.globalAlpha = dimmed ? 0.15 : 0.85;
              ctx.font = `${11 / globalScale}px Inter, sans-serif`;
              ctx.textAlign = "center";
              ctx.textBaseline = "top";
              ctx.fillStyle = colors.text;
              ctx.fillText(n.name, n.x, n.y + r + 1.5);
            }
            ctx.globalAlpha = 1;
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            const n = node as { __r: number; x: number; y: number };
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.__r + 2, 0, 2 * Math.PI);
            ctx.fill();
          }}
          linkCanvasObjectMode={() => "replace"}
          linkCanvasObject={(link, ctx) => {
            const l = link as unknown as GraphEdgeInput & {
              source: { x: number; y: number };
              target: { x: number; y: number };
            };
            if (isEdgeVisible && !isEdgeVisible(l)) return;

            const inferred = l.confidence === "inferred";
            ctx.strokeStyle = inferred ? colors.inferred : colors.direct;
            ctx.globalAlpha = inferred ? 0.65 : 0.4;
            ctx.lineWidth = 0.6;
            ctx.setLineDash(inferred ? [2, 2] : []);
            ctx.beginPath();
            ctx.moveTo(l.source.x, l.source.y);
            ctx.lineTo(l.target.x, l.target.y);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.globalAlpha = 1;
          }}
        />
      )}
    </div>
  );
}
