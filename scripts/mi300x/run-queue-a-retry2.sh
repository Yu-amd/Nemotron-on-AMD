#!/usr/bin/env bash
# Second retry: VL processors + einops. Keep earlier FAIL/BLOCKED dirs.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-queue-retry2-manifest.txt}"
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
    --output-dir "results/mi300x/${run_id}" \
    --trust-remote-code \
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

run_one A5r2 nvidia/llama-nemotron-embed-vl-1b-v2 vl-embed
run_one A7br2 nvidia/nemotron-colembed-vl-4b-v2 vl-embed
run_one A7cr2 nvidia/nemotron-colembed-vl-8b-v2 vl-embed
run_one A8r2 nvidia/omni-embed-nemotron-3b vl-embed
run_one A9r2 nvidia/NVIDIA-Nemotron-Parse-2.0 parse

echo "=== QUEUE A RETRY2 DONE ==="
cat "$MANIFEST"
