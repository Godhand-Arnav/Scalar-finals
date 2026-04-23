# app.py — FORGE Autonomous Engine (V4.2 — Aurora + Neon + Patched)
# CHANGES: FTS5 sanitization, auto-btn state fix, semantic event rename,
#          enhanced aurora shader, neon glows, robust cursor system

import gradio as gr
import time
import random
import re
import html as html_lib
import traceback
import logging
import threading 
import math 
import asyncio
import json
from frontend.constants import *
from frontend.components import (
    _s, _ai_state_html, _topnav, _statusbar_html, _left_idle, _left_active,
    _center_idle, _center_active, _right_idle, _right_active, _right_done, _graph_text
)
import os
import sqlite3
import atexit
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# ─── Environment & Agent Imports ──────────────────────────────────────────────
import config
from env.misinfo_env import MisInfoForensicsEnv, ACTIONS
from agents.llm_agent import LLMAgent
from env.tasks import TASK_REGISTRY

# ─── FORGE-MA Pre-trained checkpoints ─────────────────────────────────────────
try:
    from pretrain import load_checkpoints as _load_ckpts, checkpoints_exist as _ckpts_exist
    _PRETRAIN_AVAILABLE = True
except Exception:
    _PRETRAIN_AVAILABLE = False

# ─── Constants & Config ───────────────────────────────────────────────────────
DB_PATH = "forge_memory.db"
POLICY_PATH = "forge_policy.json"
AGENT_STEP_BACKSTOP = 200
MAX_TIME_SEC = 180
MAX_AUTO_CYCLES = 50


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
_app_logger = logging.getLogger("forge.enterprise")

# ══════════════════════════════════════════════════════════════════════════════
# 1. OBSERVABILITY
# ══════════════════════════════════════════════════════════════════════════════
class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.latencies = []; self.errors = 0; self.total_runs = 0
    def record_latency(self, ms):
        with self._lock:
            self.latencies.append(ms)
            if len(self.latencies) > 1000: self.latencies.pop(0)
    def record_error(self):
        with self._lock: self.errors += 1
    def record_run(self):
        with self._lock: self.total_runs += 1
    def get_stats(self):
        with self._lock:
            if not self.latencies: return {"p50": 0, "p99": 0, "errors": self.errors, "runs": self.total_runs}
            s = sorted(self.latencies)
            return {"p50": s[int(len(s) * 0.50)], "p99": s[int(len(s) * 0.99)], "errors": self.errors, "runs": self.total_runs}

FORGE_METRICS = Metrics()

# ══════════════════════════════════════════════════════════════════════════════
# 2. PERSISTENCE (SQLite FTS5) — PATCHED: Input sanitization
# ══════════════════════════════════════════════════════════════════════════════
# 🔥 PATCH #3: FTS5 special chars can break MATCH queries
_FTS5_SAFE = re.compile(r'[^a-zA-Z0-9_]')
def _sanitize_fts5(s: str) -> str:
    """Strip FTS5 special chars (", *, :, -, (, ), etc.)"""
    return _FTS5_SAFE.sub('', str(s))[:64]

