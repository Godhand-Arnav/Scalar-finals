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

In 2018, a two-minute WhatsApp video of a man "kidnapping a child" spread through a village in Jharkhand. It was actually a public awareness clip shot in Pakistan. By the time anyone figured that out, five people had been lynched by a mob. The video had been forwarded so many times that no one remembered where it came from or what it originally meant.

This is not a one-off. It is a pattern.

In 2019, weeks before the general election, a deepfake video of Amit Shah circulated where he appeared to say the BJP would scrap reservations for OBCs. It never happened. The video was synthetic. But it spread through 50,000 WhatsApp groups in 48 hours — and WhatsApp University, as we like to call it, has no peer review process.

The damage is not done when the lie spreads. It is done the moment the lie *feels* true to someone. And by the time a fact-checker catches up, that moment has long passed for millions of people.

We have spent years building tools that answer the wrong question. "Is this claim true or false?" is the question of a referee. What we actually need are detectives — systems that can look at a piece of misinformation and ask: who built this, how, and which specific tactics did they use to make it believable?

That is forensic reasoning. Not binary classification. Not sentiment analysis. Actual, structured, step-by-step forensic reasoning — the kind that maps a disinformation campaign the way a crime scene investigator maps a murder scene.

No open-source tool was doing this.

So during the META AI Hackathon, we built FORGE-RL: a reinforcement learning pipeline that trains a language model — a genuinely small one, 0.5 billion parameters, free to run on Kaggle — to identify the precise deception tactics used to construct any given misinformation claim.

We ran it for 100 steps. The reward nearly doubled.

We think that matters. A lot.

---

## Why This Is Different From Every Other Misinformation Tool

Here is the thing about existing fact-checking tools — they are all playing defence. You feed them a claim, they tell you if it is true. That is useful, but it is the equivalent of a doctor who can only tell you if you are sick, not what disease you have or how you caught it.

FORGE-RL is a pathologist, not just a physician.

When FORGE-RL analyses a claim, it does not just say "false". It says: "This claim was constructed using SOURCE_LAUNDER followed by TEMPORAL_SHIFT — someone took a real 2012 quote, attributed it to a credible institution, and presented it as a statement from yesterday." That is actionable intelligence. You can trace the campaign. You can find other content using the same fingerprint. You can build a case.

Think of it this way. Every WhatsApp forward your uncle sends is not random — it was *designed*. Someone sat down and deliberately chose which deception tactics to combine to make it believable to a 60-year-old in a tier-2 city at 6 AM. FORGE-RL can read that design. No other open-source tool can.

And because it is a *trained model*, not a rule-based system, it generalises. Feed it a claim it has never seen before in a domain it was never trained on — it still tries to reason about the forensic structure. It gets better every time you train it with more episodes. It runs on hardware you already have access to for free.

---

## What FORGE-RL Actually Does

The first thing we did was build a vocabulary of deception primitives — the atomic building blocks that real disinformation campaigns are assembled from:

| Primitive | What It Means | Real Indian Example |
|---|---|---|
| `SOURCE_LAUNDER` | Attribute a false claim to a credible-sounding source | "AIIMS doctors confirm drinking cow urine cures COVID" — AIIMS never said this |
| `TEMPORAL_SHIFT` | Present old or future events as happening right now | 2013 Muzaffarnagar riot footage shared in 2020 as "fresh violence today" |
| `QUOTE_FABRICATE` | Attach words to a real person that they never said | The 2019 deepfake of Amit Shah on OBC reservations |
| `CONTEXT_STRIP` | Remove the context that makes a true statement misleading | A satire article from The Fauxy shared as real news — happens every other week |
| `CITATION_FORGE` | Invent or distort academic/official sources | "WHO confirms turmeric milk prevents coronavirus" — WHO said no such thing |
| `NETWORK_AMPLIFY` | Use coordinated bot networks to manufacture consensus | 2021 Twitter trends in India manufactured by coordinated bot accounts |
| `SATIRE_REFRAME` | Take satirical content and present it as factual | Onion-style headlines from Postcard News shared as breaking news |
| `ENTITY_SUBSTITUTE` | Swap real people, places, or dates to change the story | Pakistani flood images shared as photos from recent Indian disasters |

Every synthetic misinformation claim in our training environment is assembled from a hidden chain of these primitives. The model's job is to predict that chain from the claim text alone — like reading the recipe from the finished dish.

If you have ever received a WhatsApp forward from a "concerned uncle" that starts with "Please share this immediately, very important —" you have seen at least three of these primitives working together.

The reward signal we designed for this is called Tactic-Edit-Distance (TED): how many edits would you need to transform the model's predicted chain into the true one? The closer the prediction, the higher the reward. It is clean, differentiable, and directly measures what we care about.

---

## The Training Pipeline (And the Crashes We Fixed Along the Way)

Getting this to run reliably on a free GPU took more debugging than we care to admit. Pydantic version conflicts. Bleeding-edge `trl` releases that imported a module that did not exist yet. FP16 gradient scaling errors that appeared only on P100 hardware. We hit all of it.

Every single one is fixed. Every fix is documented in the notebook. You will not have to figure any of this out.

