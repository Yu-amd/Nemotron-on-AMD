#!/usr/bin/env bash
# Remaining 1× MI300X VF checkpoints that still fit this GPU.
# Do not download Super BF16, Ultra, or NVFP4.
# Do not copy FlashInfer / NVFP4 flags.
set -euo pipefail
cd /root/Nemotron-on-AMD
source .venv-mi300x/bin/activate
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
MANIFEST="${1:-/tmp/nemotron-fit1x-manifest.txt}"
: > "$MANIFEST"

python - << 'PY'
import torch
print("preflight torch", torch.__version__, "hip", torch.version.hip, "avail", torch.cuda.is_available())
assert torch.version.hip
assert "rocm" in torch.__version__.lower()
PY

run_tf() {
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
    ${extra} \
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

wait_health() {
  local url="$1" tries="$2"
  local i
  for i in $(seq 1 "${tries}"); do
    if python - << PY
import urllib.request, sys
try:
    urllib.request.urlopen("${url}", timeout=5)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
    then
      echo "health-ok after ${i} tries ${url}"
      return 0
    fi
    sleep 10
  done
  return 1
}

run_vllm() {
  local tag="$1" model="$2" served="$3"
  local run_id
  run_id="$(date -u +%Y-%m-%d_%H%M%SZ)"
  local out="results/mi300x/${run_id}"
  echo "=== START ${tag} vLLM ${run_id} ${model} ==="
  mkdir -p "${out}/vllm/logs" "${out}/logs"
  docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true
  set +e
  nohup bash scripts/mi300x/launch-vllm.sh \
    --docker \
    --model "$model" \
    --served-name "$served" \
    --port 8000 \
    --max-model-len 8192 \
    --output-dir "${out}/vllm" \
    > "${out}/logs/launch-nohup.out" 2>&1 &
  echo $! > "${out}/logs/vllm-launch.pid"
  set -e
  if wait_health "http://127.0.0.1:8000/health" 180; then
    set +e
    python scripts/mi300x/test-openai-api.py \
      --base-url http://127.0.0.1:8000/v1 \
      --model "$served" \
      --output-dir "$out" \
      > "${out}/logs/openai-api.out" 2>&1
    local rc=$?
    set -e
    echo "${tag} ${run_id} vllm-api rc=${rc} ${model}" | tee -a "$MANIFEST"
  else
    echo "${tag} ${run_id} vllm-health TIMEOUT ${model}" | tee -a "$MANIFEST"
    tail -n 80 "${out}/vllm/logs/vllm.stderr.log" >> "${out}/logs/launch-nohup.out" || true
  fi
  docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true
  python - << 'PY' || true
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
PY
}

# Tracked 1×-fit Transformers gaps (not NVFP4, not Super BF16, not Ultra).
run_tf D1 nvidia/NVIDIA-Nemotron-3-Nano-4B-FP8 causal --max-new-tokens=96
run_tf D2 nvidia/llama-nemotron-embed-vl-1b-v2-fp8 vl-embed --trust-remote-code
run_tf D3 nvidia/llama-nemotron-rerank-vl-1b-v2-fp8 rerank --trust-remote-code

# vLLM only after Transformers already Validated on this VF.
run_vllm E1 nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16 nemotron-nano-4b-bf16
run_vllm E2 nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 nemotron-lightning-bf16

echo "=== FIT-1X QUEUE DONE ==="
cat "$MANIFEST"
