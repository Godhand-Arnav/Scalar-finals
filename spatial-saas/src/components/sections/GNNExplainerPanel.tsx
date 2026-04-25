"use client";
import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useForgeStore } from "@/store/forgeStore";

const PRIMITIVE_COLORS: Record<string, string> = {
  SOURCE_LAUNDER:    "#22d3ee",
  QUOTE_FABRICATE:   "#a78bfa",
  TEMPORAL_SHIFT:    "#f59e0b",
  ENTITY_SUBSTITUTE: "#34d399",
  NETWORK_AMPLIFY:   "#f87171",
  CITATION_FORGE:    "#60a5fa",
  CONTEXT_STRIP:     "#fb923c",
  SATIRE_REFRAME:    "#e879f9",
};

export default function GNNExplainerPanel() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { gnnNodeImportance, predictedChain } = useForgeStore();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const nodeEntries = Object.entries(gnnNodeImportance ?? {});
    if (nodeEntries.length === 0) {
      // Draw placeholder
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = canvas.offsetWidth * dpr;
      canvas.height = canvas.offsetHeight * dpr;
      ctx.scale(dpr, dpr);
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(100,116,139,0.25)";
      ctx.font = "12px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("Run an investigation or activate Demo Mode", w / 2, h / 2);
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    ctx.scale(dpr, dpr);
    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;

    ctx.clearRect(0, 0, w, h);

    // Arrange nodes in a circle around center
    const cx = w / 2;
    const cy = h / 2;
    const radius = Math.min(w, h) * 0.35;

    const positions: Record<string, [number, number]> = {};
    nodeEntries.forEach(([id], i) => {
      const angle = (i / nodeEntries.length) * Math.PI * 2 - Math.PI / 2;
      positions[id] = [
        cx + radius * Math.cos(angle),
        cy + radius * Math.sin(angle),
      ];
    });

    // Draw edges root → each node
    nodeEntries.forEach(([id]) => {
      const [x, y] = positions[id];
      const imp = gnnNodeImportance[id];
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.strokeStyle = `rgba(34,211,238,${imp * 0.35})`;
      ctx.lineWidth = imp * 2.5;
      ctx.stroke();
    });

    // Draw root CLAIM node
    const rootGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 22);
    rootGrad.addColorStop(0, "rgba(124,58,237,0.85)");
    rootGrad.addColorStop(1, "rgba(124,58,237,0.08)");
    ctx.beginPath();
    ctx.arc(cx, cy, 20, 0, Math.PI * 2);
    ctx.fillStyle = rootGrad;
    ctx.fill();
    ctx.strokeStyle = "rgba(167,139,250,0.9)";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "#fff";
    ctx.font = `bold 9px Inter, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("CLAIM", cx, cy);

    // Draw evidence nodes
    nodeEntries.forEach(([id]) => {
      const imp = gnnNodeImportance[id];
      const [x, y] = positions[id];
      const nodeR = 6 + imp * 14;
      const color = imp > 0.7 ? "#f87171" : imp > 0.45 ? "#f59e0b" : "#64748b";

      // Glow halo
      const glow = ctx.createRadialGradient(x, y, 0, x, y, nodeR * 2.2);
      glow.addColorStop(0, color + "55");
      glow.addColorStop(1, "transparent");
      ctx.beginPath();
      ctx.arc(x, y, nodeR * 2.2, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // Node fill
      ctx.beginPath();
      ctx.arc(x, y, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = color + "cc";
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Importance % label inside node
      ctx.fillStyle = "rgba(248,250,252,0.95)";
      ctx.font = `bold 8.5px Inter, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(`${(imp * 100).toFixed(0)}%`, x, y);

      // Node name label below
      const shortId = id.length > 15 ? id.slice(0, 13) + "…" : id;
      ctx.fillStyle = "rgba(148,163,184,0.85)";
      ctx.font = `8px Inter, sans-serif`;
      ctx.fillText(shortId, x, y + nodeR + 11);
    });
  }, [gnnNodeImportance]);

  const hasData = gnnNodeImportance && Object.keys(gnnNodeImportance).length > 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full rounded-2xl bg-slate-900/60 border border-white/[0.07] backdrop-blur-xl p-4 flex flex-col shadow-[0_0_40px_rgba(0,0,0,0.3)]"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <span className="text-xs font-bold text-slate-200 tracking-widest">GNN EXPLAINER</span>
        <span className="text-xs text-slate-500">node influence on chain prediction</span>
        <div className="ml-auto flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
            <span className="text-slate-500">high</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
            <span className="text-slate-500">medium</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-slate-500 inline-block" />
            <span className="text-slate-500">low</span>
          </span>
        </div>
      </div>

      {/* Canvas */}
      <div className="relative flex-1" style={{ minHeight: 200 }}>
        <canvas
          ref={canvasRef}
          className="w-full h-full rounded-lg"
          style={{ minHeight: 200 }}
        />
        {!hasData && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="text-[10px] text-slate-600 italic">
              Activate Demo Mode or submit a live claim to see the evidence graph
            </p>
          </div>
        )}
      </div>

      {/* Predicted chain chips */}
      {predictedChain && predictedChain.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-white/[0.06]">
          <span className="text-[9px] font-bold text-slate-500 tracking-widest self-center mr-1">
            PREDICTED CHAIN
          </span>
          {predictedChain.map((p, i) => (
            <span
              key={i}
              className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border"
              style={{
                background: (PRIMITIVE_COLORS[p] ?? "#22d3ee") + "20",
                borderColor: (PRIMITIVE_COLORS[p] ?? "#22d3ee") + "50",
                color: PRIMITIVE_COLORS[p] ?? "#22d3ee",
              }}
            >
              {p}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}
