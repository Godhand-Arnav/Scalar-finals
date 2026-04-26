---
title: "FORGE‑MA: GRPO‑Powered Fine‑Tuning of a 0.5 B LLM for Misinformation Forensics"
author: "Arnav Godhand"
tags: ["reinforcement-learning", "GRPO", "LoRA", "misinformation", "forensics", "HuggingFace"]
license: "MIT"
---

# We Taught a Tiny LLM to Think Like a Misinformation Detective — Here's How

**What started as a hackathon side-project turned into something we genuinely believe could matter: a tiny 0.5B model that learns to forensically dissect fake news — trained in under 30 minutes on a free GPU.**

---

## Why We Built This

Honestly? We were frustrated.

Every time we saw a viral misinformation post get debunked, the fact-check came hours — sometimes *days* — too late. By then the damage was done. But what bothered us even more was that the debunks rarely explained the *mechanics*. They said "this is false" but never "here's exactly how it was constructed to fool you."

A lie isn't random. It has a structure. Someone chose to take a real statistic and strip its source (`SOURCE_LAUNDER`). Someone deliberately shifted the date on a news story to make it feel recent (`TEMPORAL_SHIFT`). Someone took a genuine expert quote and ripped it out of context (`QUOTE_FABRICATE`).

If we could teach a model to *identify those construction techniques* — not just label something true or false — we'd have something actually useful for analysts, journalists, and researchers.

That's FORGE‑MA. That's what we spent our hackathon building.

---

## What It Actually Does

At its core, FORGE‑MA is a reinforcement learning pipeline. We take a small Qwen‑0.5B model — small enough to run free on Kaggle or Colab — and we train it with GRPO to identify **deception primitives**: the building blocks that bad actors combine to construct misinformation.

Instead of telling the model "the right answer is X", we let it generate 4 different responses, score each one using our **Tactic‑Edit‑Distance (TED) reward**, and nudge it toward the answers that scored highest. Repeat 100 times. Done.

| Feature | What it means in plain English |
|---|---|
| 🌍 **Universal Setup** | One cell. Paste it into Colab or Kaggle. It figures out the rest. |
| 🧠 **GRPO Training** | The model generates 4 guesses per prompt and learns from which ones were closest. |
| 🎯 **TED Reward** | We score how close the model's forensic chain is to the real one — like edit distance, but for deception tactics. |
| ⚡ **Runs on a Free GPU** | P100 or T4. < 4 GB VRAM. ~5 minutes per 100 steps. |
| 📖 **Fully Open Source** | MIT license. Fork it, extend it, break it. |

### The Core Training Loop (Simplified)

```python
# Wrap the base model with tiny LoRA adapters (only 0.1% of params are trained!)
model = get_peft_model(model, LoraConfig(r=16, task_type="CAUSAL_LM",
                       target_modules=["q_proj","k_proj","v_proj","o_proj"]))

# Our custom reward: how close is the model's forensic chain to the truth?
def reward_fn(completions, prompts=None, true_chains=None, **kwargs):
    return [tactic_edit_distance(extract_chain(c), true_chains[i])
            for i, c in enumerate(completions)]

# Let GRPO do its thing — no value network, no reference model needed
trainer = GRPOTrainer(model=model, reward_funcs=reward_fn,
                      args=GRPOConfig(num_generations=4, max_steps=100, fp16=True),
                      train_dataset=dataset)
trainer.train()
# → "Training complete!"
```

The thing we love most about GRPO here: it doesn't need a separate "critic" network like PPO does. It's simpler, leaner, and it worked on our free GPU without running out of memory. That matters a lot when you're a small team with no budget.

---

## Did It Actually Work?

Yeah, it did — more than we expected.

![Reward curve – GRPO training on Qwen‑0.5B](/assets/grpo_reward_curve.png)

Here's what happened during training:

- **Early steps (0–30):** The model was basically guessing. Mean TED reward was around 0.02 — nearly random.
- **Mid training (30–65):** Something clicked. The reward started climbing consistently as the model picked up the vocabulary of deception primitives.
- **Step 65:** The model crossed the random baseline of 0.11. It was now *smarter than chance* at forensic analysis.
- **Step 90:** Peak reward hit **0.20** — nearly double the baseline.

```
[Step 100] Training complete!
Evaluation on 20 fresh episodes → Mean TED = 0.174
Journey: random(0.11) → untrained(~0.14) → GRPO-trained(0.174)
```

A 58% improvement over random, in 30 minutes, on a free GPU. For a hackathon proof-of-concept, we'll take it.

*(And yes — the loss stayed near zero for most of training. That's totally normal in GRPO. The reward is what you watch, not the loss.)*

---

## You Can Reproduce This Exactly

We were obsessive about making this reproducible because honestly, papers and demos that you can't actually run are useless. Here's everything:

- ✅ **`notebooks/trl_forge_ma.ipynb`** — open in Colab or Kaggle, run Cell 1, done. Literally zero setup beyond that.
- ✅ **Pinned versions** — `trl==0.15.1`, `pydantic==2.9.2` — we learned the hard way that bleeding-edge library updates will silently break your training loop.
- ✅ **`.env.example`** — all the API slots labeled so you know exactly what key goes where.
- ✅ **Auto-generated reward curve** — saved to `baselines/grpo_reward_curve.png` the moment training ends.

```yaml
# .env.example — just fill in your free keys
OPENAI_API_KEY="<groq-token>"           # Forensic Auditor agent
CEREBRAS_API_KEY="<cerebras-token>"     # Context Historian agent
MISTRAL_API_KEY="<mistral-token>"       # Narrative Critic agent
OPENROUTER_API_KEY="<openrouter-token>" # NegotiatedSearch agents
GNEWS_API_KEY="<gnews-token>"           # Live news tool
```

---

## Where This Goes Next

We're excited about this beyond the hackathon. A few directions we're already thinking about:

- **Multilingual** — the same pipeline should work with `aya-23-8b` or `Mistral-7B-multilingual`. Misinformation isn't only in English.
- **Bigger models** — the LoRA setup can scale up to 7B parameters with 4-bit NF4 quantization on a single A100 if you have access to one.
- **HF Spaces demo** — we want to build a live interface where you paste any claim and get back a forensic primitive chain in seconds.
- **Plugging into real newsrooms** — `MisInfoForensicsEnv` is designed to be modular. You can swap in your own claim dataset and reward function without touching the training code.

If any of this sounds useful to your work, we'd genuinely love to collaborate. Open an issue, send a PR, or just drop a comment below.

[![Contribute](https://img.shields.io/badge/Contribute-Open%20Issues-blueviolet?style=flat-square)](https://github.com/Godhand-Arnav/Scalar-finals/issues)

---

## Give It a Try

The whole thing runs in a single notebook. No setup beyond running Cell 1.

```bash
git clone https://github.com/Godhand-Arnav/Scalar-finals.git
cd Scalar-finals
# Open notebooks/trl_forge_ma.ipynb in Colab or Kaggle
```

If you train your own version — especially if you get a better reward curve than us — tag your HF Space with `forge-ma`. We want to see what the community does with it.

**→ [GitHub Repository](https://github.com/Godhand-Arnav/Scalar-finals)**
**→ [Live Demo Space](https://huggingface.co/spaces/NeuralHU/forge-rl)**
**→ [Full README](https://github.com/Godhand-Arnav/Scalar-finals/blob/main/HACKATHON_README.md)**

---

*Built at the META AI Hackathon by a small team that got very annoyed at misinformation and decided to do something about it. If forensic AI should exist anywhere, it should exist in the open.*
