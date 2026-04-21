# Real-World Impact: Why FORGE Matters

## The Gap FORGE Fills

Existing misinformation benchmarks (LIAR, FakeNewsNet, MultiFC) 
treat fact-checking as **classification**: given a claim, output 
true/false. This misses the investigative process entirely.

FORGE is the first RL environment that models fact-checking as 
**sequential investigation** — the way human analysts actually work.

## Connection to Production Systems

A policy trained on FORGE can be directly adapted for:

**Automated triage**: An agent that learned investigation policies 
could pre-screen viral content, flagging items that exhibit 
coordinated amplification patterns or statistical anomalies — 
reducing the queue for human reviewers.

**Analyst assistance**: Rather than replacing human fact-checkers, 
a FORGE-trained agent can suggest which investigative tool to apply 
next — accelerating investigations by surfacing the most relevant 
evidence first.

**Robustness benchmarking**: The adversarial self-play regime 
generates novel misinformation patterns that production classifiers 
have never seen — providing a continuous red-teaming capability.

## Why RL, Not Fine-tuning?

Fine-tuned LLMs for fact-checking are brittle to distribution shift 
— they fail on misinformation patterns that weren't in their 
training data. An RL agent trained on FORGE learns transferable 
**investigation strategies** (check source credibility, verify 
timestamps, detect coordination) that generalise across new patterns.

## Benchmark vs. Training Environment

FORGE serves both purposes:
- **As a benchmark**: Evaluate how well any agent (LLM, RL, hybrid) 
  can conduct structured fact-checking investigations
- **As a training environment**: Train policies that transfer to 
  real-world content moderation tools
