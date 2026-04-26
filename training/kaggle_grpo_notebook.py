"""
FORGE-MA · Kaggle GRPO Training Notebook
=========================================
Cell layout:
  Cell 1  — Environment setup (this file)
  Cell 2  — Load dataset
  Cell 3  — Load model + apply LoRA
  Cell 4  — GRPO training loop
  Cell 5  — Evaluate + save

Run Cell 1 first; it applies all master fixes and exports the
training artefacts (GRPO_KWARGS, LORA_CONFIG, etc.) to the notebook
namespace so subsequent cells can use them directly.
"""

# ============================================================
# CELL 1 — Environment setup + Master Fix
# ============================================================
import os, sys, gc, torch

WORK_DIR = '/kaggle/working/forge-rl'
os.chdir(WORK_DIR)
if WORK_DIR not in sys.path:
    sys.path.insert(0, WORK_DIR)

# ── Apply all fixes in one shot ──────────────────────────────
from training.master_fix import (
    apply_all,
    LABELS, LABEL2ID, ID2LABEL, LABEL_WEIGHTS,
    parse_label, compute_reward, batch_rewards,
    sot_majority_vote,
    FORGE_SYSTEM_PROMPT,
    get_grpo_kwargs, get_lora_config,
    run_self_tests,
)

result = apply_all(
    openrouter_key=os.environ.get("OPENROUTER_API_KEY", ""),
    grpo_output_dir=f"{WORK_DIR}/grpo_output",
    verbose=True,
)

GRPO_KWARGS  = result["grpo_kwargs"]
LORA_CONFIG  = result["lora_config"]
assert result["tests_passed"], "Self-tests failed — fix before training!"

# ============================================================
# CELL 2 — Load dataset
# ============================================================
# Expects a CSV with columns: claim, label
# label must be one of: real | fabricated | misinfo | out_of_context
#
# from datasets import Dataset
# import pandas as pd
#
# df = pd.read_csv(f"{WORK_DIR}/data/hackathon_train.csv")
# df["label_id"] = df["label"].map(LABEL2ID)
# dataset = Dataset.from_pandas(df)
# print(dataset)

# ============================================================
# CELL 3 — Load model + apply LoRA
# ============================================================
# MODEL_NAME = result.get("active_or_model") or "meta-llama/Llama-3.2-3B-Instruct"
#
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import get_peft_model
#
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
# tokenizer.pad_token = tokenizer.eos_token
#
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     torch_dtype=torch.float16,
#     device_map="auto",
#     trust_remote_code=True,
# )
# model = get_peft_model(model, LORA_CONFIG)
# model.print_trainable_parameters()

# ============================================================
# CELL 4 — GRPO training loop
# ============================================================
# def forge_reward_fn(responses, prompts, ground_truths, **_):
#     """GRPO reward function — called per group of G completions."""
#     sot_labels = []
#     for group in responses:          # group = list of G responses
#         winner, _ = sot_majority_vote(group)
#         sot_labels.append(winner)
#
#     all_rewards = []
#     for group, gt, sot in zip(responses, ground_truths, sot_labels):
#         group_rewards = batch_rewards(group, [gt] * len(group),
#                                       [sot] * len(group))
#         all_rewards.append(group_rewards)
#     return all_rewards
#
# from trl import GRPOTrainer, GRPOConfig
#
# grpo_config = GRPOConfig(**GRPO_KWARGS)
# trainer = GRPOTrainer(
#     model=model,
#     args=grpo_config,
#     tokenizer=tokenizer,
#     train_dataset=dataset,
#     reward_funcs=[forge_reward_fn],
# )
# trainer.train()

# ============================================================
# CELL 5 — Evaluate + save
# ============================================================
# from sklearn.metrics import classification_report
#
# preds, gts = [], []
# for sample in eval_dataset:
#     output = model.generate(...)
#     preds.append(parse_label(tokenizer.decode(output[0])))
#     gts.append(ID2LABEL[sample["label_id"]])
#
# print(classification_report(gts, preds, target_names=LABELS))
#
# model.save_pretrained(f"{WORK_DIR}/forge_ma_final")
# tokenizer.save_pretrained(f"{WORK_DIR}/forge_ma_final")
