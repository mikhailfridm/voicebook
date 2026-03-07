"""
Merge LoRA adapter into base Qwen2.5-14B model for vLLM deployment.

Usage:
    python merge_lora.py \
        --base-model Qwen/Qwen2.5-14B-Instruct \
        --lora-path ../../models/voicebook-dpo \
        --output ../../models/voicebook-qwen2.5-14b
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(base_model: str, lora_path: str, output_path: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    logger.info(f"Loading base model: {base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    logger.info(f"Loading LoRA adapter: {lora_path}")
    model = PeftModel.from_pretrained(model, lora_path)

    logger.info("Merging LoRA weights...")
    model = model.merge_and_unload()

    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving merged model to: {output}")
    model.save_pretrained(output)
    tokenizer.save_pretrained(output)

    logger.info("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-14B-Instruct")
    parser.add_argument("--lora-path", default="../../models/voicebook-dpo")
    parser.add_argument("--output", default="../../models/voicebook-qwen2.5-14b")
    args = parser.parse_args()

    main(args.base_model, args.lora_path, args.output)
