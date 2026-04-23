import html as html_lib
import re
from .constants import TASK_META, ACTION_COLORS, ACTION_ICONS, LOG_DISPLAY_COUNT

def _s(text: str, max_len: int = 120) -> str:
    return html_lib.escape(str(text))[:max_len] if text else ""

def _ai_state_html(status="IDLE", cov=0.0, con=0, unc=0.0, prs=0.0) -> str:
    return f'<div id="forge-ai-state" data-status="{status}" data-coverage="{cov:.2f}" data-contras="{con}" data-uncertainty="{unc:.2f}" data-pressure="{prs:.2f}"></div>'

def _topnav(auto=False) -> str:
    pill = ('<div class="forge-live-pill neon-amber"><div class="forge-pulse-dot" style="background:var(--c-amber);"></div>AUTONOMOUS</div>'
            if auto else
            '<div class="forge-live-pill neon-green"><div class="forge-pulse-dot"></div>LIVE</div>')
    return (f'<div class="forge-topnav">'
            f'<div style="display:flex;align-items:center;gap:14px;">'
            f'<div class="forge-logo-icon">🛡️</div>'
            f'<div><div class="forge-logo-text">FORGE</div>'
            f'<div style="font-size:11px;color:var(--c-cyan);font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">Hardened Enterprise Core</div></div>'
            f'</div>{pill}</div>')

def _statusbar_html(status="IDLE", bw="0.0K/S") -> str:
    c = "var(--c-green)" if status in ("OPTIMAL","ACTIVE") else "var(--c-pink)" if status=="ALERT" else "var(--txt2)"
    return (f'<div class="forge-statusbar">'
            f'<span>NET: <span style="color:{c};font-weight:700;text-shadow:0 0 8px {c};">{status}</span></span>'
            f'<span>BW: <span style="color:var(--c-cyan);text-shadow:0 0 8px var(--c-cyan);">{bw}</span></span>'
            f'</div>')

def _left_idle() -> str:
    return ('<div style="padding:22px;">'
            '<div class="section-header"><span class="dot-idle"></span>LIVE FEED</div>'
            '<div style="text-align:center;padding:48px 20px;color:var(--txt2);">'
            '<div class="icon-idle">⏳</div>'
            '<div style="font-size:12px;font-weight:500;">Awaiting Task Initialization</div>'
            '</div></div>')

def _left_active(logs) -> str:
    h = ""
    visible = logs[-LOG_DISPLAY_COUNT:]
    last_idx = len(visible) - 1
    for i, (t, m, a) in enumerate(visible):
        is_newest = (i == last_idx)
        anim_class = "log-entry-new" if is_newest else "log-entry-stable"
        color = ACTION_COLORS.get(a, "var(--c-cyan)")
        h += (f'<div class="log-entry {anim_class}" style="border-left-color:{color};">'
              f'<span class="log-time">{t}</span>'
              f'<div><div class="log-action" style="color:{color};text-shadow:0 0 6px {color}60;">'
              f'{ACTION_ICONS.get(a,"?")} {a.replace("_"," ").title()}</div>'
              f'<div class="log-detail">{_s(m, 80)}</div></div></div>')
    return (f'<div style="padding:22px;">'
            f'<div class="section-header neon-purple-text"><span class="dot-purple"></span>LIVE FEED</div>'
            f'{h}</div>')

def _center_idle() -> str:
    return ('<div class="scanner-container idle-scanner">'
            '<div class="scanner-ring"></div>'
            '<div class="icon-center-idle">⏳</div>'
            '<div style="font-size:14px;font-weight:600;color:var(--txt2);position:relative;z-index:2;">System Standing By</div>'
            '</div>')

def _highlight_entities(text: str) -> str:
    if not isinstance(text, str): return ""
    safe_text = html_lib.escape(text)
    return re.sub(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})+)\b',
                  r'<span class="highlight-entity">\1</span>', safe_text)

def _center_active(claim, task, vir, dom, stat, cov=0.0, div=0.0, bud=1.0) -> str:
    meta = TASK_META.get(task, {"icon": "❓", "code": "UNK"})
    c, d, b = int(cov*100), min(100, int((div/5.0)*100)), max(0, int(bud*100))
    return (f'<div class="scanner-container" style="min-height:340px;padding:22px;">'
            f'<div style="display:flex;justify-content:center;margin-bottom:16px;">'
            f'<div class="task-badge">'
            f'<span>{meta["icon"]}</span>{_s(task.replace("_"," ").title(), 40)}'
            f'<span style="opacity:0.5;font-family:var(--font-mono);">[{meta["code"]}]</span>'
            f'</div></div>'
            f'<div class="claim-text">"{_highlight_entities(claim)}"</div>'
            f'<div style="padding:0 24px 8px;">'
            f'<div class="pb-wrap"><div class="pb-header"><span class="pb-name">Evidence Coverage</span><span class="pb-pct">{c}%</span></div>'
            f'<div class="pb-track"><div class="pb-fill pb-cyan" style="width:{c}%"></div></div></div>'
            f'<div class="pb-wrap"><div class="pb-header"><span class="pb-name">Source Diversity</span><span class="pb-pct">{d}%</span></div>'
            f'<div class="pb-track"><div class="pb-fill pb-purple" style="width:{d}%"></div></div></div>'
            f'<div class="pb-wrap" style="margin-bottom:0"><div class="pb-header"><span class="pb-name">Budget Remaining</span><span class="pb-pct">{b}%</span></div>'
            f'<div class="pb-track"><div class="pb-fill pb-green" style="width:{b}%"></div></div></div>'
            f'</div>'
            f'<div class="meta-grid">'
            f'<div class="meta-card"><div class="meta-label">Node Source</div><div class="meta-value" style="font-size:14px;color:var(--txt);">{_s(dom.title(), 20)}</div></div>'
            f'<div class="meta-card"><div class="meta-label">Viral Index</div><div class="meta-value">{vir*100:.1f}%</div></div>'
            f'<div class="meta-card"><div class="meta-label">Status</div><div class="meta-value" style="font-size:13px;">{_s(stat, 15)}</div></div>'
            f'</div></div>')

