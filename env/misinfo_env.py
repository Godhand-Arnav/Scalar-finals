"""
misinfo_env.py — FORGE Gymnasium-compatible RL environment.

Observation space: Box(3859,) float32
  [0   :3840] — Sentence embeddings (up to 10 nodes × 384 dims)
  [3840:3853] — Tool usage counts (13 actions)
  [3853:3859] — Graph scalars: coverage, diversity, contradictions,
                manipulation_flag, budget_remaining, steps_ratio

Action space: Discrete(13)
  0  query_source
  1  trace_origin
  2  cross_reference
  3  request_context
  4  entity_link
  5  temporal_audit
  6  network_cluster
  7  flag_manipulation
  8  submit_verdict_real
  9  submit_verdict_misinfo
  10 submit_verdict_satire
  11 submit_verdict_out_of_context
  12 submit_verdict_fabricated
"""

from __future__ import annotations
import logging
import random
import uuid
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import gymnasium as gym
from gymnasium import spaces

import config
from env.claim_graph import ClaimGraph
from env.reward import compute_potential
from env.tasks import TASK_REGISTRY
from tools.tool_registry import SimulatedToolRegistry

logger = logging.getLogger(__name__)

# ─── Action Definitions ───────────────────────────────────────────────────────

ACTIONS: List[str] = [
    "query_source",
    "trace_origin",
    "cross_reference",
    "request_context",
    "entity_link",
    "temporal_audit",
    "network_cluster",
    "flag_manipulation",
    "submit_verdict_real",
    "submit_verdict_misinfo",
    "submit_verdict_satire",
    "submit_verdict_out_of_context",
    "submit_verdict_fabricated",
]

N_ACTIONS: int = len(ACTIONS)  # 13

# Observation layout constants
_EMBED_DIM = config.CLAIM_EMBED_DIM          # 384
_MAX_NODES = config.MAX_OBSERVATION_NODES    # 10
_OBS_DIM = _EMBED_DIM * _MAX_NODES + N_ACTIONS + 6  # 3859

# Verdict action prefix
_VERDICT_PREFIX = "submit_verdict_"

# Label extracted from a verdict action name
def _label_from_action(action: str) -> str:
    return action.replace(_VERDICT_PREFIX, "")


# ─── Environment ──────────────────────────────────────────────────────────────

