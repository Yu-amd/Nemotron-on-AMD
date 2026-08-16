#!/usr/bin/env bash
# Download a pinned official llama.cpp GitHub release tarball into tools/llamacpp/.
# Does not upgrade OS, ROCm, or kernel.
#
# Usage:
#   bash scripts/llamacpp/fetch-release.sh --backend cpu --tag b10453
#   bash scripts/llamacpp/fetch-release.sh --backend vulkan --tag b10453

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TAG="b10453"
BACKEND="cpu"

usage() {
  cat <<'EOF'
Fetch an official ggml-org/llama.cpp Ubuntu x64 release.

  --tag TAG          default b10453
  --backend NAME     cpu | vulkan
  --dest DIR         override extract directory
EOF
}

DEST=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="$2"; shift 2 ;;
    --backend) BACKEND="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

case "${BACKEND}" in
  cpu) ASSET="llama-${TAG}-bin-ubuntu-x64.tar.gz" ;;
  vulkan) ASSET="llama-${TAG}-bin-ubuntu-vulkan-x64.tar.gz" ;;
  hip|rocm)
    echo "No Ubuntu HIP/ROCm tarball is fetched here (not published on every tag). Use scripts/llamacpp/build-hip.sh on the MI300X host." >&2
    exit 2
    ;;
  *) echo "unsupported backend: ${BACKEND}" >&2; exit 2 ;;
esac

URL="https://github.com/ggml-org/llama.cpp/releases/download/${TAG}/${ASSET}"
DEST="${DEST:-${REPO_ROOT}/tools/llamacpp/releases/${TAG}/${BACKEND}}"
ARCHIVE="${REPO_ROOT}/tools/llamacpp/releases/${ASSET}"

mkdir -p "$(dirname "${ARCHIVE}")" "${DEST}"
echo "url=${URL}"
echo "archive=${ARCHIVE}"
echo "dest=${DEST}"

if [[ ! -f "${ARCHIVE}" ]]; then
  curl -fL --retry 3 --retry-delay 2 -o "${ARCHIVE}.partial" "${URL}"
  mv "${ARCHIVE}.partial" "${ARCHIVE}"
fi

tar -xzf "${ARCHIVE}" -C "${DEST}" --strip-components=1 2>/dev/null || tar -xzf "${ARCHIVE}" -C "${DEST}"

if [[ -x "${DEST}/llama-cli" ]]; then
  echo "llama-cli=${DEST}/llama-cli"
elif [[ -x "${DEST}/bin/llama-cli" ]]; then
  echo "llama-cli=${DEST}/bin/llama-cli"
else
  echo "extracted; llama-cli not at a known path. listing:" >&2
  ls -la "${DEST}" | head
  find "${DEST}" -name 'llama-cli' -o -name 'llama-cli.exe' | head
fi
