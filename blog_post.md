---
title: "FORGE‑MA: GRPO‑Powered Fine‑Tuning of a 0.5 B LLM for Misinformation Forensics"
author: "Arnav Godhand"
tags: ["reinforcement-learning", "GRPO", "LoRA", "misinformation", "forensics", "HuggingFace"]
license: "MIT"
---

# FORGE‑MA: Teaching a Tiny LLM to Unmask Fake News with Reinforcement Learning

**What if a 0.5B model — smaller than most chat assistants — could learn to think like a forensic investigator? We built it. In under 30 minutes. On a free GPU.**

---

## Why We Built This

Honestly? We were frustrated.

Misinformation detection tools are everywhere — but almost all of them stop at the question *"Is this true or false?"*. That is like hiring a detective who only tells you whether a crime happened, not *how* it was committed.

The harder, more important question is: **what tactics were used to construct this piece of misinformation in the first place?** Was the source laundered through a seemingly credible outlet? Was a genuine quote pulled out of context? Was a statistic technically accurate but temporally misleading?

These are the questions that forensic analysts actually ask. And they are the questions that **FORGE‑MA** is designed to answer.

We built this during the META AI Hackathon, and it started as a weekend experiment: *can we use reinforcement learning — specifically GRPO — to teach a tiny, free-to-run language model to trace the fingerprints of a disinformation campaign?*

Spoiler: yes, and the results surprised even us.

---

## What Is FORGE‑MA, Exactly?

FORGE‑MA stands for *Forensic Ordinance for Generative Reasoning Environments — Multi‑Agent*. The name is a mouthful, but the idea is simple:

1. We define a vocabulary of **deception primitives** — atomic tactics like `SOURCE_LAUNDER`, `TEMPORAL_SHIFT`, `QUOTE_FABRICATE`, `CONTEXT_STRIP` — that real disinformation campaigns use.
2. We create a training environment that generates synthetic misinformation claims, each assembled from a hidden chain of those primitives.
3. We fine‑tune **Qwen‑0.5B** (a genuinely tiny model) using **GRPO** to predict that hidden chain — rewarding it every time it gets closer to the true forensic fingerprint.

The reward metric we use is called **Tactic‑Edit‑Distance (TED)** — it measures how many edits you would need to transform the model's predicted chain into the ground‑truth chain. Think of it as the AI equivalent of a forensic investigator's accuracy score.

---

## The Technical Bits (We Promise It's Worth Reading)

Getting this to actually work on a free Kaggle/Colab GPU was... an adventure. Here is what the final system looks like:

| Feature | What We Did |
|---|---|
| 🌍 **Universal Setup** | One bootstrap cell — works on Colab, Kaggle, and local. Auto‑detects the runtime, no manual config. |
| 🧠 **GRPO Training** | 4 completions per prompt, LoRA adapters (r=16) so the FP16 base model stays frozen while adapters train in FP32. |
| 🎯 **TED Reward** | Custom `reward_fn` scores each completion against the ground‑truth primitive chain. No labels needed — the environment generates them. |
| ⚡ **Hardware Efficient** | P100/T4, < 4 GB VRAM, 100 steps in ~5 minutes. Genuinely free to run. |
| 📖 **Open Source** | MIT license, pinned dependencies, `.env.example` for all API keys. |

One thing we want to flag: we hit a *lot* of dependency issues along the way — wrong `pydantic` versions, `mergekit` import crashes in bleeding‑edge `trl`, FP16 gradient errors. We fixed every single one and documented the solutions in the notebook comments, so **you won't have to**.

### The Training Loop in Plain English

For every training step, the model looks at a misinformation claim and generates 4 different forensic analyses. We score all 4 using TED. The ones that identified the deception tactics more accurately get a higher reward. GRPO then nudges the model's weights to make those better responses more likely next time — no reference model, no value network, no fuss.

```python
# 1. Wrap Qwen-0.5B with LoRA adapters (fixes the FP16 gradient crash!)
model = get_peft_model(model, LoraConfig(r=16, task_type="CAUSAL_LM",
                       target_modules=["q_proj","k_proj","v_proj","o_proj"]))

# 2. Custom TED reward — the heart of the whole system
def reward_fn(completions, prompts=None, true_chains=None, **kwargs):
    return [tactic_edit_distance(extract_chain(c), true_chains[i])
            for i, c in enumerate(completions)]

# 3. Let GRPO do its thing
config = GRPOConfig(num_generations=4, generation_batch_size=4,
                    max_steps=100, fp16=True)
trainer = GRPOTrainer(model=model, reward_funcs=reward_fn,
                      args=config, train_dataset=dataset)
trainer.train()
# → "Training complete!"
```

