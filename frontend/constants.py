"""
frontend/constants.py — Shared UI constants for FORGE Enterprise.
Extracted from app.py to keep the main app file small and focused.
"""
import threading

# ── Runtime limits ─────────────────────────────────────────────────────────────
AGENT_STEP_BACKSTOP   = 200
MAX_TIME_SEC          = 180
MAX_AUTO_CYCLES       = 50
THROTTLE_INTERVAL     = 0.35
LOG_DISPLAY_COUNT     = 12
LLM_TIMEOUT           = 20
MAX_AGENT_FAILURES    = 3
MAX_ACTIVE_RUNS       = 5

# ── Shared mutable state ───────────────────────────────────────────────────────
ACTIVE_RUNS  = 0
ACTIVE_LOCK  = threading.Lock()
LAST_CALL: dict = {}

# ── Task metadata ──────────────────────────────────────────────────────────────
TASK_META = {
    "fabricated_stats":     {"icon": "📊", "code": "FAB_STAT"},
    "out_of_context":       {"icon": "🎬", "code": "OOC_STRIP"},
    "coordinated_campaign": {"icon": "🤖", "code": "BOT_CAMP"},
    "satire_news":          {"icon": "😄", "code": "SAT_PARSE"},
    "verified_fact":        {"icon": "✓",  "code": "VER_FACT"},
    "politifact_liar":      {"icon": "🔍", "code": "POL_LIAR"},
    "image_forensics":      {"icon": "📸", "code": "IMG_FRNSC"},
    "sec_fraud":            {"icon": "⚠️", "code": "SEC_FRAUD"},
}

# Representative claim text per R1 task — surfaced in FORGE-MA tab
TASK_TO_CLAIM: dict[str, str] = {
    "fabricated_stats":     "Fabricated statistics: study claims 90% efficacy — journal retracted, still circulating.",
    "out_of_context":       "Video shows 2015 protest mislabelled as 2024 riots.",
    "coordinated_campaign": "Bot network amplified fake election-fraud claim across 50k accounts.",
    "satire_news":          "Politician quoted saying 'immigrants are criminals' — source: satirical site.",
    "verified_fact":        "WHO confirms standard childhood vaccine schedule is safe and effective.",
    "politifact_liar":      "Politician's statement rated 'False' by PolitiFact — claim circulating without context.",
    "image_forensics":      "Scientist replaced with lookalike in doctored photo shared virally.",
    "sec_fraud":            "Company's SEC filing shows fabricated revenue figures still cited in media.",
}

EXAMPLE_CLAIMS = [[k, 1] for k in list(TASK_META.keys())[:5]]

# ── Action display maps ────────────────────────────────────────────────────────
ACTION_ICONS = {
    "query_source": "🔎", "trace_origin": "🔗", "cross_reference": "📍",
    "request_context": "📝", "entity_link": "🏷️", "temporal_audit": "⏰",
    "network_cluster": "🕸️", "flag_manipulation": "🚩",
    "submit_verdict_real": "✓", "submit_verdict_misinfo": "✗",
    "submit_verdict_satire": "😄", "submit_verdict_out_of_context": "🎬",
    "submit_verdict_fabricated": "📊",
}

ACTION_COLORS = {k: "#00f5ff" for k in ACTION_ICONS}
ACTION_COLORS.update({
    "flag_manipulation":   "#ff006e",
    "submit_verdict_real": "#00ff87",
    "submit_verdict_misinfo": "#ff006e",
})

EXAMPLES = [
    ["fabricated_stats", 1], ["satire_news", 1],
    ["coordinated_campaign", 2], ["sec_fraud", 2],
    ["image_forensics", 3],
]
