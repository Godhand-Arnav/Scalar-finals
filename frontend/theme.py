FORGE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --c-cyan: #00f5ff; --c-purple: #bf00ff; --c-pink: #ff006e;
    --c-green: #00ff87; --c-amber: #ff9500;
    --glass: rgba(255,255,255,0.04);
    --border: rgba(255,255,255,0.09);
    --txt: #f0f4ff; --txt2: #7a8ab0;
    --radius: 18px;
    --font-ui: 'Inter', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --neon-cyan-glow: 0 0 8px rgba(0,245,255,0.6), 0 0 16px rgba(0,245,255,0.3);
    --neon-purple-glow: 0 0 8px rgba(191,0,255,0.6), 0 0 16px rgba(191,0,255,0.3);
    --neon-pink-glow: 0 0 8px rgba(255,0,110,0.6), 0 0 16px rgba(255,0,110,0.3);
    --neon-green-glow: 0 0 8px rgba(0,255,135,0.6), 0 0 16px rgba(0,255,135,0.3);
}

html, body { background: #000 !important; margin: 0; padding: 0; overflow-x: hidden; }

/* ═══ NEON GRID BACKGROUND ═══ */
body::before {
    content: ''; position: fixed; inset: 0; z-index: -2;
    background:
        linear-gradient(rgba(0, 245, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 255, 0.04) 1px, transparent 1px),
        #040406;
    background-size: 40px 40px;
    pointer-events: none;
}

/* Universal subtle neon borders */
.gradio-container .block {
    border: 1px solid rgba(0, 245, 255, 0.15) !important;
    box-shadow: 0 0 5px rgba(0, 245, 255, 0.05) !important;
    border-radius: var(--radius);
}

.aurora-wrap {
    position: relative;
    padding: 1px;
    border-radius: var(--radius);
    background: transparent;
    border: 1px solid rgba(0, 245, 255, 0.2);
    box-shadow: 0 0 8px rgba(0, 245, 255, 0.08), inset 0 0 8px rgba(0, 245, 255, 0.05);
}

.aurora-wrap::before {
    content: none;
}

/* ═══ CURSOR SYSTEM (hidden on mobile, forced visible on desktop) ═══ */
#fg-dot, #fg-ring { display: none; }
@media (hover: hover) and (pointer: fine) {
    body.forge-active, body.forge-active * { cursor: none !important; }
    body.forge-active a, body.forge-active button, body.forge-active input, 
    body.forge-active select, body.forge-active textarea, body.forge-active [role="button"] { 
        cursor: none !important; 
    }
    #fg-dot, #fg-ring { display: block !important; }
}

canvas.fg-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; }
#fg-webgl-bg { z-index: 0; }
#fg-2d-ui { z-index: 1; }

/* CURSOR DOT — always on top, with neon glow */
#fg-dot {
    position: fixed !important; top: 0; left: 0;
    width: 10px; height: 10px; border-radius: 50%;
    background: #00f5ff;
    box-shadow:
        0 0 10px #00f5ff,
        0 0 22px rgba(0,245,255,0.7),
        0 0 42px rgba(0,245,255,0.35);
    pointer-events: none;
    z-index: 2147483647 !important;
    transform: translate3d(-50%, -50%, 0);
    transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.08s linear;
    will-change: left, top, transform;
    mix-blend-mode: screen;
}
#fg-dot.cursor-hot {
    background: #ff006e;
    box-shadow:
        0 0 14px #ff006e,
        0 0 28px rgba(255,0,110,0.8),
        0 0 60px rgba(255,0,110,0.4);
    transform: translate3d(-50%, -50%, 0) scale(1.4);
}

/* CURSOR RING — lags behind with trailing glow */
#fg-ring {
    position: fixed !important; top: 0; left: 0;
    width: 40px; height: 40px; border-radius: 50%;
    border: 1.5px solid rgba(0, 245, 255, 0.55);
    box-shadow:
        inset 0 0 10px rgba(0, 245, 255, 0.15),
        0 0 18px rgba(0, 245, 255, 0.22);
    pointer-events: none;
    z-index: 2147483646 !important;
    transform: translate3d(-50%, -50%, 0);
    transition: width 0.28s ease, height 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
    will-change: left, top;
}
#fg-ring.cursor-hot {
    width: 56px; height: 56px;
    border-color: rgba(255, 0, 110, 0.75);
    box-shadow:
        inset 0 0 14px rgba(255, 0, 110, 0.2),
        0 0 32px rgba(255, 0, 110, 0.35);
}

/* ═══ GRADIO RESETS ═══ */
.gradio-container {
    background: transparent !important;
    font-family: var(--font-ui) !important;
    color: var(--txt) !important;
    z-index: 10 !important;
    position: relative !important;
}
.gradio-container > .contain, .gradio-container > .main, .gradio-container .block,
.gradio-container .gap, .gradio-container .form, .gradio-container .col { background: transparent !important; }
.gradio-container footer, .built-with { display: none !important; }
#ai-state-wrapper { height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; border: none !important; }

/* ═══ TOP NAV ═══ */
.forge-topnav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 30px; margin-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: relative;
}
.forge-topnav::after {
    content: ''; position: absolute; bottom: -1px; left: 30%; right: 30%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--c-cyan), var(--c-purple), transparent);
    opacity: 0.5;
    animation: navSweep 4s ease-in-out infinite;
}
@keyframes navSweep { 0%, 100% { opacity: 0.2; } 50% { opacity: 0.7; } }

