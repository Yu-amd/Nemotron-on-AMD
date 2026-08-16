#!/usr/bin/env bash
# Launch vLLM for Nemotron on one MI300X GPU.
#
# Conservative defaults. NVIDIA cookbook flags that are CUDA/FlashInfer/NVFP4
# specific are documented, not silently copied.
#
# Official Nano BF16 model card (checked 2026-08-15):
#   pip install -U "vllm>=0.12.0"
#   wget .../nano_v3_reasoning_parser.py
#   vllm serve nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
#     --trust-remote-code \
#     --enable-auto-tool-choice \
#     --tool-call-parser qwen3_coder \
#     --reasoning-parser-plugin nano_v3_reasoning_parser.py \
#     --reasoning-parser nano_v3
#
# Those NVIDIA examples were written for CUDA. On ROCm:
#   - Install vLLM from a ROCm wheel, AMD CDNA image, or vllm/vllm-openai-rocm.
#     Never CUDA wheels. On this MI300X host (HIP 7.14, Python 3.12), AMD's
#     documented ROCm 7.14 vLLM wheel is cp314, so --docker is the pip-free path.
#   - Start with a short --max-model-len (8192), not 256k or 1M.
#   - Drop NVIDIA-only env vars such as VLLM_USE_FLASHINFER_MOE_FP4.
#
# Usage:
#   bash scripts/mi300x/launch-vllm.sh --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
#   bash scripts/mi300x/launch-vllm.sh --docker --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
#   bash scripts/mi300x/launch-vllm.sh --model <MODEL> --port 8000 --max-model-len 8192
#
# Do not run this until Transformers smoke tests succeed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PORT=8000
MAX_MODEL_LEN=8192
TP_SIZE=1
SERVED_NAME="nemotron-nano-bf16"
OUT_DIR=""
REASONING_PARSER="nano_v3"
TOOL_PARSER="qwen3_coder"
GPU_MEM_UTIL="0.80"
REVISION=""
TUNED_CONFIG_DIR="${REPO_ROOT}/scripts/mi300x/tuned-configs"
EXTRA_ARGS=()
DRY_RUN=0
USE_DOCKER=0
# AMD ROCm 7.14 Instinct (gfx942) image, checked 2026-08-15:
# https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/inference/vllm.html
DOCKER_IMAGE="rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0"
DOCKER_NAME="nemotron-nano-vllm"

usage() {
  cat <<'EOF'
Launch vLLM for one MI300X. Conservative Nemotron Nano defaults.

  --model ID
  --port N
  --max-model-len N          default 8192; do not start at 1M
  --tp N                     tensor parallel size, default 1
  --served-name NAME
  --output-dir DIR           logs + command capture
  --gpu-memory-utilization F default 0.80
  --reasoning-parser NAME    default nano_v3
  --tool-parser NAME         default qwen3_coder
  --revision HASH            Hugging Face snapshot; default is cache refs/main if present
  --tuned-config-dir DIR     VLLM_TUNED_CONFIG_FOLDER (MoE JSON from tune-moe.sh)
  --docker                   serve inside the AMD ROCm 7.14 CDNA vLLM image
  --image NAME               override docker image
  --dry-run                  print the command only
  extra args after -- are passed through to vllm
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --max-model-len) MAX_MODEL_LEN="$2"; shift 2 ;;
    --tp) TP_SIZE="$2"; shift 2 ;;
    --served-name) SERVED_NAME="$2"; shift 2 ;;
    --output-dir) OUT_DIR="$2"; shift 2 ;;
    --gpu-memory-utilization) GPU_MEM_UTIL="$2"; shift 2 ;;
    --reasoning-parser) REASONING_PARSER="$2"; shift 2 ;;
    --tool-parser) TOOL_PARSER="$2"; shift 2 ;;
    --revision) REVISION="$2"; shift 2 ;;
    --tuned-config-dir) TUNED_CONFIG_DIR="$2"; shift 2 ;;
    --docker) USE_DOCKER=1; shift ;;
    --image) DOCKER_IMAGE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; EXTRA_ARGS+=("$@"); break ;;
    *) EXTRA_ARGS+=("$1"); shift ;;
  esac
done

STAMP="$(date -u +%Y-%m-%d_%H%M%S)Z"
if [[ -z "${OUT_DIR}" ]]; then
  OUT_DIR="${REPO_ROOT}/results/mi300x/${STAMP}/vllm"
fi
mkdir -p "${OUT_DIR}/logs"

HF_CACHE_HOST="${HF_HOME:-${HOME}/.cache/huggingface}"
if [[ -z "${REVISION}" ]]; then
  MODEL_CACHE_NAME="models--${MODEL//\//--}"
  MAIN_REF="${HF_CACHE_HOST}/hub/${MODEL_CACHE_NAME}/refs/main"
  if [[ -f "${MAIN_REF}" ]]; then
    REVISION="$(tr -d '[:space:]' < "${MAIN_REF}")"
    echo "[launch-vllm] using cached snapshot revision=${REVISION}"
  fi
