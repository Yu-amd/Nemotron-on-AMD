#!/usr/bin/env bash
# Real Wave B/C after argparse extra-arg bug. Keep first UNKNOWN/FAIL dirs.
# Use --max-new-tokens=96 as a single argv token. No FlashInfer. No Super BF16.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
export TRANSFORMERS_ATTN_IMPLEMENTATION=sdpa
MANIFEST="${1:-/tmp/nemotron-queue-bc-manifest.txt}"
: > "$MANIFEST"

python - << 'PY'
import torch
print("torch", torch.__version__, "hip", torch.version.hip)
assert torch.version.hip
PY
python -m pip install -q ftfy regex
python - << 'PY'
try:
    import open_clip
    print("open_clip", getattr(open_clip, "__version__", "ok"))
except Exception as e:
    print("open_clip still missing", type(e).__name__, e)
PY

run_one() {
  local tag="$1" model="$2" task="$3"
  shift 3
  local extra="$*"
  local run_id
  run_id="$(date -u +%Y-%m-%d_%H%M%SZ)"
  echo "=== START ${tag} ${run_id} ${model} task=${task} extra=${extra} ==="
  mkdir -p "results/mi300x/${run_id}/logs"
  set +e
  # shellcheck disable=SC2086
  python scripts/mi300x/family-smoke.py \
    --model "$model" \
    --task "$task" \
    --output-dir "results/mi300x/${run_id}" \
    --max-new-tokens=96 \
    --attn-implementation=sdpa \
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

run_one A9r4 nvidia/NVIDIA-Nemotron-Parse-2.0 parse --trust-remote-code
run_one B1 nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 causal
run_one B2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 causal --trust-remote-code
run_one C1 nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8 causal
run_one C2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8 causal --trust-remote-code
run_one C3 nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 causal --trust-remote-code

echo "=== QUEUE BC DONE ==="
cat "$MANIFEST"
