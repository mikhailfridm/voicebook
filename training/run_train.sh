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
cd "$SCRIPT_DIR"

# ─── Step 0: Install dependencies ────────────────────────────────
install_deps() {
    echo "=== Installing dependencies ==="
    pip install -r finetune/requirements-train.txt
    echo "Done."
}

# ─── Step 1: Prepare dataset ─────────────────────────────────────
prepare_data() {
    echo "=== Preparing dataset ==="
    cd dataset
    python convert_to_chatml.py \
        --dialogs sft_dialogs.jsonl \
        --intents raw/intent_pairs.jsonl \
        --dpo dpo_pairs.jsonl \
        --output-dir processed/
    cd ..
    echo "=== Dataset ready ==="
}

# ─── Step 2: SFT Training ────────────────────────────────────────
run_sft() {
    echo "=== Starting SFT training ==="
    cd finetune
    llamafactory-cli train config.yaml
    cd ..
    echo "=== SFT complete ==="
}

# ─── Step 3: DPO Training ────────────────────────────────────────
run_dpo() {
    echo "=== Starting DPO training ==="
    cd finetune
    llamafactory-cli train config_dpo.yaml
    cd ..
    echo "=== DPO complete ==="
}

# ─── Step 4: Merge LoRA ──────────────────────────────────────────
merge_model() {
    echo "=== Merging LoRA into base model ==="
    cd finetune
    python merge_lora.py
    cd ..
    echo "=== Merged model saved to models/voicebook-qwen2.5-14b ==="
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
        echo "Merged model: models/voicebook-qwen2.5-14b"
        echo ""
        echo "To serve with vLLM:"
        echo "  vllm serve models/voicebook-qwen2.5-14b --dtype bfloat16 --max-model-len 4096"
        ;;
    *)
        echo "Usage: $0 {install|prepare|sft|dpo|merge|all}"
        exit 1
        ;;
esac