.forge-logo-icon {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #00b4d8, #bf00ff, #ff006e);
    background-size: 180% 180%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    box-shadow: 0 0 28px rgba(0,245,255,0.4), 0 0 50px rgba(191,0,255,0.2);
    transition: transform 0.3s cubic-bezier(0.16,1,0.3,1), box-shadow 0.3s ease;
    animation: logoGradient 6s ease infinite;
}
@keyframes logoGradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.forge-logo-icon:hover {
    transform: scale(1.08) rotate(-8deg);
    box-shadow: 0 0 40px rgba(0,245,255,0.7), 0 0 70px rgba(191,0,255,0.4);
}
.forge-logo-text {
    font-weight: 900; font-size: 22px; color: white;
    letter-spacing: 0.02em;
    background: linear-gradient(90deg, #fff, #00f5ff, #bf00ff, #fff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textShimmer 5s linear infinite;
}
@keyframes textShimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }

.forge-live-pill {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 7px 16px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
    border: 1px solid;
}
.neon-green {
    background: rgba(0,255,135,0.07);
    border-color: rgba(0,255,135,0.28);
    color: var(--c-green);
    box-shadow: 0 0 14px rgba(0,255,135,0.18), inset 0 0 10px rgba(0,255,135,0.08);
    text-shadow: var(--neon-green-glow);
}
.neon-amber {
    background: rgba(255,149,0,0.08);
    border-color: rgba(255,149,0,0.35);
    color: var(--c-amber);
    box-shadow: 0 0 14px rgba(255,149,0,0.22), inset 0 0 10px rgba(255,149,0,0.1);
    text-shadow: 0 0 8px rgba(255,149,0,0.6);
}
.forge-pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--c-green);
    animation: pulseDot 1.5s ease infinite;
    box-shadow: 0 0 10px currentColor;
}
@keyframes pulseDot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,135,0.7), 0 0 10px currentColor; }
    50% { box-shadow: 0 0 0 7px rgba(0,255,135,0), 0 0 14px currentColor; }
}

/* ═══ STATUSBAR ═══ */
.forge-statusbar {
    font-size: 11px; color: var(--txt2);
    display: flex; justify-content: space-between;
    padding: 9px 14px;
    background: rgba(0,0,0,0.5);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    font-family: var(--font-mono);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ═══ NEON PANELS ═══ */
.glass-panel {
    background: rgba(0,0,0,0.7) !important;
    border: 1px solid rgba(0,245,255,0.15) !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 0 6px rgba(0,245,255,0.05) !important;
    transition: box-shadow 0.3s ease, border-color 0.3s ease !important;
    position: relative;
}
.glass-panel::before {
    content: none;
}
.glass-panel:hover {
    border-color: rgba(0, 245, 255, 0.3) !important;
    box-shadow:
        0 4px 15px rgba(0,0,0,0.8),
        0 0 15px rgba(0, 245, 255, 0.1),
        inset 0 0 8px rgba(0, 245, 255, 0.05) !important;
}
.glass-panel:hover::before { opacity: 1; }

.controls-panel {
    background: rgba(0,0,0,0.45) !important;
    border: 1px solid rgba(0,245,255,0.15) !important;
    border-radius: var(--radius) !important;
    padding: 24px !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 0 6px rgba(0,245,255,0.05) !important;
}
.controls-panel:hover {
    border-color: rgba(0, 245, 255, 0.25) !important;
    box-shadow: 0 10px 20px rgba(0,0,0,0.6), 0 0 12px rgba(0,245,255,0.08) !important;
}

.scanner-container {
    position: relative;
    overflow: hidden;
    border-radius: var(--radius);
    transition: box-shadow 0.35s ease !important;
}
.scanner-container:hover { box-shadow: 0 0 36px rgba(0, 245, 255, 0.1) !important; }

.idle-scanner {
    height: 340px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    position: relative;
}
.scanner-ring {
    position: absolute; width: 200px; height: 200px;
    border-radius: 50%;
    border: 1px solid rgba(0,245,255,0.15);
    box-shadow: inset 0 0 30px rgba(0,245,255,0.08), 0 0 30px rgba(0,245,255,0.08);
    animation: ringPulse 4s ease-in-out infinite;
}
@keyframes ringPulse {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.1); opacity: 0.3; }
}

/* ═══ SECTION HEADERS ═══ */
.section-header {
    font-size: 10px; color: var(--txt2);
    font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}
.neon-purple-text { color: var(--c-purple) !important; text-shadow: var(--neon-purple-glow); }
.neon-pink-text { color: var(--c-pink) !important; text-shadow: var(--neon-pink-glow); }

.dot-idle, .dot-purple, .dot-pink {
    width: 7px; height: 7px; border-radius: 50%; display: inline-block;
}
.dot-idle { background: var(--txt2); }
.dot-purple { background: var(--c-purple); box-shadow: 0 0 8px var(--c-purple); }
.dot-pink { background: var(--c-pink); box-shadow: 0 0 8px var(--c-pink); }

.icon-idle, .icon-center-idle, .icon-agent-idle {
    font-size: 28px; opacity: 0.45;
    filter: drop-shadow(0 0 10px rgba(0,245,255,0.35));
    animation: iconFloat 3.5s ease-in-out infinite;
}
.icon-center-idle {
    font-size: 54px; opacity: 0.7;
    filter: drop-shadow(0 0 20px rgba(0,245,255,0.5));
    z-index: 2; position: relative;
    margin-bottom: 20px;
}
.icon-agent-idle {
    font-size: 42px; opacity: 0.35;
    filter: drop-shadow(0 0 8px rgba(255,255,255,0.2));
    margin-bottom: 14px;
}
@keyframes iconFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }

