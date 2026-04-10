---
title: FORGE Misinformation RL
colorFrom: green
colorTo: blue
sdk: docker
pinned: true
tags:
  - openenv
  - reinforcement-learning  
  - misinformation
  - fact-checking
  - trust-and-safety
  - graph-neural-network
  - content-moderation
---

# FORGE: Forensic RL Graph Environment

> Train and evaluate agents that investigate misinformation the way 
> human fact-checkers actually do — sequentially, under time pressure, 
> with incomplete information.

> [Why FORGE matters for real-world content moderation →](REAL_WORLD_IMPACT.md)

## The Problem FORGE Solves

Content moderation at scale faces a fundamental tension: human 
fact-checkers are accurate but slow; automated classifiers are fast 
but shallow. Neither approach models the **investigative process** 
that experienced Trust & Safety engineers use.

FORGE bridges this gap. It frames fact-checking as a sequential 
decision problem where an agent must:

- Choose which forensic tool to apply at each step
- Build a structured evidence graph from tool results  
- Submit a verdict under a tight step budget

An agent trained on FORGE learns **investigation policies** — not 
just classification boundaries. It learns that some claims require 
source verification first; others require timeline analysis; others 
require bot network detection. This mirrors how real content 
moderation teams triage and escalate content.

**Immediate applications:**
- Training automated triage systems for content moderation pipelines
- Benchmarking LLMs on structured investigative reasoning
- Studying how investigation strategies transfer across misinformation types
- Evaluating whether agents can prioritise the right tools under budget constraints

## Environment

**Observation** — `Box(3859,)` float32:
```text
[0:3840]     Sentence embeddings of up to 10 discovered claim graph nodes
[3840:3853]  Tool usage history (call counts per action)
[3853:3859]  Graph scalars: coverage, diversity, contradictions, manipulation_flag, budget_remaining, steps_ratio
```

**Actions** — `Discrete(13)`:
```text
Investigation tools (0-7):
0  query_source      Domain credibility check
1  trace_origin      Wayback Machine / propagation tracing
2  cross_reference   Wikipedia / encyclopedia verification
3  request_context   LLM structural summarisation
4  entity_link       Wikidata entity disambiguation
5  temporal_audit    Timestamp anomaly detection
6  network_cluster   Bot network / coordination detection
7  flag_manipulation Free action — tag adversarial intent

Verdicts (8-12):
8   submit_verdict_real
9   submit_verdict_misinfo
10  submit_verdict_satire
11  submit_verdict_out_of_context
12  submit_verdict_fabricated
```

**Reward** — Dense, potential-based shaped reward (Ng et al., 1999):
```text
Step reward:    r = base + γΦ(s') − Φ(s)
Terminal:       correctness + calibration bonus + efficiency bonus + manipulation detection component
Range:          (0.001, 0.999) — strictly open interval
```

## Tasks

| Task | Difficulty | Domain | Required Tools | Real Data |
|---|---|---|---|---|
| `fabricated_stats` | Easy | Science/Health | entity_link, cross_reference | No |
| `verified_fact` | Easy | Control | cross_reference, entity_link | No |
| `out_of_context` | Medium | Media/Images | trace_origin, temporal_audit | No |
| `politifact_liar` | Medium | Politics | cross_reference, entity_link | **LIAR dataset** |
| `satire_news` | Medium | Journalism | request_context, cross_reference | No |
| `coordinated_campaign` | Hard | Social Networks | network_cluster, query_source | No |
| `image_forensics` | Hard | Multimodal | temporal_audit, trace_origin | No |
| `sec_fraud` | Hard | Finance/SEC | cross_reference, entity_link | No |

Each task has a deterministic grader that awards partial credit for 
correct tool usage independently of verdict correctness — providing 
dense signal across the full trajectory.

## Adversarial Self-Play