class ForgeDB:
    def __init__(self, path=DB_PATH):
        self.path = path
        self._local = threading.local()
        self._init_db()
    @contextmanager
    def get_conn(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        try: yield self._local.conn
        except Exception as e: _app_logger.error(f"DB Error: {e}"); raise
    def _init_db(self):
        with self.get_conn() as conn:
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS exp_memory USING fts5(task, claim, actions, reward, correct)")
            conn.commit()
    async def store(self, task, claim, actions, reward, correct):
        def _w():
            with self.get_conn() as conn:
                conn.execute(
                    "INSERT INTO exp_memory (task, claim, actions, reward, correct) VALUES (?, ?, ?, ?, ?)",
                    (task, claim, json.dumps(actions), reward, int(correct))
                )
                conn.commit()
        await asyncio.get_running_loop().run_in_executor(None, _w)
    async def search_similar(self, task, limit=2):
        def _r():
            safe_task = _sanitize_fts5(task)
            if not safe_task: return []
            query = f'task:{safe_task} AND correct:1'
            try:
                with self.get_conn() as conn:
                    return [dict(r) for r in conn.execute(
                        "SELECT task, actions, reward FROM exp_memory WHERE exp_memory MATCH ? ORDER BY rank LIMIT ?",
                        (query, limit)
                    ).fetchall()]
            except sqlite3.OperationalError as e:
                _app_logger.warning(f"FTS5 query failed: {e}")
                return []
        return await asyncio.get_running_loop().run_in_executor(None, _r)

FORGE_DB = ForgeDB()

# ══════════════════════════════════════════════════════════════════════════════
# 3. RL POLICY
# ══════════════════════════════════════════════════════════════════════════════
class RLPolicy:
    def __init__(self, path=POLICY_PATH):
        self.path = path; self._lock = threading.Lock()
        self.weights = {v: 1.0 for v in ACTIONS}
        self.alpha = 0.1; self.epsilon = 0.15; self._load()
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    self.weights.update(data.get("weights", {}))
                    self.epsilon = data.get("epsilon", 0.15)
            except: pass
    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump({"weights": self.weights, "epsilon": self.epsilon}, f, indent=2)
        except Exception as e: _app_logger.error(f"Policy save failed: {e}")
    def update(self, actions_taken, reward):
        if math.isnan(reward): reward = 0.0
        with self._lock:
            for act in set(actions_taken):
                if act in self.weights:
                    self.weights[act] = (1 - self.alpha) * self.weights[act] + self.alpha * reward
            total = sum(abs(v) for v in self.weights.values()) + 1e-6
            for k in self.weights: self.weights[k] /= total
            self.epsilon = max(0.05, self.epsilon * 0.995)
            self.save()
    def get_biases(self):
        with self._lock: return dict(self.weights)

FORGE_POLICY = RLPolicy()

# ══════════════════════════════════════════════════════════════════════════════
# 4. CONCURRENCY & SECURITY — PATCHED: Semantic rename
# ══════════════════════════════════════════════════════════════════════════════
_LLM_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="llm_worker")
@atexit.register
def shutdown_executor():
    try: _LLM_EXECUTOR.shutdown(wait=False)
    except: pass

class AutonomousCore:
    def __init__(self):
        # 🔥 PATCH #5: Renamed for clarity. running_event.is_set() == "is running"
        self.running_event = threading.Event()
        self.active_run_id = None

FORGE_CORE = AutonomousCore()

# ─── Load pre-trained HAE / GIN weights at startup ────────────────────────────
def _startup_load_checkpoints():
    """Background thread: restore HAE + GIN weights from checkpoints/ if available."""
    if not _PRETRAIN_AVAILABLE:
        return
    try:
        from env.forge_env import ForgeEnv, ForgeEnvConfig
        _probe_env = ForgeEnv(ForgeEnvConfig(budget=10, seed=0))
        ok = _load_ckpts(_probe_env)
        if ok:
            _app_logger.info("[startup] HAE/GIN checkpoints loaded successfully.")
        else:
            _app_logger.info("[startup] No checkpoints found — running with init weights.")
    except Exception as exc:
        _app_logger.warning("[startup] Checkpoint load failed: %s", exc)

threading.Thread(target=_startup_load_checkpoints, daemon=True, name="ckpt_loader").start()

@contextmanager
def safe_run_slot():
    global ACTIVE_RUNS
    with ACTIVE_LOCK:
        if ACTIVE_RUNS >= MAX_ACTIVE_RUNS:
            raise gr.Error("System busy. Try again later.")
        ACTIVE_RUNS += 1
    try: yield
    finally:
        with ACTIVE_LOCK: ACTIVE_RUNS -= 1

def rate_limit(user="global"):
    now = time.time()
    if user in LAST_CALL and now - LAST_CALL[user] < 1:
        raise gr.Error("Too many requests. Slow down.")
    LAST_CALL[user] = now

def validate_inputs(task_name: str, difficulty: str):
    if not task_name or not isinstance(task_name, str): raise gr.Error("Task name cannot be empty.")
    if len(task_name) > 60: raise gr.Error("Input too large.")
    if not re.match(r"^[a-zA-Z0-9_\s\(\)\-]+$", task_name): raise gr.Error("Invalid characters.")
    try:
        diff = int(difficulty)
        if diff < 1 or diff > 4: raise ValueError()
    except (ValueError, TypeError): raise gr.Error("Difficulty must be 1-4.")
    return True

async def _safe_act_async(agent, obs, context):
    loop = asyncio.get_running_loop()
    try:
        action = await asyncio.wait_for(
            loop.run_in_executor(_LLM_EXECUTOR, agent.act, obs, context),
            timeout=LLM_TIMEOUT
        )
    except asyncio.TimeoutError:
        _app_logger.warning("LLM timeout"); action = 0
    except Exception as e:
        _app_logger.error(f"LLM error: {e}"); FORGE_METRICS.record_error()
        action = 0
    if not (isinstance(action, int) and 0 <= action < len(ACTIONS)): action = 0
    return action

# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS — ENHANCED AURORA, NEON, CURSOR
# ══════════════════════════════════════════════════════════════════════════════
from frontend.theme import FORGE_CSS

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM JS — ENHANCED AURORA SHADER + ROBUST CURSOR
# ══════════════════════════════════════════════════════════════════════════════
from frontend.theme import FORGE_JS

# ══════════════════════════════════════════════════════════════════════════════
# CORE INVESTIGATION LOOP
# ══════════════════════════════════════════════════════════════════════════════
async def _investigate_async(task_name: str, difficulty: int, auto_mode: bool = False):
    env = None; t_start = time.time()
    try:
        validate_inputs(task_name, str(difficulty))
        agent = LLMAgent()
        if hasattr(agent, "action_biases"): agent.action_biases = FORGE_POLICY.get_biases()
        env = (MisInfoForensicsEnv(task_names=[task_name], difficulty=difficulty)
               if task_name != "All Tasks (Random)"
               else MisInfoForensicsEnv(difficulty=difficulty))
        obs, info = env.reset(seed=random.randint(0, 2**31 - 1))
        if hasattr(agent, "reset"): agent.reset()
        if not getattr(env, "graph", None): raise ValueError("Graph init failed")
        
        claim = getattr(env.graph.root, 'text', "")
        task_id = info.get("task_id", "unknown")
        dom = getattr(env.graph.root, 'domain', "unknown")
        vir = getattr(env.graph.root, 'virality_score', 0.5)
        max_steps = getattr(env, "max_steps", AGENT_STEP_BACKSTOP)
        logs, actions_taken = [], []
        def _ts(): return f"{int((time.time()-t_start)//60):02d}:{int((time.time()-t_start)%60):02d}"
        past_cases = await FORGE_DB.search_similar(task_id)
        if past_cases: logs.append((_ts(), f"Retrieved {len(past_cases)} DB cases", "cross_reference"))
        logs.append((_ts(), f'Task init: {str(task_id).replace("_", " ").title()}', "query_source"))

        # 🔥 PATCH #4: auto_btn shows "Stop" semantics during autonomous run
        auto_btn_label = "⏹  Stop Autonomous" if auto_mode else "♾️ Autonomous Mode"

        yield (_left_active(logs),
               _center_active(claim, task_id, vir, dom, "Waking API…"),
               _right_idle(),
               _statusbar_html("ACTIVE", f"{random.uniform(0.8, 2.0):.1f}K/S"),
               gr.update(interactive=not auto_mode),
               gr.update(value=auto_btn_label, interactive=True),
               _graph_text(env, FORGE_METRICS.get_stats()),
               _ai_state_html("ACTIVE"),
               _topnav(auto_mode))

        done, step_count, last_ui = False, 0, 0.0
        cov, div, con, bud, prs, unc = 0.0, 0.0, 0, 1.0, 0.0, 0.0
        step_info, final_reward, last = {}, 0.0, {}

        while not done and env.steps < max_steps and step_count < AGENT_STEP_BACKSTOP:
            if auto_mode and not FORGE_CORE.running_event.is_set(): break
            if time.time() - t_start > MAX_TIME_SEC: break
            step_count += 1
            prs = step_count / max(max_steps, 1)
            context = {
                "steps": env.steps, "max_steps": max_steps,
                "coverage": cov, "contradictions": con,
                "last_tool_result": step_info.get("tool_result"),
                "claim_text": claim, "task_name": task_id,
                "past_cases": past_cases
            }
            try:
                act_t0 = time.time()
                action = await _safe_act_async(agent, obs, context)
                FORGE_METRICS.record_latency((time.time() - act_t0) * 1000)
                action_name = ACTIONS[action] if (isinstance(action, int) and 0 <= action < len(ACTIONS)) else str(action)
                actions_taken.append(action_name)
                res = env.step(action)
                if len(res) == 5: obs, reward, terminated, truncated, step_info = res
                else: raise ValueError("Bad step output")
                done = terminated or truncated
                final_reward = reward if reward is not None and not math.isnan(reward) else 0.0
            except Exception as e:
                _app_logger.error(f"Step err: {e}"); FORGE_METRICS.record_error(); break

            if env.graph:
                cov = getattr(env.graph, 'evidence_coverage', 0.0)
                div = getattr(env.graph, 'source_diversity_entropy', 0.0)
                con = getattr(env.graph, 'contradiction_surface_area', 0)
            bud = max(0.0, (max_steps - env.steps) / max(max_steps, 1))
            if hasattr(agent, "reasoning_log") and agent.reasoning_log:
                last = agent.reasoning_log[-1]
                unc = min(1.0, len(str(last.get("think", ""))) / 1000.0)
            tool_summary = (step_info.get("tool_result", {}).get("summary", f"R:{final_reward:+.2f}")
                            if isinstance(step_info.get("tool_result"), dict)
                            else f"R:{final_reward:+.2f}")
            logs.append((_ts(), str(tool_summary)[:80], action_name))
            logs = logs[-50:]
            actions_taken = actions_taken[-200:]
            
            now = time.time()
            if (now - last_ui >= THROTTLE_INTERVAL) or done:
                yield (_left_active(logs[-LOG_DISPLAY_COUNT:]),
                       _center_active(claim, task_id, vir, dom, "Analysing…", cov, div, bud),
                       _right_active(last.get("think",""), last.get("predict",""),
                                     getattr(agent,"_fsm_state",""), env.steps, max_steps, cov, con),
                       _statusbar_html("ACTIVE", f"{random.uniform(1,3.5):.1f}K/S"),
                       gr.update(interactive=not auto_mode),
                       gr.update(value=auto_btn_label, interactive=True),
                       _graph_text(env, FORGE_METRICS.get_stats()),
                       _ai_state_html("ACTIVE", cov, con, unc, prs),
                       _topnav(auto_mode))
                last_ui = now

        true_label = getattr(env.graph, 'true_label', "unknown") if env.graph else "unknown"
        verdict = step_info.get("verdict")
        correct = (verdict == true_label)
        conf = env._estimate_confidence() if hasattr(env, "_estimate_confidence") else cov
        if not conf or math.isnan(conf): conf = 0.0
        await FORGE_DB.store(task_id, claim, actions_taken, final_reward, correct)
        FORGE_POLICY.update(actions_taken, final_reward)
        FORGE_METRICS.record_run()

        ep_out = step_info.get("episode_output")
        if ep_out:
            try:
                from env.oversight_report import generate_oversight_report, generate_stix2_bundle
                os.makedirs("graphify-out", exist_ok=True)

                # ── Markdown forensic report ──────────────────────────────────
                report_md = generate_oversight_report(ep_out, claim_text=claim)
                with open("graphify-out/GRAPH_REPORT.md", "w", encoding="utf-8") as f:
                    f.write(report_md)

                # ── STIX 2.1 bundle (machine-readable, Fleet AI prize) ────────
                stix_json = generate_stix2_bundle(
                    ep_out,
                    campaign_name=f"FORGE-MA | {task_id}",
                    claim_text=claim,
                )
                with open("graphify-out/STIX_BUNDLE.json", "w", encoding="utf-8") as f:
                    f.write(stix_json)

                _app_logger.info(
                    "[graphify] Reports written: GRAPH_REPORT.md + STIX_BUNDLE.json"
                )
            except Exception as e:
                _app_logger.error(f"Failed to generate oversight report: {e}")


        yield (_left_active(logs[-LOG_DISPLAY_COUNT:]),
               _center_active(claim, task_id, vir, dom, "FINAL", cov, div, 0),
               _right_done(verdict, true_label, correct, env.steps, final_reward, conf),
               _statusbar_html("OPTIMAL" if correct else "ALERT"),
               gr.update(interactive=True),
               gr.update(value="♾️ Autonomous Mode" if not auto_mode else auto_btn_label, interactive=True),
               _graph_text(env, FORGE_METRICS.get_stats()),
               _ai_state_html("OPTIMAL" if correct else "ALERT", cov, con),
               _topnav(auto_mode))
    except gr.Error: raise
    except Exception as e:
        _app_logger.error(f"CRASH: {traceback.format_exc()}"); FORGE_METRICS.record_error()
        yield (_left_idle(),
               _center_active("SYSTEM FAILURE", "err", 0, "err", "ERROR"),
               _right_idle(),
               _statusbar_html("ERROR"),
               gr.update(interactive=True),
               gr.update(value="♾️ Autonomous Mode", interactive=True),
               f"Error: {str(e)}",
               _ai_state_html("ALERT"),
               _topnav(auto_mode))
    finally:
        if env and hasattr(env, "close"):
            try: env.close()
            except: pass

