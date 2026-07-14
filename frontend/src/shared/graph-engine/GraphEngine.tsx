import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
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

export type GraphEngineHandle = {
  /** Center + zoom to a node within ~600ms. Resolves with the measured ms. */
  flyToNode: (id: string) => Promise<number>;
  /** Frame the whole graph. */
  zoomToFit: (durationMs?: number) => void;
};

export type GraphEngineProps = {
  nodes: GraphNodeInput[];
  edges: GraphEdgeInput[];
  /** Hard cap on rendered nodes. Present per CLAUDE.md even though the demo graph
   *  is well under it; excess nodes (and their edges) are dropped. */
  maxNodes?: number;
  onNodeClick?: (id: string) => void;
  /** Fired when the empty canvas (not a node) is clicked. */
  onBackgroundClick?: () => void;
  /** Controlled highlight: these nodes get an accent ring and stay bright. */
  highlightNodeIds?: ReadonlySet<string>;
  /** When true, nodes not in `highlightNodeIds` render at 15% opacity. */
  dim?: boolean;
  /** Edge visibility filter (e.g. hide inferred edges). */
  isEdgeVisible?: (edge: GraphEdgeInput) => boolean;
  /** Opacity multiplier for inferred edges (1 = shown, 0 = faded out). Animate
   *  this to fade inferred edges without changing the layout. */
  inferredEdgeOpacity?: number;
  /** After settle, the camera eases toward this node's region (demo 1:00-1:15). */
  focusRegionNodeId?: string;
  /** Called once when the force layout settles, with the measured settle ms. */
  onSettle?: (ms: number) => void;
};

const DEFAULT_MAX_NODES = 1000;
const SETTLE_MS = 2000; // cooldownTime cap -> layout freezes at ~2.0s
const FLY_MS = 600;
const FLY_ZOOM = 6;
const REGION_ZOOM = 2.5;

export const GraphEngine = forwardRef<GraphEngineHandle, GraphEngineProps>(
  function GraphEngine(
    {
      nodes,
      edges,
      maxNodes = DEFAULT_MAX_NODES,
      onNodeClick,
      onBackgroundClick,
      highlightNodeIds,
      dim = false,
      isEdgeVisible,
      inferredEdgeOpacity = 1,
      focusRegionNodeId,
      onSettle,
    },
    ref,
  ) {
    const containerRef = useRef<HTMLDivElement | null>(null);
    const fgRef = useRef<any>(null);
    const [size, setSize] = useState({ width: 0, height: 0 });
    const colors = useMemo(() => readGraphColors(), []);

    const settleStart = useRef(0);
    const settled = useRef(false);

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
    // repaint without reheating the layout). Radius scales modestly by degree.
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

    // Mark the layout start when data first arrives.
    useEffect(() => {
      if (graphData.nodes.length > 0 && settleStart.current === 0) {
        settleStart.current = performance.now();
        settled.current = false;
      }
    }, [graphData]);

    function flyToNode(id: string): Promise<number> {
      const fg = fgRef.current;
      const node = graphData.nodes.find((n) => n.id === id) as
        | { x?: number; y?: number }
        | undefined;
      if (!fg || !node || node.x == null || node.y == null) return Promise.resolve(-1);

      const start = performance.now();
      performance.mark("flyToNode:start");
      fg.centerAt(node.x, node.y, FLY_MS);
      fg.zoom(FLY_ZOOM, FLY_MS);
      return new Promise((resolve) => {
        const poll = () => {
          const elapsed = performance.now() - start;
          if (Math.abs(fg.zoom() - FLY_ZOOM) < 0.05 || elapsed > 1200) {
            performance.mark("flyToNode:end");
            performance.measure("flyToNode", "flyToNode:start", "flyToNode:end");
            resolve(Math.round(elapsed));
          } else {
            requestAnimationFrame(poll);
          }
        };
        requestAnimationFrame(poll);
      });
    }

    useImperativeHandle(
      ref,
      () => ({
        flyToNode,
        zoomToFit: (durationMs = 600) => fgRef.current?.zoomToFit(durationMs, 40),
      }),
      [graphData],
    );

    function handleEngineStop() {
      if (settled.current) return; // only the initial settle
      settled.current = true;
      const ms = Math.round(performance.now() - settleStart.current);
      performance.measure?.("graph-settle");
      onSettle?.(ms);

      const fg = fgRef.current;
      if (!fg) return;
      // Frame the whole graph, then ease toward the flagship cluster's region.
      fg.zoomToFit(600, 40);
      const node = focusRegionNodeId
        ? (graphData.nodes.find((n) => n.id === focusRegionNodeId) as
            | { x?: number; y?: number }
            | undefined)
        : undefined;
      if (node && node.x != null && node.y != null) {
        window.setTimeout(() => {
          fg.centerAt(node.x, node.y, 900);
          fg.zoom(REGION_ZOOM, 900);
        }, 800);
      }
    }

    return (
      <div ref={containerRef} className="h-full w-full">
        {size.width > 0 && (
          <ForceGraph2D
            ref={fgRef}
            width={size.width}
            height={size.height}
            graphData={graphData}
            backgroundColor="rgba(0,0,0,0)"
            cooldownTime={SETTLE_MS}
            onEngineStop={handleEngineStop}
            onNodeClick={(node) => onNodeClick?.((node as { id: string }).id)}
            onBackgroundClick={() => onBackgroundClick?.()}
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
              const alpha = inferred ? 0.65 * inferredEdgeOpacity : 0.4;
              if (alpha <= 0.001) return; // fully faded — skip draw (positions unchanged)
              ctx.strokeStyle = inferred ? colors.inferred : colors.direct;
              ctx.globalAlpha = alpha;
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
  },
);