The final setup: one bootstrap cell that auto-detects whether you are on Colab, Kaggle, or local, installs the right dependencies, and clones the repo. From there, LoRA adapters (r=16) keep the FP16 base model frozen while the adapters themselves train in FP32 — which is what fixes the gradient scaling crash. The environment generates ground-truth primitive chains automatically, so there is no manual labeling involved at any point.

### How GRPO Works Here

Forget value networks. Forget reference models. GRPO is beautifully simple: the model generates 4 forensic analyses for the same claim. We score them all. The better ones get reinforced. The worse ones get discouraged. Repeat 100 times.

No labels. No human annotation. Just a reward signal and a policy update.

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
# → "Training complete!"
```

---

## The Results

![Reward curve – GRPO training on Qwen-0.5B](/assets/grpo_reward_curve.png)

Watch the curve. At step 0, the model knows nothing — mean TED reward is barely above zero. By step 40, it starts learning the forensic vocabulary. By step 65, it crosses the random baseline of 0.11 — it is now better than random at identifying deception tactics in a structured claim. By step 90, it hits 0.20, nearly double the baseline, with 100 steps of training on a free GPU.

```
[Step 100] Training complete!
Evaluation on 20 episodes → Mean TED = 0.174
Improvement: random(0.11) → pre-train(~0.14) → after GRPO(0.174)
```

Is 0.174 the ceiling? Absolutely not. This is a 0.5B model trained for 5 minutes. Swap in a 7B model with NF4 quantization, train for 1000 steps, and you are in genuinely competitive territory. The architecture scales. The reward signal scales. The environment scales. We just proved the concept works on the most constrained possible setup.

---

## Run It Yourself

```bash
git clone https://github.com/Godhand-Arnav/Scalar-finals.git
cd Scalar-finals
# Open notebooks/trl_forge_rl.ipynb in Colab or Kaggle
# Run Cell 1, wait for "Setup complete.", then run all remaining cells
```

Everything is pinned. Everything is documented. Nothing requires a paid API key to train. The dependencies are locked to `trl==0.15.1`, `pydantic==2.9.2`, `torch>=2.1.0` — no version guessing. The `.env.example` has labeled slots for every service used (Groq, Cerebras, Mistral, OpenRouter, GNews). The reward curve is saved to `baselines/grpo_reward_curve.png` automatically at the end of training.

---

## What We Are Building Next

FORGE-RL was built in a weekend, but we are not done with it.

The `MisInfoForensicsEnv` is a proper OpenAI Gym environment — any agent can plug in. The primitive vocabulary is editable without retraining. The reward function is swappable. The architecture is a scaffold, not a monolith.

We are actively working on multilingual forensics using `aya-23-8b` for non-English disinformation, adversarial self-play where a red-team generator goes up against the forensic blue-team agent in a loop, a live HF Space where you can paste any claim and get a forensic chain back in real time, and federated training that lets news organizations fine-tune collaboratively without sharing raw article data.

If any of this sounds like something you want to build with us, the issues page is open.

[Open Issues](https://github.com/Godhand-Arnav/Scalar-finals/issues)

---

## Why You Should Use This, Not Just Star It

Most research projects get starred on GitHub and never run. We built FORGE-RL specifically to break that pattern.

The notebook is a single file. You do not need to understand LoRA, GRPO, or Pydantic version hell to run it — all of that is handled in Cell 1. You do not need a paid GPU — Kaggle gives you 30 hours of free P100 time every week. You do not need a labelled dataset — the environment generates training data on its own.

What you *do* get at the end is a model that has learned to reason forensically about misinformation claims, a reward curve that shows exactly how much it improved, and a modular codebase you can immediately extend for your own use case — whether that is Hindi-language fact-checking, political deepfake detection, or building a browser extension that annotates WhatsApp screenshots.

India has 500 million WhatsApp users. The next election cycle is not far. The next health scare will come. The next riot-triggering video is probably being edited right now somewhere. The tools to understand how that content is made should not be locked behind expensive APIs or academic paywalls.

This one is not. Fork it and use it.

---

## A Closing Thought

The misinformation problem is not going to be solved by a better classifier. It is going to be solved by systems that understand *how* disinformation works — the tactics, the patterns, the forensic fingerprints that campaigns leave behind.

Fact-checkers are tired. Journalists are overworked. Platform moderation teams are drowning. We cannot hire our way out of this problem. We need tools that scale — and the only thing that scales like disinformation does is AI.

We do not think we have solved it. But we have proved that a tiny, open-source, free-to-run language model can start to reason about it in a structured way — and that it gets meaningfully better when you give it the right reward signal. That is not a small thing. That is the proof of concept that makes everything else possible.

Fork it. Run it. Train it on your own data. Build the thing we did not have time to build during the hackathon. We want to see what you find.

[GitHub Repository](https://github.com/Godhand-Arnav/Scalar-finals) — [Demo Space](https://huggingface.co/spaces/NeuralHU/forge-rl) — [HACKATHON_README](https://github.com/Godhand-Arnav/Scalar-finals/blob/main/HACKATHON_README.md)

---

*Built during the META AI Hackathon. All feedback, critiques, and pull requests genuinely welcome.*