---

## The Results (This Is the Part We Are Proud Of)

![Reward curve – GRPO training on Qwen‑0.5B](/assets/grpo_reward_curve.png)

The curve tells a clear story. At the start, the model is essentially guessing — mean TED reward hovering around 0.02. By step 65, it crosses the **random baseline of 0.11**, meaning it has genuinely learned something about forensic reasoning. By step 90, it peaks at **0.20 — nearly double the baseline**.

```
[Step 100] Training complete!
Evaluation on 20 episodes → Mean TED = 0.174
Improvement: random(0.11) → pre‑train(~0.14) → after GRPO(0.174)
```

Is 0.174 perfect? No. But this is a **0.5 billion parameter model**, trained for **100 steps**, on a **free GPU**. The fact that it learns anything meaningful about a structured forensic task in that time is — we think — genuinely exciting. And the architecture scales: swap in a 7B model with 4‑bit NF4 quantization and you can push this much further.

---

## You Can Reproduce This. Right Now.

We made this as easy to run as we possibly could:

- ✅ **One‑click notebook** — `notebooks/trl_forge_ma.ipynb`. Run Cell 1, run the rest, get a reward curve.
- ✅ **Pinned dependencies** — `trl==0.15.1`, `pydantic==2.9.2`, `torch>=2.1.0`. No guessing which version breaks what.
- ✅ **API template** — `.env.example` with labeled slots for every service we use (Groq, Cerebras, Mistral, OpenRouter, GNews).
- ✅ **Quick‑start guide** — `HACKATHON_README.md` with 5 steps from zero to training, plus a demo script.
- ✅ **Automatic reward curve** — `baselines/grpo_reward_curve.png` is generated at the end of training, ready to include in your write‑up.

```bash
git clone https://github.com/Godhand-Arnav/Scalar-finals.git
cd Scalar-finals
# Open notebooks/trl_forge_ma.ipynb in Colab or Kaggle and hit Run All
```

---

## Where This Can Go

We built FORGE‑MA as a hackathon project, but we think the core idea has legs beyond that.

The `MisInfoForensicsEnv` is a proper OpenAI Gym environment — you can drop any agent into it, not just the GRPO‑trained LLM. The `reward_fn` is modular — swap in a different reward signal and you have a completely different training objective. The primitive vocabulary in `env/primitives.py` is editable — extend it with new deception tactics without retraining from scratch.

Some directions we are genuinely excited about:
- **Multilingual support** — train on non‑English claims using `aya-23-8b` or `Mistral-7B-multilingual`
- **Larger models** — 7B with NF4 quantization, still fits on a single A100
- **Live HF Space** — paste any claim, get a forensic primitive chain back in seconds
- **Multi‑agent self‑play** — pit a red‑team generator against the forensic blue‑team agent in an adversarial loop

If any of these sound interesting to you, the issues page is open and we would genuinely love the collaboration.

[![Contribute](https://img.shields.io/badge/Contribute-Open%20Issues-blueviolet?style=flat-square)](https://github.com/Godhand-Arnav/Scalar-finals/issues)

---

## One More Thing

We spent a lot of time making sure this project works — not just in theory, but in practice, on the hardware most developers actually have access to. Every error we hit, we documented. Every dependency conflict, we resolved. Every config parameter that caused a crash, we fixed.

If this project helps even one person build something useful in the misinformation‑detection space, that is more than enough for us.

Fork it. Break it. Make it better.

**→ [GitHub Repository](https://github.com/Godhand-Arnav/Scalar-finals)**
**→ [Demo Space](https://huggingface.co/spaces/NeuralHU/forge-rl)**
**→ [HACKATHON_README](https://github.com/Godhand-Arnav/Scalar-finals/blob/main/HACKATHON_README.md)**

---

*Built with too much caffeine and genuine enthusiasm for the META AI Hackathon. All feedback welcome.*
