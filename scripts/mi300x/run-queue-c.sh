#!/usr/bin/env bash
# Wave C: FP8 FNUZ research. Do not call Validated without BF16 cross-check.
# Skip C4 (no official Lightning FP8). Do not pull Super BF16 / NVFP4 / Ultra.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-queue-c-manifest.txt}"
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
    --max-new-tokens 64 \
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

run_one C1 nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8 causal
run_one C2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8 causal --trust-remote-code
run_one C3 nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 causal --trust-remote-code

echo "=== QUEUE C DONE ==="
cat "$MANIFEST"
