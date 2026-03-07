#!/bin/bash
# VoiceBook Training Pipeline
# Run on a GPU server with at least 40GB VRAM (A100/A6000/etc.)
#
# Usage:
#   chmod +x run_train.sh
#   ./run_train.sh          # full pipeline
#   ./run_train.sh prepare  # only prepare data
#   ./run_train.sh sft      # only SFT training
#   ./run_train.sh dpo      # only DPO training
#   ./run_train.sh merge    # only merge LoRA

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATASET_DIR="$SCRIPT_DIR/dataset"
FINETUNE_DIR="$SCRIPT_DIR/finetune"
MODELS_DIR="$SCRIPT_DIR/../models"

# ─── Step 0: Install dependencies ────────────────────────────────
install_deps() {
    echo "=== Installing dependencies ==="
    pip install -r "$FINETUNE_DIR/requirements-train.txt"
    echo "Done."
}

# ─── Step 1: Prepare dataset ─────────────────────────────────────
prepare_data() {
    echo "=== Preparing dataset ==="
    python "$DATASET_DIR/convert_to_chatml.py" \
        --dialogs "$DATASET_DIR/sft_dialogs.jsonl" \
        --intents "$DATASET_DIR/raw/intent_pairs.jsonl" \
        --dpo "$DATASET_DIR/dpo_pairs.jsonl" \
        --output-dir "$DATASET_DIR/processed/"

    # Create dataset_info.json for LLaMA-Factory
    cat > "$DATASET_DIR/processed/dataset_info.json" << 'DINFO'
{
  "train": {
    "file_name": "train.jsonl",
    "formatting": "sharegpt",
    "columns": {"conversations": "messages"},
    "tags": {"role_tag": "role", "content_tag": "content", "user_tag": "user", "assistant_tag": "assistant", "system_tag": "system", "function_tag": "function_call", "observation_tag": "observation"}
  },
  "eval": {
    "file_name": "eval.jsonl",
    "formatting": "sharegpt",
    "columns": {"conversations": "messages"},
    "tags": {"role_tag": "role", "content_tag": "content", "user_tag": "user", "assistant_tag": "assistant", "system_tag": "system", "function_tag": "function_call", "observation_tag": "observation"}
  },
  "dpo_train": {
    "file_name": "dpo_train.jsonl",
    "formatting": "sharegpt",
    "ranking": true,
    "columns": {"messages": "prompt", "chosen": "chosen", "rejected": "rejected"},
    "tags": {"role_tag": "role", "content_tag": "content", "user_tag": "user", "assistant_tag": "assistant", "system_tag": "system"}
  },
  "dpo_eval": {
    "file_name": "dpo_eval.jsonl",
    "formatting": "sharegpt",
    "ranking": true,
    "columns": {"messages": "prompt", "chosen": "chosen", "rejected": "rejected"},
    "tags": {"role_tag": "role", "content_tag": "content", "user_tag": "user", "assistant_tag": "assistant", "system_tag": "system"}
  }
}
DINFO
    echo "=== Dataset ready ==="
}

# ─── Step 2: SFT Training ────────────────────────────────────────
run_sft() {
    echo "=== Starting SFT training ==="
    llamafactory-cli train "$FINETUNE_DIR/config.yaml"
    echo "=== SFT complete ==="
}

# ─── Step 3: DPO Training ────────────────────────────────────────
run_dpo() {
    echo "=== Starting DPO training ==="
    llamafactory-cli train "$FINETUNE_DIR/config_dpo.yaml"
    echo "=== DPO complete ==="
}

# ─── Step 4: Merge LoRA ──────────────────────────────────────────
merge_model() {
    echo "=== Merging LoRA into base model ==="
    python "$FINETUNE_DIR/merge_lora.py" \
        --lora-path "$MODELS_DIR/voicebook-dpo" \
        --output "$MODELS_DIR/voicebook-qwen2.5-14b"
    echo "=== Merged model saved to $MODELS_DIR/voicebook-qwen2.5-14b ==="
}

# ─── Main ─────────────────────────────────────────────────────────
case "${1:-all}" in
    install)
        install_deps
        ;;
    prepare)
        prepare_data
        ;;
    sft)
        run_sft
        ;;
    dpo)
        run_dpo
        ;;
    merge)
        merge_model
        ;;
    all)
        install_deps
        prepare_data
        run_sft
        run_dpo
        merge_model
        echo ""
        echo "=== Training pipeline complete! ==="
        echo "Merged model: $MODELS_DIR/voicebook-qwen2.5-14b"
        echo ""
        echo "To serve with vLLM:"
        echo "  vllm serve $MODELS_DIR/voicebook-qwen2.5-14b --dtype bfloat16 --max-model-len 4096"
        ;;
    *)
        echo "Usage: $0 {install|prepare|sft|dpo|merge|all}"
        exit 1
        ;;
esac
