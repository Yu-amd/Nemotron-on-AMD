#!/usr/bin/env bash
# Sequential MI300X family-smoke jobs. Each gets its own timestamped results dir.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-queue-manifest.txt}"
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

run_one A3 nvidia/Nemotron-3-Embed-8B-BF16 embed
run_one A4 nvidia/llama-nemotron-rerank-1b-v2 rerank
run_one A5 nvidia/llama-nemotron-embed-vl-1b-v2 vl-embed
run_one A6 nvidia/llama-nemotron-rerank-vl-1b-v2 rerank
run_one A7a nvidia/llama-nemotron-colembed-vl-3b-v2 vl-embed
run_one A7b nvidia/nemotron-colembed-vl-4b-v2 vl-embed
run_one A7c nvidia/nemotron-colembed-vl-8b-v2 vl-embed
run_one A8 nvidia/omni-embed-nemotron-3b vl-embed
run_one A9 nvidia/NVIDIA-Nemotron-Parse-2.0 parse --trust-remote-code
run_one A10 nvidia/nemotron-3.5-asr-streaming-0.6b asr --trust-remote-code
run_one A11 nvidia/Nemotron-3.5-Content-Safety safety --trust-remote-code
run_one A12 nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3 safety

echo "=== QUEUE BATCH DONE ==="
cat "$MANIFEST"
