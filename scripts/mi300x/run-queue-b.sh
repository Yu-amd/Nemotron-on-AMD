#!/usr/bin/env bash
# Wave B: Lightning 30B BF16 then Omni 30B BF16. Transformers smoke first.
# No FlashInfer. New timestamp per model. Do not download Super BF16 / Ultra / NVFP4.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-queue-b-manifest.txt}"
: > "$MANIFEST"

run_one() {
  local tag="$1" model="$2" task="$3"
  local extra="${4:-}"
  local run_id
  run_id="$(date -u +%Y-%m-%d_%H%M%SZ)"
  echo "=== START ${tag} ${run_id} ${model} task=${task} ==="
  mkdir -p "results/mi300x/${run_id}/logs"
  set +e
  # shellcheck disable=SC2086
  python scripts/mi300x/family-smoke.py \
    --model "$model" \
    --task "$task" \
    --max-new-tokens 96 \
    --output-dir "results/mi300x/${run_id}" \
    $extra \
    > "results/mi300x/${run_id}/logs/launch-nohup.out" 2>&1
  local rc=$?
  set -e
  local result="UNKNOWN"
  if [[ -f "results/mi300x/${run_id}/run-metadata.json" ]]; then
    result="$(python -c "import json; print(json.load(open('results/mi300x/${run_id}/run-metadata.json')).get('result'))")"
  fi
  echo "${tag} ${run_id} rc=${rc} result=${result} ${model}" | tee -a "$MANIFEST"
  python - << 'PY' || true
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
PY
}

run_one B1 nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 causal
run_one B2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 causal --trust-remote-code

echo "=== QUEUE B DONE ==="
cat "$MANIFEST"
