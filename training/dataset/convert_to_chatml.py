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
    """Transform OpenAI-style messages to clean user/assistant sharegpt format.

    Merges function_call/observation sequences into assistant turns.
    This ensures ALL examples are valid for LLaMA-Factory training.
    The model learns dialog flow and brevity; function calling relies
    on Qwen2.5's built-in tool calling capability + system prompt.
    """
    # First pass: collect all messages with their roles
    raw = []
    for msg in messages:
        role = msg.get("role")
        if role == "assistant" and msg.get("tool_calls"):
            content = msg.get("content", "")
            # Format tool calls as text for training context
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                fn_args = fn.get("arguments", "{}")
                if isinstance(fn_args, str):
                    fn_args = json.loads(fn_args)
                fn_name = fn.get("name", "")
                # Skip extract_intent calls (internal), keep API calls
                if fn_name in ("check_slots", "create_booking", "cancel_booking", "lookup_client"):
                    args_str = ", ".join(f"{k}={v}" for k, v in fn_args.items())
                    if content:
                        content += " "
                    content += f"[{fn_name}({args_str})]"
            raw.append({"role": "assistant", "content": content})
        elif role == "tool":
            # Include API results that contain useful data
            tool_content = msg.get("content", "")
            try:
                data = json.loads(tool_content)
                if "slots" in data:
                    raw.append({"role": "tool_result", "content": tool_content})
                # Skip simple {"status":"ok"} responses
            except (json.JSONDecodeError, TypeError):
                pass
        else:
            raw.append({"role": role, "content": msg.get("content", "")})

    # Second pass: merge into clean user/gpt alternation
    result = []
    for item in raw:
        role = item["role"]
        content = item.get("content", "")

        if role == "system":
            result.append({"from": "system", "value": content})
        elif role == "user":
            result.append({"from": "human", "value": content})
        elif role == "assistant":
            if not content:
                continue  # skip empty assistant messages (pure tool calls)
            # Merge with previous gpt message if exists
            if result and result[-1]["from"] == "gpt":
                result[-1]["value"] += " " + content
            else:
                result.append({"from": "gpt", "value": content})
        elif role == "tool_result":
            # Attach to previous gpt message as context
            if result and result[-1]["from"] == "gpt":
                result[-1]["value"] += " → " + content

    # Ensure first non-system message is "human"
    first_non_system = 0
    for i, m in enumerate(result):
        if m["from"] != "system":
            first_non_system = i
            break

    if result and result[first_non_system]["from"] == "gpt":
        result.insert(first_non_system, {"from": "human", "value": "[Входящий звонок]"})

    # Clean up: remove empty values, strip whitespace
    result = [{"from": m["from"], "value": m["value"].strip()} for m in result if m["value"].strip()]

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
    if len(messages) < 2 or not has_human or not has_gpt:
        return False
    # Verify alternating human/gpt after optional system
    i = 1 if messages[0]["from"] == "system" else 0
    expected = "human"
    while i < len(messages):
        if messages[i]["from"] != expected:
            return False
        expected = "gpt" if expected == "human" else "human"
        i += 1
    return messages[-1]["from"] == "gpt"


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

    # Load dialogs (supports both 'messages' and 'conversations' formats)
    dialog_files = [p.strip() for p in dialogs_path.split(",")]
    for dpath in dialog_files:
        if not Path(dpath).exists():
            logger.warning(f"File not found: {dpath}")
            continue
        file_count = 0
        with open(dpath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                example = json.loads(line)
                raw_examples.append(example)
                # Handle both formats
                if "conversations" in example:
                    msgs = example["conversations"]
                    # Already in conversations format — normalize roles
                    transformed = []
                    for msg in msgs:
                        if "from" in msg:
                            m = dict(msg)
                        else:
                            role = ROLE_MAP.get(msg.get("role", ""), msg.get("role", ""))
                            m = {"from": role, "value": msg.get("content", "")}
                        # Merge consecutive same-role messages
                        if transformed and transformed[-1]["from"] == m["from"] and m["from"] != "system":
                            transformed[-1]["value"] += " " + m["value"]
                        else:
                            transformed.append(m)
                    # Ensure first non-system message is "human"
                    first_ns = next((i for i, m in enumerate(transformed) if m["from"] != "system"), 0)
                    if transformed and transformed[first_ns]["from"] == "gpt":
                        transformed.insert(first_ns, {"from": "human", "value": "[Входящий звонок]"})
                    if validate_transformed(transformed):
                        all_examples.append({"conversations": transformed})
                        file_count += 1
                elif "messages" in example:
                    transformed = transform_messages(example["messages"])
                    if validate_transformed(transformed):
                        all_examples.append({"conversations": transformed})
                        file_count += 1
                else:
                    logger.warning("Unknown format, skipping")
        logger.info(f"Loaded {file_count} valid dialogs from {dpath}")
    logger.info(f"Total dialogs: {len(all_examples)}")

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