class MisInfoForensicsEnv(gym.Env):
    """
    FORGE Forensic RL Environment (Gymnasium API).

    Parameters
    ----------
    task_names      : Restrict episodes to these tasks. None = all tasks.
    difficulty      : 1-4.
    budget_multiplier: scales max_steps relative to base.
    use_live_tools  : If True, use real API calls; else use SimulatedToolRegistry.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        task_names: Optional[List[str]] = None,
        difficulty: int = 1,
        budget_multiplier: float = 1.0,
        use_live_tools: bool = False,
    ):
        super().__init__()
        self.task_names = task_names or list(TASK_REGISTRY.keys())
        self.difficulty = difficulty
        self.budget_multiplier = budget_multiplier

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(_OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(N_ACTIONS)

        # Tool registry (simulated by default for training)
        self._tool_registry = SimulatedToolRegistry()

        # Episode state (populated on reset)
        self.graph: Optional[ClaimGraph] = None
        self.current_task = None
        self.steps: int = 0
        self.max_steps: int = config.BASE_EPISODE_STEPS
        self.manipulation_flagged: bool = False
        self._tool_history: np.ndarray = np.zeros(N_ACTIONS, dtype=np.float32)
        self._episode_id: str = ""
        self._seed: Optional[int] = None
        self._prev_potential: float = 0.0
        self._task_name: str = ""

        # Sentence embedder (lazy init to avoid startup cost)
        self._embedder = None

    # ── Sentence embedding ────────────────────────────────────────────────────

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(config.HF_EMBEDDING_MODEL)
                logger.info("Sentence embedder loaded: %s", config.HF_EMBEDDING_MODEL)
            except Exception as e:
                logger.warning("Could not load sentence embedder: %s", e)
                self._embedder = None
        return self._embedder

    def _embed_text(self, text: str) -> np.ndarray:
        embedder = self._get_embedder()
        if embedder is None:
            return np.zeros(_EMBED_DIM, dtype=np.float32)
        try:
            vec = embedder.encode(text, convert_to_numpy=True, show_progress_bar=False)
            return vec.astype(np.float32)
        except Exception:
            return np.zeros(_EMBED_DIM, dtype=np.float32)

    # ── Observation builder ───────────────────────────────────────────────────

    def _build_observation(self) -> np.ndarray:
        obs = np.zeros(_OBS_DIM, dtype=np.float32)

        if self.graph:
            # Embed up to _MAX_NODES retrieved nodes
            retrieved = [n for n in self.graph.nodes.values() if n.retrieved]
            # Always include root first
            root = self.graph.root
            if root and root not in retrieved:
                retrieved = [root] + retrieved
            retrieved = retrieved[:_MAX_NODES]

            for i, node in enumerate(retrieved):
                if node.embedding is not None:
                    emb = np.asarray(node.embedding, dtype=np.float32)
                else:
                    emb = self._embed_text(node.text)
                    node.embedding = emb
                start = i * _EMBED_DIM
                obs[start: start + _EMBED_DIM] = emb[:_EMBED_DIM]

        # Tool history
        obs[_EMBED_DIM * _MAX_NODES: _EMBED_DIM * _MAX_NODES + N_ACTIONS] = self._tool_history

        # Graph scalars
        scalar_start = _EMBED_DIM * _MAX_NODES + N_ACTIONS
        if self.graph:
            obs[scalar_start + 0] = float(self.graph.evidence_coverage)
            obs[scalar_start + 1] = float(self.graph.source_diversity_entropy)
            obs[scalar_start + 2] = float(min(self.graph.contradiction_surface_area, 5) / 5.0)
            obs[scalar_start + 3] = float(self.manipulation_flagged)
            obs[scalar_start + 4] = float(max(0.0, (self.max_steps - self.steps) / max(self.max_steps, 1)))
            obs[scalar_start + 5] = float(self.steps / max(self.max_steps, 1))

        return obs

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self._seed = seed if seed is not None else random.randint(0, 2**31)
        rng = random.Random(self._seed)

        # Pick a task
        self._task_name = rng.choice(self.task_names)
        task_class = TASK_REGISTRY[self._task_name]
        self.current_task = task_class()

        # Generate the graph
        self.graph = self.current_task.generate(
            difficulty=self.difficulty,
            seed=self._seed,
        )

        # Compute max_steps from config + budget_multiplier
        n_extra_tactics = max(0, len(self.graph.applied_tactics) - 1)
        self.max_steps = int(
            (config.BASE_EPISODE_STEPS + n_extra_tactics * config.STEP_COMPLEXITY_BONUS)
            * self.budget_multiplier
        )
        self.max_steps = max(self.max_steps, config.BASE_EPISODE_STEPS)

        self.steps = 0
        self.manipulation_flagged = False
        self._tool_history = np.zeros(N_ACTIONS, dtype=np.float32)
        self._episode_id = str(uuid.uuid4())
        self._prev_potential = compute_potential(self.graph)

        obs = self._build_observation()
        info = {
            "episode_id": self._episode_id,
            "task_id": self._task_name,
            "true_label": self.graph.true_label,
            "max_steps": self.max_steps,
            "difficulty": self.difficulty,
        }
        logger.debug("Reset: task=%s difficulty=%d max_steps=%d", self._task_name, self.difficulty, self.max_steps)
        return obs, info

    # ── Step ──────────────────────────────────────────────────────────────────

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        assert self.graph is not None, "Call reset() before step()"
        assert 0 <= action < N_ACTIONS, f"Invalid action {action}"

        self.steps += 1
        action_name = ACTIONS[action]
        self._tool_history[action] += 1.0

        terminated = False
        truncated = False
        tool_result: Dict[str, Any] = {}
        verdict: Optional[str] = None

        # ── Handle verdict actions ─────────────────────────────────────────────
        if action_name.startswith(_VERDICT_PREFIX):
            verdict = _label_from_action(action_name)
            terminated = True
            tool_result = {"verdict": verdict, "summary": f"Submitted verdict: {verdict}"}
        elif action_name == "flag_manipulation":
            self.manipulation_flagged = True
            tool_result = self._tool_registry.call("flag_manipulation", self.graph)
        else:
            # Investigative tool
            tool_result = self._tool_registry.call(action_name, self.graph)

        # ── Reward shaping ────────────────────────────────────────────────────
        curr_potential = compute_potential(self.graph)
        shaped_bonus = config.PPO_GAMMA * curr_potential - self._prev_potential
        self._prev_potential = curr_potential

        step_penalty = config.REWARD_STEP_PENALTY

        # Duplicate tool penalty
        dup_penalty = (
            config.REWARD_DUPLICATE_TOOL_PENALTY
            if self._tool_history[action] > 1 and not action_name.startswith(_VERDICT_PREFIX)
            else 0.0
        )

        if terminated:
            # Terminal reward
            correct = (verdict == self.graph.true_label)
            base = (
                config.REWARD_CORRECT_VERDICT if correct
                else config.REWARD_WRONG_VERDICT
            )
            # False positive penalty: flagged a real claim as misinfo
            fp_penalty = 0.0
            if self.graph.true_label == "real" and verdict in ("misinfo", "fabricated"):
                fp_penalty = config.REWARD_FALSE_POSITIVE
            # Manipulation bonus/penalty
            manip_bonus = 0.0
            if self.manipulation_flagged:
                true_manip = bool(self.graph.applied_tactics)
                manip_bonus = (
                    config.REWARD_MANIPULATION_FLAG if true_manip
                    else config.REWARD_MANIPULATION_PENALTY
                )
            reward = base + fp_penalty + manip_bonus + shaped_bonus
        else:
            reward = step_penalty + dup_penalty + shaped_bonus

        # Clip reward to (REWARD_CLIP_MIN, REWARD_CLIP_MAX) per config (default 0.001–0.999)
        reward = float(np.clip(reward, config.REWARD_CLIP_MIN, config.REWARD_CLIP_MAX))

        # Truncation: out of budget
        if not terminated and self.steps >= self.max_steps:
            truncated = True

        obs = self._build_observation()
        info: Dict[str, Any] = {
            "action": action_name,
            "tool_result": tool_result,
            "steps": self.steps,
            "max_steps": self.max_steps,
            "coverage": self.graph.evidence_coverage,
            "contradictions": self.graph.contradiction_surface_area,
            "manipulation_flagged": self.manipulation_flagged,
        }
        if verdict:
            info["verdict"] = verdict
            info["correct"] = verdict == self.graph.true_label

        return obs, reward, terminated, truncated, info

    # ── Utility ───────────────────────────────────────────────────────────────

    def _estimate_confidence(self) -> float:
        """Heuristic confidence estimate based on graph coverage and contradictions."""
        if not self.graph:
            return 0.0
        cov = self.graph.evidence_coverage
        contra_norm = min(self.graph.contradiction_surface_area, 5) / 5.0
        return float(np.clip(cov * (1.0 - contra_norm * 0.3), 0.0, 1.0))

    def get_episode_summary(self) -> Dict[str, Any]:
        return {
            "episode_id": self._episode_id,
            "task_id": self._task_name,
            "steps": self.steps,
            "max_steps": self.max_steps,
            "difficulty": self.difficulty,
            "manipulation_flagged": self.manipulation_flagged,
            "evidence_coverage": self.graph.evidence_coverage if self.graph else 0.0,
            "true_label": self.graph.true_label if self.graph else "unknown",
        }

    @staticmethod
    def parse_observation(obs: np.ndarray) -> Dict[str, Any]:
        """Parse a flat observation vector into named components."""
        embed_end = _EMBED_DIM * _MAX_NODES        # 3840
        hist_end = embed_end + N_ACTIONS           # 3853
        tool_history = obs[embed_end:hist_end]
        scalars = obs[hist_end:]                   # 6 values
        return {
            "tool_history": tool_history,
            "evidence_coverage": float(scalars[0]) if len(scalars) > 0 else 0.0,
            "source_diversity": float(scalars[1]) if len(scalars) > 1 else 0.0,
            "contradiction_norm": float(scalars[2]) if len(scalars) > 2 else 0.0,
            "manipulation_flagged": bool(scalars[3] > 0.5) if len(scalars) > 3 else False,
            "budget_remaining": float(scalars[4]) if len(scalars) > 4 else 1.0,
            "steps_ratio": float(scalars[5]) if len(scalars) > 5 else 0.0,
        }

    def close(self) -> None:
        if hasattr(self._tool_registry, "close"):
            try:
                self._tool_registry.close()
            except Exception:
                pass
        self.graph = None
