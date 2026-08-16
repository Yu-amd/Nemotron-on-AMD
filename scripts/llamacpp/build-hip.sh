#!/usr/bin/env bash
# Build llama.cpp HIP against the host ROCm/HIP. Does not upgrade OS/ROCm/kernel.
# Intended for the MI300X host (gfx942). Do not assume this works on gfx1150 512 MB.
#
# Usage (on the Instinct host, from the repo root):
#   bash scripts/llamacpp/build-hip.sh --gpu-target gfx942

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_DIR="${REPO_ROOT}/tools/llamacpp/src"
BUILD_DIR="${REPO_ROOT}/tools/llamacpp/build/hip"
GPU_TARGET="gfx942"
TAG="b10453"
JOBS="$(nproc)"

usage() {
  cat <<'EOF'
Clone (if needed) and build llama.cpp with GGML_HIP=ON.

  --gpu-target ARCH   default gfx942
  --tag TAG           git tag to checkout, default b10453
  --jobs N            parallel build jobs
  --src DIR
  --build DIR
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpu-target) GPU_TARGET="$2"; shift 2 ;;
    --tag) TAG="$2"; shift 2 ;;
    --jobs) JOBS="$2"; shift 2 ;;
    --src) SRC_DIR="$2"; shift 2 ;;
    --build) BUILD_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! command -v hipconfig >/dev/null 2>&1; then
  echo "hipconfig not found. HIP build needs the existing ROCm toolchain; do not install a second ROCm." >&2
  exit 2
fi

if [[ ! -d "${SRC_DIR}/.git" ]]; then
  mkdir -p "$(dirname "${SRC_DIR}")"
  git clone --depth 1 --branch "${TAG}" https://github.com/ggml-org/llama.cpp.git "${SRC_DIR}"
else
  git -C "${SRC_DIR}" fetch --depth 1 origin "refs/tags/${TAG}:refs/tags/${TAG}" || true
  git -C "${SRC_DIR}" checkout "${TAG}"
fi

HIPCXX="$(hipconfig -l)/clang"
HIP_PATH="$(hipconfig -R)"
if [[ ! -f "${HIP_PATH}/lib/cmake/hip-lang/hip-lang-config.cmake" ]]; then
  for candidate in "${HIP_PATH%/core-*}" /opt/rocm /opt/rocm-7.0.2; do
    if [[ -f "${candidate}/lib/cmake/hip-lang/hip-lang-config.cmake" ]]; then
      HIP_PATH="${candidate}"
      break
    fi
  done
fi
echo "HIPCXX=${HIPCXX}"
echo "HIP_PATH=${HIP_PATH}"
echo "GPU_TARGET=${GPU_TARGET}"
echo "tag=${TAG}"

mkdir -p "${BUILD_DIR}"
export HIPCXX HIP_PATH ROCM_PATH="${HIP_PATH}"
export CPATH="${HIP_PATH}/include${CPATH:+:$CPATH}"
export CPLUS_INCLUDE_PATH="${HIP_PATH}/include${CPLUS_INCLUDE_PATH:+:$CPLUS_INCLUDE_PATH}"
HIPCXX="${HIPCXX}" HIP_PATH="${HIP_PATH}" ROCM_PATH="${HIP_PATH}" cmake -S "${SRC_DIR}" -B "${BUILD_DIR}" \
  -DGGML_HIP=ON \
  -DGPU_TARGETS="${GPU_TARGET}" \
  -DCMAKE_PREFIX_PATH="${HIP_PATH}" \
  -DCMAKE_HIP_FLAGS="-I${HIP_PATH}/include" \
  -DCMAKE_CXX_FLAGS="-I${HIP_PATH}/include" \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=ON
cmake --build "${BUILD_DIR}" --config Release -j "${JOBS}"

CLI="${BUILD_DIR}/bin/llama-cli"
if [[ -x "${CLI}" ]]; then
  echo "llama-cli=${CLI}"
else
  echo "build finished but llama-cli missing at ${CLI}" >&2
  ls -la "${BUILD_DIR}/bin" | head
  exit 1
fi
