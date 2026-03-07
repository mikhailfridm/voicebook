"""
Convert raw generated dialogs into LLaMA-Factory default sharegpt format.

Output format per message: {"from": "human/gpt/system/function_call/observation", "value": "..."}
Key: "conversations" (LLaMA-Factory default)

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

# Map our roles to LLaMA-Factory sharegpt defaults
ROLE_MAP = {
    "system": "system",
    "user": "human",
    "assistant": "gpt",
    "function_call": "function_call",
    "observation": "observation",
}


def transform_messages(messages: list[dict]) -> list[dict]:
    """Transform OpenAI-style messages to LLaMA-Factory default sharegpt format."""
    result = []
    for msg in messages:
        role = msg.get("role")

        if role == "assistant" and msg.get("tool_calls"):
            content = msg.get("content", "")
            if content:
                result.append({"from": "gpt", "value": content})

            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                fn_content = json.dumps({
                    "name": fn.get("name", ""),
                    "arguments": json.loads(fn["arguments"]) if isinstance(fn.get("arguments"), str) else fn.get("arguments", {}),
                }, ensure_ascii=False)
                result.append({"from": "function_call", "value": fn_content})

        elif role == "tool":
            result.append({"from": "observation", "value": msg.get("content", "")})

        else:
            sharegpt_role = ROLE_MAP.get(role, role)
            result.append({"from": sharegpt_role, "value": msg.get("content", "")})

    # LLaMA-Factory requires first non-system message to be "human".
    first_non_system = 0
    for i, m in enumerate(result):
        if m["from"] != "system":
            first_non_system = i
            break

    if result[first_non_system]["from"] == "gpt":
        result.insert(first_non_system, {"from": "human", "value": "[Входящий звонок]"})

    return result


def transform_dpo(example: dict) -> dict:
    """Transform DPO pair to sharegpt format.

    LLaMA-Factory expects chosen/rejected as single message dicts, not lists.
    """
    prompt = []
    for msg in example.get("prompt", []):
        role = ROLE_MAP.get(msg["role"], msg["role"])
        prompt.append({"from": role, "value": msg["content"]})

    # Ensure prompt starts with human
    first_non_system = 0
    for i, m in enumerate(prompt):
        if m["from"] != "system":
            first_non_system = i
            break
    if prompt and prompt[first_non_system]["from"] != "human":
        prompt.insert(first_non_system, {"from": "human", "value": "[Входящий звонок]"})

    # chosen/rejected must be single message dicts
    chosen_msgs = example.get("chosen", [])
    rejected_msgs = example.get("rejected", [])

    chosen = {"from": "gpt", "value": chosen_msgs[0]["content"]} if chosen_msgs else {"from": "gpt", "value": ""}
    rejected = {"from": "gpt", "value": rejected_msgs[0]["content"]} if rejected_msgs else {"from": "gpt", "value": ""}

    return {"conversations": prompt, "chosen": chosen, "rejected": rejected}


def validate_transformed(messages: list[dict]) -> bool:
    has_human = any(m["from"] == "human" for m in messages)
    has_gpt = any(m["from"] == "gpt" for m in messages)
    return len(messages) >= 2 and has_human and has_gpt


def extract_intents(example: dict) -> list[str]:
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
                    all_examples.append({"conversations": transformed})
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
                    all_examples.append({"conversations": transformed})
                    intent_count += 1
        logger.info(f"Loaded {intent_count} valid intent pairs")

    logger.info(f"Total examples: {len(all_examples)}")

    # Analyze intent distribution
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

    # Process DPO pairs
    if dpo_path and Path(dpo_path).exists():
        dpo_examples = []
        with open(dpo_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ex = json.loads(line)
                if "prompt" in ex and "chosen" in ex and "rejected" in ex:
                    dpo_examples.append(transform_dpo(ex))

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