def _right_idle() -> str:
    return ('<div style="padding:22px;height:100%;display:flex;align-items:center;justify-content:center;">'
            '<div style="text-align:center;color:var(--txt2);">'
            '<div class="icon-agent-idle">⏳</div>'
            '<div style="font-size:13px;font-weight:600;">Agent Offline</div>'
            '</div></div>')

def _right_active(think, pred, fsm, step, max_s, cov, con) -> str:
    return (f'<div style="padding:22px;">'
            f'<div class="section-header neon-pink-text"><span class="dot-pink"></span>AGENT THOUGHT STREAM</div>'
            f'<div class="thought-box">"{_s(think, 320)}"</div>'
            f'<div style="display:flex;gap:10px;align-items:center;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
            f'<div class="orbit-badge"><div class="orbit-ring-1"></div><div class="orbit-ring-2"></div><span class="orbit-val">{step}</span></div>'
            f'<div style="font-size:9px;color:var(--txt2);font-family:var(--font-mono);">/{max_s}</div>'
            f'</div>'
            f'<div style="display:flex;flex-direction:column;gap:8px;flex:1;">'
            f'<div style="display:flex;gap:8px;">'
            f'<div class="stat-mini stat-cyan"><div class="stat-mini-label">Coverage</div><div class="stat-mini-val" style="color:var(--c-cyan);">{cov:.0%}</div></div>'
            f'<div class="stat-mini stat-purple"><div class="stat-mini-label" style="color:#c4b5fd;">FSM State</div><div class="stat-mini-val" style="color:#e9d5ff;font-size:11px;">{_s(fsm, 9)}</div></div>'
            f'</div>'
            f'<div style="display:flex;gap:8px;">'
            f'<div class="stat-mini stat-pink"><div class="stat-mini-label" style="color:#fda4af;">Contradictions</div><div class="stat-mini-val" style="color:var(--c-pink);">{con}</div></div>'
            f'<div class="stat-mini stat-green"><div class="stat-mini-label" style="color:#6ee7b7;">Predict</div><div class="stat-mini-val" style="color:var(--c-green);font-size:11px;">{_s(pred, 9) or "–"}</div></div>'
            f'</div></div></div></div>')

def _right_done(verdict, true_l, correct, steps, reward, conf) -> str:
    cls, glow, badge_text, icon = (
        ("verdict-correct", "var(--c-green)", "✓ CORRECT VERDICT", "✓")
        if correct else
        ("verdict-wrong", "var(--c-pink)", "✗ INCORRECT VERDICT", "✗")
        )
    return (f'<div style="padding:22px;">'
            f'<div class="section-header">INVESTIGATION RESOLVED</div>'
            f'<div class="{cls}" style="margin-bottom:16px;">'
            f'<div class="verdict-icon" style="filter:drop-shadow(0 0 20px {glow});">{icon}</div>'
            f'<div class="verdict-text" style="color:{glow};text-shadow:0 0 26px {glow};">{badge_text}</div>'
            f'<div style="font-size:11px;color:var(--txt2);font-family:var(--font-mono);">confidence · {conf:.1%}</div>'
            f'</div>'
            f'<div class="result-box">'
            f'<div class="result-row"><span class="result-label">Submitted Verdict</span>'
            f'<span class="result-value">{_s(str(verdict).title(), 20)}</span></div>'
            f'<div class="result-row"><span class="result-label">Ground Truth</span>'
            f'<span style="font-size:12px;color:{glow};font-weight:700;text-shadow:0 0 8px {glow}80;">{_s(str(true_l).title(), 20)}</span></div>'
            f'<div class="result-row" style="border-bottom:none;"><span class="result-label">Steps / Reward</span>'
            f'<span style="font-size:12px;color:var(--c-cyan);font-weight:700;font-family:var(--font-mono);text-shadow:0 0 6px var(--c-cyan);">{steps} / {reward:.3f}</span></div>'
            f'</div></div>')

def _graph_text(env, metrics_stats) -> str:
    base = "Graph uninit."
    if env is not None:
        try:
            if hasattr(env, "get_graph_stats"):
                stats = env.get_graph_stats()
                if stats:
                    retrieved, total, cov, con = stats
                    base = f"Nodes: {retrieved}/{total} | Cov: {cov:.1%} | Contra: {con}"
                else:
                    base = "Graph: 0 nodes (initialising...)"
            elif getattr(env, "graph", None):
                g = env.graph
                base = f"Nodes: {sum(1 for n in g.nodes.values() if n.retrieved)}/{len(g.nodes)} | Cov: {g.evidence_coverage:.1%} | Contra: {g.contradiction_surface_area}"
        except Exception as exc:
            base = f"Graph err: {exc}"
    stats = metrics_stats
    base += f"  ||  [O11Y] Runs: {stats['runs']} | P50: {float(stats['p50']):.1f}ms | P99: {float(stats['p99']):.1f}ms | Err: {stats['errors']}"
    return base