async def investigate_manual(task_name: str, difficulty: str):
    rate_limit()
    with safe_run_slot():
        FORGE_CORE.running_event.clear()
        async for state in _investigate_async(task_name, int(difficulty), False):
            yield state

async def toggle_autonomous():
    # 🔥 PATCH #5: Semantic clarity — running_event.is_set() == "currently running"
    if FORGE_CORE.running_event.is_set():
        FORGE_CORE.running_event.clear()  # Signal stop
        yield (_left_idle(), _center_idle(), _right_idle(),
               _statusbar_html("IDLE"),
               gr.update(interactive=True),
               gr.update(value="♾️ Autonomous Mode", interactive=True),
               _graph_text(None, FORGE_METRICS.get_stats()),
               _ai_state_html("IDLE"),
               _topnav(False))
        return

    FORGE_CORE.running_event.set()  # Signal start
    run_id = random.random()
    FORGE_CORE.active_run_id = run_id
    cycles = 0
    while FORGE_CORE.running_event.is_set() and FORGE_CORE.active_run_id == run_id:
        cycles += 1
        if cycles > MAX_AUTO_CYCLES: break
        try:
            task = random.choice(list(TASK_REGISTRY.keys()))
            async for state in _investigate_async(task, random.randint(1, 4), True):
                if not FORGE_CORE.running_event.is_set(): break
                yield state
        except Exception as e:
            _app_logger.error(f"[AUTO ERROR] {e}"); FORGE_METRICS.record_error()
        await asyncio.sleep(random.uniform(1.0, 2.5))

    # Loop ended naturally or via stop — reset UI
    FORGE_CORE.running_event.clear()
    yield (_left_idle(), _center_idle(), _right_idle(),
           _statusbar_html("IDLE"),
           gr.update(interactive=True),
           gr.update(value="♾️ Autonomous Mode", interactive=True),
           _graph_text(None, FORGE_METRICS.get_stats()),
           _ai_state_html("IDLE"),
           _topnav(False))