fi

PARSER_SRC=""
for candidate in \
  "${REPO_ROOT}/scripts/mi300x/nano_v3_reasoning_parser.py" \
  ./nano_v3_reasoning_parser.py
do
  if [[ -f "${candidate}" ]]; then
    PARSER_SRC="${candidate}"
    break
  fi
done

CMD=(vllm serve "${MODEL}"
  --host 0.0.0.0
  --port "${PORT}"
  --served-model-name "${SERVED_NAME}"
  --dtype bfloat16
  --tensor-parallel-size "${TP_SIZE}"
  --max-model-len "${MAX_MODEL_LEN}"
  --gpu-memory-utilization "${GPU_MEM_UTIL}"
  --trust-remote-code
  --enable-auto-tool-choice
  --tool-call-parser "${TOOL_PARSER}"
  --reasoning-parser "${REASONING_PARSER}"
  --generation-config vllm
)

if [[ -n "${REVISION}" ]]; then
  CMD+=(--revision "${REVISION}")
fi

if [[ -n "${PARSER_SRC}" ]]; then
  PLUGIN_ARG="${PARSER_SRC}"
  if [[ "${USE_DOCKER}" -eq 1 ]]; then
    PLUGIN_ARG="/workspace/scripts/mi300x/nano_v3_reasoning_parser.py"
  fi
  CMD+=(--reasoning-parser-plugin "${PLUGIN_ARG}")
else
  echo "[launch-vllm] WARNING: nano_v3_reasoning_parser.py not found locally."
  echo "Download it from the official Nano BF16 repo before expecting reasoning parsing to work:"
  echo "  wget https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16/resolve/main/nano_v3_reasoning_parser.py"
fi

if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  CMD+=("${EXTRA_ARGS[@]}")
fi

HF_CACHE_HOST="${HF_HOME:-${HOME}/.cache/huggingface}"
DOCKER_ENV=(-e HF_HOME=/root/.cache/huggingface -e FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE)
if [[ -d "${TUNED_CONFIG_DIR}" ]] && compgen -G "${TUNED_CONFIG_DIR}/*.json" > /dev/null; then
  echo "[launch-vllm] using tuned MoE configs in ${TUNED_CONFIG_DIR}"
  export VLLM_TUNED_CONFIG_FOLDER="${TUNED_CONFIG_DIR}"
  if [[ "${USE_DOCKER}" -eq 1 ]]; then
    DOCKER_ENV+=(-e VLLM_TUNED_CONFIG_FOLDER=/workspace/scripts/mi300x/tuned-configs)
  fi
fi
LAUNCH_CMD=("${CMD[@]}")
if [[ "${USE_DOCKER}" -eq 1 ]]; then
  LAUNCH_CMD=(
    docker run --rm
    --name "${DOCKER_NAME}"
    --device /dev/kfd
    --device /dev/dri
    --network=host
    --ipc=host
    --group-add=video
    --cap-add=SYS_PTRACE
    --security-opt seccomp=unconfined
    -v "${HF_CACHE_HOST}:/root/.cache/huggingface"
    -v "${REPO_ROOT}:/workspace"
    "${DOCKER_ENV[@]}"
    -w /workspace
    "${DOCKER_IMAGE}"
    "${CMD[@]}"
  )
fi

{
  echo "timestamp_utc=${STAMP}"
  echo "model=${MODEL}"
  echo "max_model_len=${MAX_MODEL_LEN}"
  echo "tp=${TP_SIZE}"
  echo "port=${PORT}"
  echo "parser_plugin=${PARSER_SRC:-missing}"
  echo "revision=${REVISION:-unset}"
  echo "generation_config=vllm"
  echo "tuned_config_dir=${VLLM_TUNED_CONFIG_FOLDER:-none}"
  echo "docker=${USE_DOCKER}"
  echo "image=${DOCKER_IMAGE}"
  echo "NOTE: NVIDIA CUDA-only flags intentionally omitted (FlashInfer, NVFP4, TRT-LLM)."
  echo
  printf 'command:'
  printf ' %q' "${LAUNCH_CMD[@]}"
  printf '\n'
} | tee "${OUT_DIR}/launch-command.txt"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "[launch-vllm] dry-run only"
  exit 0
fi

if [[ "${USE_DOCKER}" -eq 1 ]]; then
  docker rm -f "${DOCKER_NAME}" >/dev/null 2>&1 || true
fi

echo
echo "[launch-vllm] starting. logs: ${OUT_DIR}/logs/vllm.stdout.log"
echo "[launch-vllm] this is an engineering serve test, not an Optimized or Production-ready claim."
exec "${LAUNCH_CMD[@]}" > >(tee "${OUT_DIR}/logs/vllm.stdout.log") 2> >(tee "${OUT_DIR}/logs/vllm.stderr.log" >&2)
