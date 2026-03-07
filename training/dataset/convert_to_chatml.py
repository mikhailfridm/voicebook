"""
Convert raw generated dialogs and intent pairs into LLaMA-Factory sharegpt format.

Transforms OpenAI-style tool_calls into LLaMA-Factory's function_call/observation format.

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


def transform_messages(messages: list[dict]) -> list[dict]:
    """Transform OpenAI-style messages to LLaMA-Factory sharegpt format.

    - assistant with tool_calls → assistant content + function_call messages
    - tool messages → observation messages
    """
    result = []
    for msg in messages:
        role = msg.get("role")

        if role == "assistant" and msg.get("tool_calls"):
            # If assistant has text content, add it first
            content = msg.get("content", "")
            if content:
                result.append({"role": "assistant", "content": content})

            # Add each tool call as a function_call message
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                fn_content = json.dumps({
                    "name": fn.get("name", ""),
                    "arguments": json.loads(fn["arguments"]) if isinstance(fn.get("arguments"), str) else fn.get("arguments", {}),
                }, ensure_ascii=False)
                result.append({"role": "function_call", "content": fn_content})

        elif role == "tool":
            result.append({"role": "observation", "content": msg.get("content", "")})

        else:
            result.append({"role": role, "content": msg.get("content", "")})

    # LLaMA-Factory requires first non-system message to be from user.
    # Our dialogs start with assistant greeting. Insert a trigger user message.
    first_non_system = 0
    for i, m in enumerate(result):
        if m["role"] != "system":
            first_non_system = i
            break

    if result[first_non_system]["role"] == "assistant":
        result.insert(first_non_system, {"role": "user", "content": "[Входящий звонок]"})

    return result


def validate_transformed(messages: list[dict]) -> bool:
    """Check that transformed messages are valid for LLaMA-Factory."""
    if len(messages) < 2:
        return False
    has_user = any(m["role"] == "user" for m in messages)
    has_assistant = any(m["role"] == "assistant" for m in messages)
    return has_user and has_assistant


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
    raw_examples = []

    # Load dialogs
    if Path(dialogs_path).exists():
        with open(dialogs_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                example = json.loads(line)
                raw_examples.append(example)
                transformed = transform_messages(example.get("messages", []))
                if validate_transformed(transformed):
                    all_examples.append({"messages": transformed})
                else:
                    logger.warning("Invalid dialog after transform, skipping")
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
                transformed = transform_messages(example.get("messages", []))
                if validate_transformed(transformed):
                    all_examples.append({"messages": transformed})
                    intent_count += 1
        logger.info(f"Loaded {intent_count} valid intent pairs")

    logger.info(f"Total examples: {len(all_examples)}")

    # Analyze intent distribution from raw examples
    intent_counter = Counter()
    for ex in raw_examples:
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