# ══════════════════════════════════════════════════════════════════════════════
# GRADIO APP
# ══════════════════════════════════════════════════════════════════════════════
EXAMPLES = [
    ["fabricated_stats", 1], ["satire_news", 1],
    ["coordinated_campaign", 2], ["sec_fraud", 2],
    ["image_forensics", 3]
]

with gr.Blocks(
    title="FORGE Enterprise V4.2"
) as demo:
    
    topnav = gr.HTML(_topnav(False))
    ai_state = gr.HTML(value=_ai_state_html("IDLE"), elem_id="ai-state-wrapper")

    with gr.Row():
        with gr.Column(scale=3, elem_classes=["glass-panel"]):
            left_panel = gr.HTML(_left_idle())
        with gr.Column(scale=7, elem_classes=["aurora-wrap"]):
            with gr.Column(elem_classes=["glass-panel"]):
                center_panel = gr.HTML(_center_idle())
            with gr.Column(elem_classes=["controls-panel"]):
                with gr.Row():
                    with gr.Column(scale=7):
                        task_dd = gr.Dropdown(
                            choices=["All Tasks (Random)"] + list(TASK_META.keys()),
                            value="All Tasks (Random)", label="Investigation Protocol",
                            elem_id="task_dd"
                        )
                    with gr.Column(scale=3):
                        diff_sl = gr.Slider(minimum=1, maximum=4, step=1, value=1, label="Depth Level")
                with gr.Row():
                    start_btn = gr.Button("▶  Launch Deep Analysis", variant="primary", scale=2)
                    auto_btn = gr.Button("♾️ Autonomous Mode", variant="secondary", scale=1)
                    stop_btn = gr.Button("⏹ Force Stop", variant="stop", scale=1)
                gr.Examples(examples=EXAMPLE_CLAIMS, inputs=[task_dd, diff_sl],
                            label="⚡ Investigation Presets — Quick start")
                statusbar = gr.HTML(_statusbar_html("IDLE"))
        with gr.Column(scale=3, elem_classes=["glass-panel"]):
            right_panel = gr.HTML(_right_idle())

    graph_box = gr.Textbox(
        label="Evidence Graph & Core State",
        lines=6, interactive=False,
        placeholder="Run an investigation to see live graph statistics…"
    )

    outputs = [left_panel, center_panel, right_panel, statusbar,
               start_btn, auto_btn, graph_box, ai_state, topnav]
    start_btn.click(fn=investigate_manual, inputs=[task_dd, diff_sl], outputs=outputs)
    auto_btn.click(fn=toggle_autonomous, inputs=[], outputs=outputs)
    stop_btn.click(fn=lambda: FORGE_CORE.running_event.clear(), inputs=[], outputs=[], queue=False)

if __name__ == "__main__":
    demo.queue(api_open=False, default_concurrency_limit=10).launch(
        server_name="0.0.0.0", server_port=7860,
        theme=gr.themes.Base(
            primary_hue="blue", secondary_hue="purple", neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter")
        ).set(
            body_background_fill="transparent",
            block_background_fill="transparent",
            block_border_width="0px",
            input_background_fill="rgba(0,0,0,0.4)",
            input_border_color="rgba(255,255,255,0.12)"
        ),
        css=FORGE_CSS, js=FORGE_JS
    )