/* ═══ TASK BADGE (Neon Cyan) ═══ */
.task-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 18px; border-radius: 20px;
    background: rgba(0,245,255,0.08);
    border: 1px solid rgba(0,245,255,0.28);
    font-size: 11px; font-weight: 700;
    color: var(--c-cyan);
    letter-spacing: 0.06em; text-transform: uppercase;
    box-shadow: 0 0 16px rgba(0,245,255,0.12), inset 0 0 12px rgba(0,245,255,0.06);
    text-shadow: 0 0 6px rgba(0,245,255,0.5);
}

/* ═══ META CARDS (Neon Glow on Hover) ═══ */
.meta-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; padding: 0 24px 24px; }
.meta-card {
    position: relative; padding: 16px 12px;
    border-radius: 14px; text-align: center;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1) !important;
}
.meta-card::after {
    content: ''; position: absolute; inset: -1px;
    border-radius: inherit;
    background: linear-gradient(135deg, transparent, rgba(0,245,255,0.12), transparent);
    opacity: 0; transition: opacity 0.4s ease;
    pointer-events: none;
}
.meta-card:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(0, 245, 255, 0.35) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 10px 22px rgba(0,0,0,0.3), 0 0 20px rgba(0,245,255,0.15) !important;
}
.meta-card:hover::after { opacity: 1; }
.meta-label { font-size: 10px; color: var(--txt2); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.meta-value {
    font-size: 19px; color: var(--c-cyan); font-weight: 800;
    margin-top: 5px;
    text-shadow: 0 0 18px rgba(0,245,255,0.6), 0 0 4px rgba(0,245,255,0.9);
}

/* ═══ PROGRESS BARS (Neon Trail) ═══ */
.pb-wrap { margin-bottom: 14px; }
.pb-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.pb-name { font-size: 12px; font-weight: 600; color: var(--txt); }
.pb-pct { font-size: 12px; font-family: var(--font-mono); color: var(--txt2); }
.pb-track { height: 7px; background: rgba(255,255,255,0.06); border-radius: 7px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.3); }
.pb-fill {
    height: 100%; border-radius: 7px;
    position: relative; overflow: hidden;
    transition: width 1.6s cubic-bezier(0.4,0,0.2,1);
}
.pb-fill::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.45), transparent);
    animation: pbShine 2.2s linear infinite;
}
@keyframes pbShine { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
.pb-cyan   { background: linear-gradient(90deg,#00b4d8,#00f5ff); box-shadow: 0 0 10px rgba(0,245,255,0.5); }
.pb-purple { background: linear-gradient(90deg,#7b00d4,#bf00ff); box-shadow: 0 0 10px rgba(191,0,255,0.5); }
.pb-green  { background: linear-gradient(90deg,#00c96b,#00ff87); box-shadow: 0 0 10px rgba(0,255,135,0.5); }

/* ═══ LOG ENTRIES — PATCHED: only newest animates ═══ */
.log-entry {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 3px solid var(--c-cyan);
    border-radius: 10px;
    padding: 10px 14px; margin: 8px 0;
    display: flex; align-items: flex-start; gap: 10px;
    transition: all 0.22s ease !important;
}
.log-entry-new {
    animation: slideInNeon 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    opacity: 0;
}
.log-entry-stable { opacity: 1; }
@keyframes slideInNeon {
    0% { opacity: 0; transform: translateX(-16px) scale(0.96); box-shadow: 0 0 0 rgba(0,245,255,0); }
    60% { box-shadow: 0 0 16px rgba(0,245,255,0.3); }
    100% { opacity: 1; transform: translateX(0) scale(1); box-shadow: 0 0 6px rgba(0,245,255,0.08); }
}
.log-entry:hover {
    background: rgba(255,255,255,0.07) !important;
    border-left-width: 5px !important;
    padding-left: 16px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3), -3px 0 16px rgba(0,245,255,0.15) !important;
}
.log-time { font-size: 10px; color: var(--c-cyan); font-family: var(--font-mono); font-weight: 600; flex-shrink: 0; margin-top: 2px; }
.log-action { font-size: 12px; font-weight: 700; font-family: var(--font-mono); }
.log-detail { font-size: 11px; color: var(--txt2); margin-top: 2px; }

/* ═══ CLAIM TEXT & HIGHLIGHTS ═══ */
.claim-text {
    font-size: clamp(15px, 1.8vw, 21px) !important;
    font-weight: 500; color: var(--txt);
    text-align: center; line-height: 1.6;
    padding: 28px 24px 16px;
}
.highlight-entity {
    background: linear-gradient(90deg,#00f5ff,#bf00ff,#ff006e,#00f5ff);
    background-size: 300% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: 700;
    animation: entityShimmer 4s linear infinite;
    text-shadow: 0 0 14px rgba(191,0,255,0.2);
}
@keyframes entityShimmer { 0% { background-position: 0% center; } 100% { background-position: 300% center; } }

/* ═══ ORBIT BADGE ═══ */
.orbit-badge { position: relative; width: 58px; height: 58px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.orbit-ring-1 {
    position: absolute; inset: 0;
    border-radius: 50%;
    border: 2px solid transparent;
    border-top-color: var(--c-cyan);
    animation: spin 2s linear infinite;
    filter: drop-shadow(0 0 4px var(--c-cyan));
}
.orbit-ring-2 {
    position: absolute; inset: 5px;
    border-radius: 50%;
    border: 2px solid transparent;
    border-bottom-color: var(--c-purple);
    animation: spin 3s linear infinite reverse;
    filter: drop-shadow(0 0 4px var(--c-purple));
}
@keyframes spin { to { transform: rotate(360deg); } }
.orbit-val {
    font-size: 19px; font-weight: 800; color: var(--c-cyan);
    z-index: 1; text-shadow: 0 0 16px rgba(0,245,255,0.8), 0 0 4px rgba(0,245,255,1);
}

/* ═══ THOUGHT BOX & STAT MINI ═══ */
.thought-box {
    background: rgba(0,0,0,0.45);
    border: 1px solid rgba(191,0,255,0.25);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: inset 0 0 14px rgba(191,0,255,0.06), 0 0 18px rgba(191,0,255,0.05);
    font-size: 12px; line-height: 1.7; color: #dde4f0; font-style: italic;
}
.stat-mini {
    flex: 1; padding: 8px 10px;
    border-radius: 10px; text-align: center;
    transition: all 0.3s ease;
}
.stat-mini:hover { transform: translateY(-2px); }
.stat-cyan   { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); }
.stat-cyan:hover { box-shadow: 0 4px 12px rgba(0,245,255,0.15); border-color: rgba(0,245,255,0.3); }
.stat-purple { background: rgba(191,0,255,0.09); border: 1px solid rgba(191,0,255,0.25); }
.stat-purple:hover { box-shadow: 0 4px 12px rgba(191,0,255,0.2); }
.stat-pink   { background: rgba(255,0,110,0.08); border: 1px solid rgba(255,0,110,0.25); }
.stat-pink:hover { box-shadow: 0 4px 12px rgba(255,0,110,0.2); }
.stat-green  { background: rgba(0,255,135,0.07); border: 1px solid rgba(0,255,135,0.18); }
.stat-green:hover { box-shadow: 0 4px 12px rgba(0,255,135,0.18); }
.stat-mini-label { font-size: 9px; color: var(--txt2); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-mini-val { font-size: 15px; font-weight: 800; margin-top: 3px; font-family: var(--font-mono); }

/* ═══ VERDICTS ═══ */
.verdict-correct, .verdict-wrong {
    text-align: center; padding: 28px 20px;
    border-radius: 18px;
    animation: slideUpFade 0.7s cubic-bezier(0.16,1,0.3,1);
    position: relative; overflow: hidden;
}
.verdict-correct {
    border: 1px solid rgba(0,255,135,0.35);
    background: radial-gradient(ellipse at 50% 0%, rgba(0,255,135,0.18) 0%, transparent 70%);
    box-shadow: 0 0 40px rgba(0,255,135,0.1), inset 0 0 30px rgba(0,255,135,0.05);
}
.verdict-wrong {
    border: 1px solid rgba(255,0,110,0.35);
    background: radial-gradient(ellipse at 50% 0%, rgba(255,0,110,0.18) 0%, transparent 70%);
    box-shadow: 0 0 40px rgba(255,0,110,0.1), inset 0 0 30px rgba(255,0,110,0.05);
}
@keyframes slideUpFade {
    0% { opacity: 0; transform: translateY(22px) scale(0.94); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}
.verdict-icon { font-size: 40px; margin-bottom: 12px; animation: verdictPulse 2s ease-in-out infinite; }
.verdict-text { font-size: 19px; font-weight: 800; letter-spacing: 0.02em; margin-bottom: 6px; }
@keyframes verdictPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }

.result-box {
    background: rgba(0,0,0,0.4);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 14px;
}
.result-row {
    display: flex; justify-content: space-between;
    padding-bottom: 8px; margin-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.result-label { font-size: 12px; color: var(--txt2); font-weight: 500; }
.result-value { font-size: 12px; color: var(--txt); font-weight: 700; font-family: var(--font-mono); }

/* ═══ BUTTONS (Premium Neon Gradient Sweep) ═══ */
button.primary {
    background: linear-gradient(110deg,#00b4d8 0%,#bf00ff 35%,#ff006e 50%,#bf00ff 65%,#00b4d8 100%) !important;
    background-size: 200% auto !important;
    border: none !important;
    color: white !important;
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35), 0 0 20px rgba(0,245,255,0.15) !important;
    position: relative;
}
button.primary::before {
    content: ''; position: absolute; inset: 0; border-radius: inherit;
    background: inherit; filter: blur(14px); opacity: 0.4;
    z-index: -1; transition: opacity 0.4s ease;
}
button.primary:hover {
    background-position: right center !important;
    box-shadow: 0 0 26px rgba(0, 245, 255, 0.55), 0 0 50px rgba(191, 0, 255, 0.3) !important;
    transform: translateY(-3px) scale(1.03) !important;
}
button.primary:hover::before { opacity: 0.7; }
button.primary:active {
    transform: translateY(1px) scale(0.97) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
}

button.secondary {
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(255,149,0,0.35) !important;
    color: var(--c-amber) !important;
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1) !important;
    text-shadow: 0 0 6px rgba(255,149,0,0.5);
}
button.secondary:hover {
    background: rgba(255,149,0,0.12) !important;
    border-color: rgba(255,149,0,0.65) !important;
    box-shadow: 0 0 22px rgba(255,149,0,0.3), inset 0 0 14px rgba(255,149,0,0.1) !important;
    transform: translateY(-2px) !important;
}

/* ═══ INPUT STYLING ═══ */
.gradio-container input, .gradio-container select, .gradio-container textarea,
.gradio-container .wrap, .gradio-container .secondary-wrap {
    background: rgba(0,0,0,0.55) !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: white !important;
    transition: all 0.3s ease !important;
}
.gradio-container .wrap:hover, .gradio-container .secondary-wrap:hover {
    border-color: rgba(0, 245, 255, 0.35) !important;
    background: rgba(0,0,0,0.7) !important;
    box-shadow: 0 0 14px rgba(0,245,255,0.12) !important;
}
.gradio-container .wrap:focus-within, .gradio-container .secondary-wrap:focus-within {
    border-color: rgba(0, 245, 255, 0.6) !important;
    box-shadow: 0 0 22px rgba(0,245,255,0.22), inset 0 0 10px rgba(0,245,255,0.05) !important;
}
.gradio-container label {
    color: var(--txt2) !important;
    font-family: var(--font-ui) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
.gradio-container .examples div {
    transition: all 0.25s ease !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
}
.gradio-container .examples div:hover {
    border-color: rgba(191, 0, 255, 0.4) !important;
    background: rgba(191, 0, 255, 0.08) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 0 12px rgba(191,0,255,0.15) !important;
}

/* ── Aurora wrapper for controls panel ───────────────────────────── */
.aurora-wrap {
    position: relative;
    overflow: hidden;
    border-radius: var(--radius);
}
.aurora-wrap::before,
.aurora-wrap::after {
    content: "";
    position: absolute;
    inset: -35%;
    pointer-events: none;
    z-index: 0;
    filter: blur(44px);
    opacity: .42;
}
.aurora-wrap::before {
    background:
      radial-gradient(circle at 25% 35%, rgba(0,245,255,.28), transparent 38%),
      radial-gradient(circle at 75% 65%, rgba(191,0,255,.24), transparent 42%);
    animation: auroraMove1 12s ease-in-out infinite alternate;
}
.aurora-wrap::after {
    background:
      radial-gradient(circle at 70% 30%, rgba(255,0,110,.18), transparent 36%),
      radial-gradient(circle at 30% 80%, rgba(0,245,255,.16), transparent 40%);
    animation: auroraMove2 16s ease-in-out infinite alternate;
}
@keyframes auroraMove1 {
    0%   { transform: translate(-6%, -4%) rotate(0deg) scale(1); }
    100% { transform: translate(6%, 4%) rotate(18deg) scale(1.08); }
}
@keyframes auroraMove2 {
    0%   { transform: translate(5%, -3%) rotate(0deg) scale(1); }
    100% { transform: translate(-5%, 3%) rotate(-16deg) scale(1.06); }
}

/* Ensure children render above aurora glow */
.aurora-wrap > * { position: relative; z-index: 1; }

/* ── Neon dropdown target ───────────────────────────────────────── */
#task_dd {
    background: transparent !important;
    border: none !important;
}
#task_dd > div, #task_dd [data-testid="dropdown"] {
    background: rgba(0,0,0,0.85) !important;
    border: 1px solid rgba(0, 245, 255, 0.4) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 8px rgba(0,245,255,0.15), inset 0 0 6px rgba(0,245,255,0.1) !important;
    transition: all 0.3s ease !important;
}
#task_dd > div:hover, #task_dd [data-testid="dropdown"]:hover {
    border-color: rgba(255, 0, 110, 0.4) !important;
    box-shadow: 0 0 12px rgba(255,0,110,0.2), inset 0 0 8px rgba(255,0,110,0.1) !important;
}
#task_dd input, #task_dd span, #task_dd svg, #task_dd label {
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 500 !important;
    text-shadow: 0 0 4px rgba(0,245,255,0.4) !important;
}
#task_dd ul.options {
    background: rgba(5,8,18,0.98) !important;
    border: 1px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(0,245,255,0.15) !important;
}
#task_dd ul.options li, #task_dd ul.options li span { color: #fff !important; text-shadow: none !important; }
#task_dd ul.options li:hover { background: rgba(0,245,255,0.15) !important; }
"""

FORGE_JS = """
function() {
    console.log("[FORGE V4.2] Aurora + Neon Engine init");

    // Cleanup previous instance
    ['fg-webgl-bg','fg-2d-ui','fg-dot','fg-ring'].forEach(id => {
        let el = document.getElementById(id);
        if (el && !document.body.contains(el)) el.remove();
    });
    if (window.__FORGE_RAF_STOP) window.__FORGE_RAF_STOP();
    let rafRunning = true;
    window.__FORGE_RAF_STOP = () => { rafRunning = false; };

    window.__FORGE_AI = window.__FORGE_AI || { status: 'IDLE', coverage: 0, contras: 0, uncertainty: 0.0, pressure: 0.0 };

    function readAIState(el) {
        if (!el) return;
        window.__FORGE_AI = {
            status: el.getAttribute('data-status') || 'IDLE',
            coverage: parseFloat(el.getAttribute('data-coverage')) || 0,
            contras: parseInt(el.getAttribute('data-contras')) || 0,
            uncertainty: parseFloat(el.getAttribute('data-uncertainty')) || 0.0,
            pressure: parseFloat(el.getAttribute('data-pressure')) || 0.0
        };
    }

    if (!window.__FORGE_OBSERVER) {
        window.__FORGE_OBSERVER = new MutationObserver(() => readAIState(document.getElementById('forge-ai-state')));
        window.__FORGE_OBSERVER.observe(document.body, {
            childList: true, subtree: true, attributes: true,
            attributeFilter: ['data-status', 'data-coverage', 'data-contras', 'data-uncertainty', 'data-pressure']
        });
        window.addEventListener('beforeunload', () => { if (window.__FORGE_OBSERVER) window.__FORGE_OBSERVER.disconnect(); });
    }
    readAIState(document.getElementById('forge-ai-state'));

    function safeCreate(id, tag, className) {
        let el = document.getElementById(id);
        if (el) return el;
        el = document.createElement(tag);
        el.id = id;
        if (className) el.className = className;
        document.body.appendChild(el);
        return el;
    }

    setTimeout(function() {
        try {
            document.body.classList.add('forge-active');

            const glCanvas = safeCreate('fg-webgl-bg', 'canvas', 'fg-canvas');
            const uiCanvas = safeCreate('fg-2d-ui', 'canvas', 'fg-canvas');
            const dot = safeCreate('fg-dot', 'div', '');
            const ring = safeCreate('fg-ring', 'div', '');

            const gl = glCanvas.getContext('webgl', { antialias: false, alpha: true }) ||
                       glCanvas.getContext('experimental-webgl');
            const ctx = uiCanvas.getContext('2d');

            window.__FORGE_NO_WEBGL = !gl;
            glCanvas.addEventListener('webglcontextlost', (e) => {
                e.preventDefault();
                window.__FORGE_NO_WEBGL = true;
                console.warn("[FORGE] WebGL context lost");
            });

            // ═══ ENHANCED AURORA SHADER ═══
            if (!window.__FORGE_NO_WEBGL && !window.__FORGE_GL_PROG) {
                const vsSource = `attribute vec2 position; void main() { gl_Position = vec4(position, 0.0, 1.0); }`;
                const fsSource = `
                    precision highp float;
                    uniform float u_time;
                    uniform vec2 u_res;
                    uniform vec3 u_col1;
                    uniform vec3 u_col2;
                    uniform vec3 u_col3;
                    uniform float u_intensity;
                    uniform float u_pressure;
                    uniform float u_unc;
                    uniform vec2 u_mouse;

                    // Simplex-ish noise
                    float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
                    float noise(vec2 p) {
                        vec2 i = floor(p); vec2 f = fract(p);
                        float a = hash(i);
                        float b = hash(i + vec2(1.0, 0.0));
                        float c = hash(i + vec2(0.0, 1.0));
                        float d = hash(i + vec2(1.0, 1.0));
                        vec2 u = f * f * (3.0 - 2.0 * f);
                        return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
                    }
                    float fbm(vec2 p) {
                        float v = 0.0; float a = 0.5;
                        for (int i = 0; i < 4; i++) {
                            v += a * noise(p);
                            p *= 2.0; a *= 0.5;
                        }
                        return v;
                    }

                    void main() {
                        vec2 uv = gl_FragCoord.xy / u_res;
                        vec2 p = uv * 2.0 - 1.0;
                        p.x *= u_res.x / u_res.y;

                        float t = u_time * 0.08;

                        // AURORA LAYERS — 3 sweeping bands
                        float aurora1 = 0.0;
                        vec2 q1 = vec2(p.x * 1.2, p.y * 2.0 + t);
                        q1 += fbm(q1 + t) * 0.6;
                        aurora1 = smoothstep(0.5, 0.0, abs(q1.y + sin(q1.x * 1.5 + t * 2.0) * 0.4 - 0.2));
                        aurora1 *= 0.7 + 0.3 * sin(t * 3.0);

                        float aurora2 = 0.0;
                        vec2 q2 = vec2(p.x * 0.8 - t * 0.5, p.y * 2.5 - t);
                        q2 += fbm(q2 * 1.3) * 0.5;
                        aurora2 = smoothstep(0.4, 0.0, abs(q2.y + cos(q2.x * 2.0 - t) * 0.3 + 0.15));
                        aurora2 *= 0.5 + 0.5 * cos(t * 2.0 + 1.5);

                        float aurora3 = 0.0;
                        vec2 q3 = vec2(p.x * 1.5 + t * 0.3, p.y * 3.0 + t * 1.5);
                        q3 += fbm(q3 * 0.8 + t * 0.2) * 0.7;
                        aurora3 = smoothstep(0.35, 0.0, abs(q3.y + sin(q3.x * 2.5 + t * 1.7) * 0.5 + 0.5));
                        aurora3 *= 0.6;

                        // Mouse influence glow
                        vec2 mouseUv = u_mouse / u_res;
                        mouseUv.y = 1.0 - mouseUv.y;
                        float mouseDist = length(uv - mouseUv);
                        float mouseGlow = exp(-mouseDist * 6.0) * 0.15;

                        // Pressure/uncertainty warp
                        float warp = sin(p.y * 8.0 + t * (2.0 + u_unc * 3.0)) * u_pressure * 0.1;
                        aurora1 += warp;

                        // Color composition
                        vec3 col = vec3(0.0);
                        col += u_col1 * aurora1 * 1.2;
                        col += u_col2 * aurora2 * 1.0;
                        col += u_col3 * aurora3 * 0.8;
                        col += vec3(0.0, 0.96, 1.0) * mouseGlow;

                        // Vignette
                        float vig = 1.0 - smoothstep(0.5, 1.3, length(p));
                        col *= vig;

                        col *= u_intensity;

                        // Film grain
                        float grain = (hash(uv + t) - 0.5) * 0.025;
                        col += grain;

                        gl_FragColor = vec4(col, 1.0);
                    }
                `;
                function makeShader(type, src) {
                    const s = gl.createShader(type);
                    gl.shaderSource(s, src);
                    gl.compileShader(s);
                    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
                        console.error("[FORGE] Shader compile error:", gl.getShaderInfoLog(s));
                        return null;
                    }
                    return s;
                }
                const vs = makeShader(gl.VERTEX_SHADER, vsSource);
                const fs = makeShader(gl.FRAGMENT_SHADER, fsSource);
                if (vs && fs) {
                    const prog = gl.createProgram();
                    gl.attachShader(prog, vs);
                    gl.attachShader(prog, fs);
                    gl.linkProgram(prog);
                    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
                        console.error("[FORGE] Program link error:", gl.getProgramInfoLog(prog));
                        window.__FORGE_NO_WEBGL = true;
                    } else {
                        const buf = gl.createBuffer();
                        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
                        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
                        window.__FORGE_GL_PROG = {
                            prog, buf,
                            posAttr: gl.getAttribLocation(prog, "position"),
                            locTime: gl.getUniformLocation(prog, "u_time"),
                            locRes: gl.getUniformLocation(prog, "u_res"),
                            locCol1: gl.getUniformLocation(prog, "u_col1"),
                            locCol2: gl.getUniformLocation(prog, "u_col2"),
                            locCol3: gl.getUniformLocation(prog, "u_col3"),
                            locInt: gl.getUniformLocation(prog, "u_intensity"),
                            locPrs: gl.getUniformLocation(prog, "u_pressure"),
                            locUnc: gl.getUniformLocation(prog, "u_unc"),
                            locMouse: gl.getUniformLocation(prog, "u_mouse")
                        };
                    }
                }
            }

            function resize() {
                const dpr = Math.min(window.devicePixelRatio || 1, 2);
                const w = window.innerWidth, h = window.innerHeight;
                glCanvas.width = uiCanvas.width = w * dpr;
                glCanvas.height = uiCanvas.height = h * dpr;
                glCanvas.style.width = uiCanvas.style.width = w + 'px';
                glCanvas.style.height = uiCanvas.style.height = h + 'px';
                ctx.setTransform(1, 0, 0, 1, 0, 0);
                ctx.scale(dpr, dpr);
                if (!window.__FORGE_NO_WEBGL) gl.viewport(0, 0, glCanvas.width, glCanvas.height);
            }
            if (!window.__FORGE_RESIZE_ATTACHED) {
                window.addEventListener('resize', resize);
                window.__FORGE_RESIZE_ATTACHED = true;
            }
            resize();

            // ═══ PARTICLES ═══
            if (!window.__FORGE_PARTS) {
                window.__FORGE_PARTS = Array.from({ length: 80 }, () => ({
                    x: Math.random() * innerWidth,
                    y: Math.random() * innerHeight,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    r: Math.random() * 1.8 + 0.4,
                    c: ['0,245,255', '191,0,255', '255,0,110', '0,255,135'][Math.floor(Math.random() * 4)],
                    life: Math.random()
                }));
            }

            // ═══ CURSOR TRACKING ═══
            if (window.__FORGE_MOUSE_X === undefined) {
                window.__FORGE_MOUSE_X = innerWidth / 2;
                window.__FORGE_MOUSE_Y = innerHeight / 2;
                window.__FORGE_RING_X = window.__FORGE_MOUSE_X;
                window.__FORGE_RING_Y = window.__FORGE_MOUSE_Y;
                window.__FORGE_PTS = [];
            }

            // 🔥 ROBUST CURSOR: use both mousemove AND pointermove for maximum compatibility
            if (!window.__FORGE_MOUSE_ATTACHED) {
                const onMove = (e) => {
                    const x = e.clientX, y = e.clientY;
                    if (x === undefined || y === undefined) return;
                    window.__FORGE_MOUSE_X = x;
                    window.__FORGE_MOUSE_Y = y;
                    dot.style.left = x + 'px';
                    dot.style.top = y + 'px';
                    window.__FORGE_PTS.push({ x, y, t: performance.now() });
                    if (window.__FORGE_PTS.length > 24) window.__FORGE_PTS.shift();
                };
                document.addEventListener('mousemove', onMove, { passive: true });
                document.addEventListener('pointermove', onMove, { passive: true });
                
                // 🔥 INTERACTIVE CURSOR STATES — hot-swap on hover over buttons/links
                const setHot = (hot) => {
                    if (hot) { dot.classList.add('cursor-hot'); ring.classList.add('cursor-hot'); }
                    else { dot.classList.remove('cursor-hot'); ring.classList.remove('cursor-hot'); }
                };
                document.addEventListener('mouseover', (e) => {
                    const t = e.target;
                    if (t.closest && t.closest('button, a, input, select, textarea, [role="button"], .meta-card, .log-entry, .glass-panel, .examples div')) {
                        setHot(true);
                    }
                }, { passive: true });
                document.addEventListener('mouseout', (e) => {
                    const t = e.target;
                    if (t.closest && t.closest('button, a, input, select, textarea, [role="button"], .meta-card, .log-entry, .glass-panel, .examples div')) {
                        setHot(false);
                    }
                }, { passive: true });
                
                window.__FORGE_MOUSE_ATTACHED = true;
            }

            if (!window.__FORGE_COLOR) {
                window.__FORGE_COLOR = {
                    c1: [0.0, 0.96, 1.0], c2: [0.75, 0.0, 1.0], c3: [1.0, 0.0, 0.43],
                    i: 1.2, u: 0.0, p: 0.0
                };
            }
            function lerp(a, b, t) { return a + (b - a) * t; }

            // ═══ MASTER ANIMATION LOOP ═══
            let lastTime = 0, lastFrameTime = performance.now(), slowFrames = 0;
            function masterLoop(ts) {
                if (!document.body.contains(uiCanvas) || !rafRunning) {
                    rafRunning = false;
                    return;
                }
                requestAnimationFrame(masterLoop);

                // Degrade gracefully if GPU is slow
                const dt = ts - lastFrameTime;
                if (dt > 100) slowFrames++; else slowFrames = Math.max(0, slowFrames - 1);
                if (slowFrames > 20) { window.__FORGE_NO_WEBGL = true; slowFrames = 0; }
                lastFrameTime = ts;

                if (ts - lastTime < 16) return;
                lastTime = ts;

                const ai = window.__FORGE_AI;
                let tC1 = [0.0, 0.96, 1.0], tC2 = [0.75, 0.0, 1.0], tC3 = [1.0, 0.0, 0.43], tI = 1.2;
                if (ai.status === 'ALERT') {
                    tC1 = [1.0, 0.0, 0.43]; tC2 = [1.0, 0.58, 0.0]; tC3 = [1.0, 0.0, 0.43]; tI = 1.6;
                } else if (ai.status === 'OPTIMAL') {
                    tC1 = [0.0, 1.0, 0.53]; tC2 = [0.0, 0.96, 1.0]; tC3 = [0.0, 1.0, 0.53]; tI = 1.5;
                } else if (ai.status === 'ACTIVE') {
                    tC1 = [0.0, 0.96, 1.0]; tC2 = [0.75, 0.0, 1.0]; tC3 = [1.0, 0.0, 0.43]; tI = 1.35;
                }

                const col = window.__FORGE_COLOR;
                for (let i = 0; i < 3; i++) {
                    col.c1[i] = lerp(col.c1[i], tC1[i], 0.04);
                    col.c2[i] = lerp(col.c2[i], tC2[i], 0.04);
                    col.c3[i] = lerp(col.c3[i], tC3[i], 0.04);
                }
                col.i = lerp(col.i, Math.min(tI, 2.5), 0.04);
                col.p = lerp(col.p, ai.pressure, 0.05);
                col.u = lerp(col.u, ai.uncertainty, 0.05);

                // Render WebGL aurora
                if (!window.__FORGE_NO_WEBGL && window.__FORGE_GL_PROG) {
                    const p = window.__FORGE_GL_PROG;
                    gl.useProgram(p.prog);
                    gl.bindBuffer(gl.ARRAY_BUFFER, p.buf);
                    gl.enableVertexAttribArray(p.posAttr);
                    gl.vertexAttribPointer(p.posAttr, 2, gl.FLOAT, false, 0, 0);
                    gl.uniform1f(p.locTime, ts * 0.001);
                    gl.uniform2f(p.locRes, glCanvas.width, glCanvas.height);
                    gl.uniform3f(p.locCol1, col.c1[0], col.c1[1], col.c1[2]);
                    gl.uniform3f(p.locCol2, col.c2[0], col.c2[1], col.c2[2]);
                    gl.uniform3f(p.locCol3, col.c3[0], col.c3[1], col.c3[2]);
                    gl.uniform1f(p.locInt, col.i);
                    gl.uniform1f(p.locPrs, col.p);
                    gl.uniform1f(p.locUnc, col.u);
                    gl.uniform2f(p.locMouse, window.__FORGE_MOUSE_X * (window.devicePixelRatio || 1),
                                              window.__FORGE_MOUSE_Y * (window.devicePixelRatio || 1));
                    gl.drawArrays(gl.TRIANGLES, 0, 6);
                }

                // 2D overlay: particles + cursor trail
                const W = window.innerWidth, H = window.innerHeight;
                ctx.clearRect(0, 0, W, H);

                // PARTICLES (pressure-reactive speed)
                const speedMul = 1.0 + col.p * 2.5;
                for (const pt of window.__FORGE_PARTS) {
                    pt.x = (pt.x + pt.vx * speedMul + W) % W;
                    pt.y = (pt.y + pt.vy * speedMul + H) % H;
                    pt.life = (pt.life + 0.004) % 1;
                    const alpha = 0.3 + 0.5 * Math.sin(pt.life * Math.PI * 2);
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(${pt.c}, ${alpha * 0.6})`;
                    ctx.shadowColor = `rgba(${pt.c}, 0.8)`;
                    ctx.shadowBlur = 8;
                    ctx.fill();
                    ctx.shadowBlur = 0;
                }

                // CURSOR RING (smooth follow)
                window.__FORGE_RING_X += (window.__FORGE_MOUSE_X - window.__FORGE_RING_X) * 0.18;
                window.__FORGE_RING_Y += (window.__FORGE_MOUSE_Y - window.__FORGE_RING_Y) * 0.18;
                ring.style.left = window.__FORGE_RING_X + 'px';
                ring.style.top = window.__FORGE_RING_Y + 'px';

                // CURSOR TRAIL (neon stroke)
                const pts = window.__FORGE_PTS;
                const now = performance.now();
                for (let i = 1; i < pts.length; i++) {
                    const age = (now - pts[i].t) / 600;
                    if (age > 1) continue;
                    const t = (1 - age) * (i / pts.length);
                    ctx.beginPath();
                    ctx.moveTo(pts[i-1].x, pts[i-1].y);
                    ctx.lineTo(pts[i].x, pts[i].y);
                    ctx.lineWidth = t * 3.5;
                    ctx.strokeStyle = `rgba(0, 245, 255, ${t * 0.55})`;
                    ctx.shadowColor = 'rgba(0, 245, 255, 0.6)';
                    ctx.shadowBlur = 6;
                    ctx.stroke();
                    ctx.shadowBlur = 0;
                }
            }
            requestAnimationFrame(masterLoop);

        } catch (err) {
            console.error("[FORGE] Engine error:", err);
            document.body.classList.remove('forge-active');
        }
    }, 500);
}
"""
