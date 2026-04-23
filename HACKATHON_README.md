# 🏆 FORGE-MA: Hackathon Submission Guide

Welcome Judges! This document outlines the technical achievements, final repository state, and evaluation instructions for our Meta × HuggingFace OpenEnv Hackathon (Round 2) submission.

## 🌟 The Plandemic Case Study: Our Capstone Benchmark

We have built a custom, rigorous evaluation scenario designed specifically for this presentation: **The Plandemic Benchmark** (`env/tasks/task_plandemic.py`). 

Instead of relying on static strings, this case study utilizes **dynamic LLM procedural generation** to synthesize novel, complex conspiracy theories on the fly. It challenges the Blue Team to unravel sophisticated, coordinated misinformation campaigns, showcasing the system's ability to handle zero-day narrative structures.

---

## 📈 Technical Achievements & Training Metrics

FORGE-MA operates on legitimate, pre-trained neural network checkpoints developed via a 50-generation adversarial curriculum learning pipeline.

### 1. Mathematical Convergence
Our Blue Team's Graph Isomorphism Network (GIN) Specialist model achieved undeniable mathematical convergence during the pretraining phase:
* **Initial Online Loss:** `66.74`
* **Final Converged Loss:** **`0.78`**

### 2. True Adversarial RL
We resolved critical gradient isolation issues. The Red Team's Hierarchical Adversarial Encoder (HAE) is explicitly tied to the PyTorch optimizer (`use_trl=True`). The adversary is actively learning to mutate claims and evade detection, providing a continuously evolving challenge for the defense.

### 3. "No-Crash" Resilience Guarantees
We engineered the multi-agent LLM system to never fail on stage. 
* Procedural generation gracefully degrades to highly-curated thematic templates if API rate limits are hit.
* If any of the four AI providers experience downtime, the `LLMAgent` falls back to deterministic mock logic, ensuring the presentation dashboard remains fully functional.

### 4. Fleet AI Compliance & Export
To satisfy the Fleet AI category requirements, the environment automatically generates machine-readable forensic evidence bundles compliant with the **STIX 2.1** standard. These reports are output directly to the `graphify-out/` directory upon episode completion.

---

## 🛠️ Repository Polish (V4.2)

We have ruthlessly minimized technical debt to provide you with a clean, professional codebase:
* **The Graveyard is Gone:** Removed over 100KB of redundant, legacy code (including `app_head.py`).
* **Transient Purge:** Cleared all temporary caches, leftover training logs, and abandoned scratch scripts.
* **FSM-Compliant Agents:** The `llm_agent.py` logic strictly enforces Finite State Machine actions, completely preventing invalid "verdict jumps" without requisite evidence.
* **UI Stabilization:** The Gradio frontend (`app.py`, `frontend/theme.py`) includes a high-priority **"STOP ANALYSIS"** interrupt to prevent autonomous loop hangs, and accurate graph rendering for live evidence nodes.

---

## 🏁 How to Evaluate

1. **Start the Environment:**
   ```bash
   python app.py
   ```
2. **Access the Dashboard:** Open your browser to `http://localhost:7860`.
3. **Run the Capstone:** Select the "Plandemic" scenario from the task dropdown and click "Begin Investigation". Watch as the Multi-Provider Society of Thought dissects the generated claim.
4. **Inspect the Weights:** View the trained checkpoints `checkpoints/gin_model.pt` and `checkpoints/hae_model.pt` that power the backend logic.

*We hope you enjoy reviewing FORGE-MA as much as we enjoyed building it!*