FORGE includes a GAN-inspired co-evolutionary training regime:
Generator Agent  →  crafts misinformation designed to evade detection
Investigator     →  learns to detect the generator's output
↑                              ↓
└──── mutual improvement loop ─┘

This mirrors the real-world dynamic where bad actors continuously 
adapt their techniques to evade detection systems. Unlike static 
datasets, FORGE's adversarial curriculum generates novel, 
increasingly sophisticated misinformation patterns.

```bash
python scripts/run_selfplay.py --rounds 10 --difficulty 3
```

## Quick Start

```bash
# Install
git clone https://github.com/Harshal1841A/Forge-RL.git
pip install -r requirements.txt

# Run offline evaluation (no API key needed)
python inference.py --episodes 2

# Run with LLM agent
HF_TOKEN=your_groq_key python inference.py --episodes 2

# Start server
docker build -t forge . && docker run -p 7860:7860 forge
```

## API

```bash
# Start episode
curl -X POST /reset \
  -d '{"task_name": "coordinated_campaign", "difficulty": 2}'

# Investigate
curl -X POST /step -d '{"action": 6}'  # network_cluster

# Check what was found
# Response includes info.hint with plain-English guidance for LLM agents

# Submit verdict
curl -X POST /step -d '{"action": 9}'  # submit_verdict_misinfo

# Get graded score
curl /episodes/{id}/grade
```

## Baseline Results

| Task | Difficulty | Heuristic | LLM (Groq) |
|---|---|---|---|
| fabricated_stats | Easy | ~35% | ~70% |
| verified_fact | Easy | ~45% | ~80% |
| out_of_context | Medium | ~30% | ~65% |
| politifact_liar | Medium | ~25% | ~60% |
| satire_news | Medium | ~30% | ~65% |
| coordinated_campaign | Hard | ~40% | ~85% |
| image_forensics | Hard | ~20% | ~75% |
| sec_fraud | Hard | ~25% | ~68% |

## Design Decisions

**Why graph-based observation?** Misinformation investigation is 
inherently relational — the same claim means different things 
depending on who is amplifying it, when it appeared, and what 
authoritative sources say. A flat observation cannot capture this 
structure. FORGE maintains an explicit `ClaimGraph` where nodes 
are sources and edges represent support/contradiction/amplification 
relationships.

**Why potential-based shaping?** Binary terminal rewards provide 
no learning signal until the final step. Potential-based shaping 
(Ng et al., 1999) provides dense step-level rewards that are 
guaranteed policy-invariant — the optimal policy under the shaped 
reward is identical to the optimal policy under the sparse reward.

**Why 5 verdict classes?** Binary real/fake classification is 
insufficient for real content moderation. FORGE distinguishes 
between fabricated (entirely made up), out_of_context (real content 
wrong context), satire (intentional parody), misinfo (false claims), 
and real — matching the taxonomy used by professional fact-checkers.

## Architecture
```text
FORGE/
├── env/
│   ├── misinfo_env.py      Gymnasium-compatible environment
│   ├── claim_graph.py      Evidence graph data structure
│   ├── reward.py           Potential-based reward shaping
│   └── tasks/              8 task generators + programmatic graders
├── agents/
│   ├── llm_agent.py        FSM-constrained ReAct LLM agent
│   ├── heuristic_agent.py  Deterministic baseline (offline)
│   ├── ppo_agent.py        PPO training agent
│   └── adversarial/        GAN-style self-play agents
├── tools/                  Forensic tool implementations
│   ├── query_source.py     Wikipedia + DuckDuckGo
│   ├── trace_origin.py     Wayback Machine + Wikidata
│   ├── cross_reference.py  Wikipedia multi-article
│   ├── entity_link.py      Wikidata SPARQL
│   ├── temporal_audit.py   Wayback timestamp verification
│   └── network_cluster.py  Graph-based bot detection
├── server/                 FastAPI OpenEnv REST API
└── inference.py            OpenEnv evaluation script
```
