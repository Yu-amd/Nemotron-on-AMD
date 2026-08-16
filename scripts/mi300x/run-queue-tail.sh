#!/usr/bin/env bash
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME=/root/.cache/huggingface
MANIFEST=/tmp/nemotron-queue-tail-manifest.txt
: > "$MANIFEST"
run_one() {
  local tag="$1" model="$2" task="$3"
  shift 3
  local extra="$*"
  local run_id
  run_id="$(date -u +%Y-%m-%d_%H%M%SZ)"
  echo "=== START ${tag} ${run_id} ${model} ==="
  mkdir -p "results/mi300x/${run_id}/logs"
  set +e
  # shellcheck disable=SC2086
  python scripts/mi300x/family-smoke.py --model "$model" --task "$task" \
    --output-dir "results/mi300x/${run_id}" --max-new-tokens=96 $extra \
    > "results/mi300x/${run_id}/logs/launch-nohup.out" 2>&1
  local rc=$?
  set -e
  local result=UNKNOWN
  if [[ -f "results/mi300x/${run_id}/run-metadata.json" ]]; then
    result="$(python -c "import json; print(json.load(open('results/mi300x/${run_id}/run-metadata.json')).get('result'))")"
  fi
  echo "${tag} ${run_id} rc=${rc} result=${result}" | tee -a "$MANIFEST"
  python -c "import torch; torch.cuda.is_available() and torch.cuda.empty_cache()" || true
}
run_one A9r5 nvidia/NVIDIA-Nemotron-Parse-2.0 parse --trust-remote-code
run_one B2e nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 causal --trust-remote-code --attn-implementation=eager
echo DONE
cat "$MANIFEST"
