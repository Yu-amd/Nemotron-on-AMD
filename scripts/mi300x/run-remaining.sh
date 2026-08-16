#!/usr/bin/env bash
# Overnight remainder: A5/A9 retries, then Lightning/Omni BF16, then FP8 FNUZ.
# Do not copy FlashInfer. Do not download Super BF16 / Ultra / NVFP4.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-remaining-manifest.txt}"
: > "$MANIFEST"

python - << 'PY'
import torch
print("preflight torch", torch.__version__, "hip", torch.version.hip, "avail", torch.cuda.is_available())
assert torch.version.hip
assert "rocm" in torch.__version__.lower()
PY

# Parse RADIO submodule. Never let pip replace ROCm torch.
python -m pip install --no-deps 'open-clip-torch' || python -m pip install --no-deps 'open_clip_torch' || true
python - << 'PY'
import torch
print("post-openclip torch", torch.__version__, "hip", torch.version.hip)
try:
    import open_clip
    print("open_clip ok", getattr(open_clip, "__version__", "?"))
except Exception as e:
    print("open_clip missing", type(e).__name__, e)
PY

run_one() {
  local tag="$1" model="$2" task="$3"
  shift 3
  local extra="$*"
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

run_one A5r3 nvidia/llama-nemotron-embed-vl-1b-v2 vl-embed --trust-remote-code
run_one A9r3 nvidia/NVIDIA-Nemotron-Parse-2.0 parse --trust-remote-code
run_one B1 nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 causal --max-new-tokens 96
run_one B2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 causal --trust-remote-code --max-new-tokens 96
run_one C1 nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8 causal --max-new-tokens 64
run_one C2 nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8 causal --trust-remote-code --max-new-tokens 64
run_one C3 nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 causal --trust-remote-code --max-new-tokens 64

echo "=== REMAINING QUEUE DONE ==="
cat "$MANIFEST"
