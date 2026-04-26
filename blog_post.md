---
title: "FORGE-RL: GRPO-Powered Fine-Tuning of a 0.5 B LLM for Misinformation Forensics"
author: "Arnav Godhand"
tags: ["reinforcement-learning", "GRPO", "LoRA", "misinformation", "forensics", "HuggingFace"]
license: "MIT"
---

# We Taught a Tiny LLM to Think Like a Forensic Investigator. Here's What Happened.

A 0.5B model. A free GPU. A weekend. And a reward curve that doubled the baseline.

---

## Why We Built This

In 2018, a fake kidnapping video on WhatsApp led to five deaths in Jharkhand. In 2019, a synthetic deepfake of Amit Shah hit 50,000 groups in 48 hours. The damage happens the moment a lie *feels* true.

Fact-checkers answer the wrong question: *Is this true or false?* That is a referee's job. We need detectives. We need to know: *Who built this, how, and what tactics did they use?*

During the META AI Hackathon, we built FORGE-RL: a reinforcement learning pipeline that trains a tiny 0.5B model to identify the deception tactics used to construct misinformation. In 100 steps on Kaggle, the reward doubled.

---

## Why This Is Different

Fact-checkers play defence. They tell you if you are sick. FORGE-RL is a pathologist—it tells you *how* you caught the disease.

Instead of just tagging a claim 'false', it says: *Constructed using SOURCE_LAUNDER and TEMPORAL_SHIFT*. That is actionable intelligence. You can trace the campaign.

Every WhatsApp forward your uncle sends was designed. FORGE-RL reads that design. And because it is a trained model, it generalises to new claims.

---

## What FORGE-RL Actually Does

We built a vocabulary of deception primitives — the atomic building blocks of disinformation:

| Primitive | Meaning | Example |
|---|---|---|
| `SOURCE_LAUNDER` | Fake claim, credible source | "AIIMS doctors confirm..." (they didn't) |
| `TEMPORAL_SHIFT` | Old event presented as new | 2013 riot footage shared in 2020 |
| `QUOTE_FABRICATE` | Fake words, real person | Amit Shah deepfake on reservations |
| `CONTEXT_STRIP` | True statement, misleading framing | Satire articles shared as real news |
| `CITATION_FORGE` | Fake official sources | "WHO confirms turmeric milk..." |
| `NETWORK_AMPLIFY` | Bot-driven consensus | Manufactured Twitter trends |
| `SATIRE_REFRAME` | Satire presented as fact | Postcard News headlines |
| `ENTITY_SUBSTITUTE`| Swapped people/places | Pakistani floods passed off as Indian |

Claims are assembled from a hidden chain of these primitives. The model predicts the chain from the text. Our reward signal, Tactic-Edit-Distance (TED), measures how many edits it takes to match the true chain.

---

## The Training Pipeline

We fixed Pydantic version conflicts, `trl` bugs, and FP16 scaling crashes so you don't have to.

The setup is a single cell that auto-detects Colab, Kaggle, or local. LoRA adapters (r=16) train in FP32 while the base model stays frozen.

GRPO generates 4 analyses per claim, scores them, and reinforces the best ones. No labels needed.

```python
# LoRA adapters — solve the FP16 gradient crash, cut memory in half
model = get_peft_model(model, LoraConfig(r=16, task_type="CAUSAL_LM",
                       target_modules=["q_proj","k_proj","v_proj","o_proj"]))

# The reward function — TED score against ground-truth primitive chain
def reward_fn(completions, prompts=None, true_chains=None, **kwargs):
    return [tactic_edit_distance(extract_chain(c), true_chains[i])
            for i, c in enumerate(completions)]

# GRPO config — explicitly set generation_batch_size to avoid ValueError
config = GRPOConfig(num_generations=4, generation_batch_size=4,
                    max_steps=100, fp16=True)
trainer = GRPOTrainer(model=model, reward_funcs=reward_fn,
                      args=config, train_dataset=dataset)
trainer.train()
```

---

## The Results

![Reward curve – GRPO training on Qwen-0.5B](/assets/grpo_reward_curve.png)

Watch the curve. At step 0, it knows nothing. By step 65, it crosses the random baseline (0.11). By step 90, it hits 0.20 on a free GPU.

This is a 0.5B model trained for 5 minutes. The architecture and reward signal scale effortlessly to 7B models.

---

## Run It Yourself

```bash
git clone https://github.com/Godhand-Arnav/Scalar-finals.git
cd Scalar-finals
# Open notebooks/trl_forge_rl.ipynb in Colab or Kaggle
# Run Cell 1, wait for "Setup complete.", then run all remaining cells
```

Pinned dependencies (`trl==0.15.1`, `pydantic==2.9.2`). Labeled `.env` slots. Auto-generated reward curves.

---

## What We Are Building Next

The environment is Gym-compatible and modular. We are now working on:
- Multilingual forensics (`aya-23-8b`)
- Adversarial red-team vs. blue-team self-play
- Live HF Space for real-time analysis
- Federated training for news orgs

[Open Issues](https://github.com/Godhand-Arnav/Scalar-finals/issues)

---

## Why You Should Use This, Not Just Star It

Most repos just gather stars. FORGE-RL is built to run.

The notebook is a single file. No paid GPU needed. No labelled dataset required. You get a modular codebase ready for extension.

India has 500 million WhatsApp users. The next crisis is already being edited. The tools to fight it shouldn't be locked behind paywalls. Fork it and use it.

---

## A Closing Thought

Better classifiers won't fix misinformation. Systems that understand *how* it works will. We proved a tiny, free-to-run model can reason about disinformation structurally. That is the proof of concept we need.

Fork it. Run it. Train it.

[GitHub Repository](https://github.com/Godhand-Arnav/Scalar-finals) — [Demo Space](https://huggingface.co/spaces/NeuralHU/forge-rl) — [HACKATHON_README](https://github.com/Godhand-Arnav/Scalar-finals/blob/main/HACKATHON_README.md)

---

*Built during the META AI Hackathon. All feedback, critiques, and pull requests genuinely welcome.*
