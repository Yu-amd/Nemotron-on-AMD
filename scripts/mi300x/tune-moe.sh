#!/usr/bin/env bash
# Generate ROCm fused-MoE Triton configs for the current GPU + Nano MoE shape.
# Do not copy NVIDIA H100/B200 JSON files. Output is used via VLLM_TUNED_CONFIG_FOLDER.
#
# Usage on the MI300X host:
#   bash scripts/mi300x/tune-moe.sh
#   bash scripts/mi300x/tune-moe.sh --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
SAVE_DIR="${REPO_ROOT}/scripts/mi300x/tuned-configs"
DOCKER_IMAGE="rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0"
HF_CACHE_HOST="${HF_HOME:-${HOME}/.cache/huggingface}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --save-dir) SAVE_DIR="$2"; shift 2 ;;
    --image) DOCKER_IMAGE="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "${SAVE_DIR}"
echo "[tune-moe] model=${MODEL}"
echo "[tune-moe] save-dir=${SAVE_DIR}"
echo "[tune-moe] this can take a long time. It is kernel autotune, not a Nemotron quality test."

docker run --rm \
  --device /dev/kfd \
  --device /dev/dri \
  --network=host \
  --ipc=host \
  --group-add=video \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v "${HF_CACHE_HOST}:/root/.cache/huggingface" \
  -v "${REPO_ROOT}:/workspace" \
  -e HF_HOME=/root/.cache/huggingface \
  -e FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE \
  -w /workspace \
  --entrypoint python3 \
  "${DOCKER_IMAGE}" \
  /app/vllm/benchmarks/kernels/benchmark_moe.py \
  --model "${MODEL}" \
  --tp-size 1 \
  --dtype auto \
  --tune \
  --save-dir /workspace/scripts/mi300x/tuned-configs \
  --trust-remote-code

ls -la "${SAVE_DIR}"
