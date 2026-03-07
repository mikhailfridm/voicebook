"""
Convert raw generated dialogs and intent pairs into Qwen2.5 ChatML format.

Combines dialogs + intent pairs, validates format, splits into train/eval.

Usage:
    python convert_to_chatml.py \
        --dialogs sft_dialogs.jsonl \
        --intents raw/intent_pairs.jsonl \
        --dpo dpo_pairs.jsonl \
        --output-dir processed/
"""

import argparse
import json
import random
import logging
from pathlib import Path
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_message(msg: dict) -> bool:
    """Check that a message has valid structure."""
    role = msg.get("role")
    if role not in ("system", "user", "assistant", "tool"):
        return False
    if role == "assistant":
        # Must have content or tool_calls
        if not msg.get("content") and not msg.get("tool_calls"):
            return False
    if role == "tool":
        if "content" not in msg:
            return False
    return True


def validate_example(example: dict) -> bool:
    """Validate a complete training example."""
    messages = example.get("messages", [])
    if len(messages) < 2:
        return False
    for msg in messages:
        if not validate_message(msg):
            return False
    return True


def extract_intents(example: dict) -> list[str]:
    """Extract all intents from tool calls in an example."""
    intents = []
    for msg in example.get("messages", []):
        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            if fn.get("name") == "extract_intent":
                args = fn.get("arguments", "{}")
                if isinstance(args, str):
                    args = json.loads(args)
                intent = args.get("intent")
                if intent:
                    intents.append(intent)
    return intents


def main(dialogs_path: str, intents_path: str, output_dir: str, dpo_path: str = ""):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    all_examples = []

    # Load dialogs
    if Path(dialogs_path).exists():
        with open(dialogs_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                example = json.loads(line)
                if validate_example(example):
                    all_examples.append(example)
                else:
                    logger.warning(f"Invalid dialog example, skipping")
        logger.info(f"Loaded {len(all_examples)} valid dialogs")

    # Load intent pairs
    intent_count = 0
    if Path(intents_path).exists():
        with open(intents_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                example = json.loads(line)
                if validate_example(example):
                    all_examples.append(example)
                    intent_count += 1
        logger.info(f"Loaded {intent_count} valid intent pairs")

    logger.info(f"Total examples: {len(all_examples)}")

    # Analyze intent distribution
    intent_counter = Counter()
    for ex in all_examples:
        for intent in extract_intents(ex):
            intent_counter[intent] += 1

    logger.info("Intent distribution:")
    for intent, count in intent_counter.most_common():
        logger.info(f"  {intent}: {count}")

    # Shuffle and split 90/10
    random.shuffle(all_examples)
    split_idx = int(len(all_examples) * 0.9)
    train_set = all_examples[:split_idx]
    eval_set = all_examples[split_idx:]

    # Save
    train_path = output / "train.jsonl"
    eval_path = output / "eval.jsonl"

    with open(train_path, "w", encoding="utf-8") as f:
        for ex in train_set:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(eval_path, "w", encoding="utf-8") as f:
        for ex in eval_set:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    logger.info(f"Train: {len(train_set)} examples -> {train_path}")
    logger.info(f"Eval: {len(eval_set)} examples -> {eval_path}")

    # Process DPO pairs if provided
    if dpo_path and Path(dpo_path).exists():
        dpo_examples = []
        with open(dpo_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ex = json.loads(line)
                if "prompt" in ex and "chosen" in ex and "rejected" in ex:
                    dpo_examples.append(ex)

        random.shuffle(dpo_examples)
        dpo_split = int(len(dpo_examples) * 0.9)
        dpo_train = dpo_examples[:dpo_split]
        dpo_eval = dpo_examples[dpo_split:]

        dpo_train_path = output / "dpo_train.jsonl"
        dpo_eval_path = output / "dpo_eval.jsonl"

        with open(dpo_train_path, "w", encoding="utf-8") as f:
            for ex in dpo_train:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        with open(dpo_eval_path, "w", encoding="utf-8") as f:
            for ex in dpo_eval:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        logger.info(f"DPO Train: {len(dpo_train)} -> {dpo_train_path}")
        logger.info(f"DPO Eval: {len(dpo_eval)} -> {dpo_eval_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialogs", default="sft_dialogs.jsonl")
    parser.add_argument("--intents", default="raw/intent_pairs.jsonl")
    parser.add_argument("--dpo", default="dpo_pairs.jsonl")
    parser.add_argument("--output-dir", default="processed/")
    args = parser.parse_args()

    main(args.dialogs, args.intents, args.output_dir, args.dpo)
