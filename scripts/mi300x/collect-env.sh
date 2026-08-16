#!/usr/bin/env bash
# Collect a timestamped environment snapshot on the MI300X host.
# Does not modify the system. Does not overwrite previous runs.
#
# Usage (on the MI300X machine, from this repo):
#   bash scripts/mi300x/collect-env.sh
#   bash scripts/mi300x/collect-env.sh [output-dir]

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y-%m-%d_%H%M%S)Z"
OUT_DIR="${1:-${REPO_ROOT}/results/mi300x/${STAMP}/environment}"

mkdir -p "${OUT_DIR}"
echo "[mi300x/collect-env] writing to ${OUT_DIR}"

bash "${REPO_ROOT}/scripts/common/collect-linux-env.sh" "${OUT_DIR}"

{
  echo "### MI300X extra probes"
  echo "### started: $(date -u -Iseconds)"
  echo
  echo "=== rocm-smi memory / use ==="
  if command -v rocm-smi >/dev/null 2>&1; then
    rocm-smi --showmeminfo vram 2>&1 || true
    rocm-smi --showproductname 2>&1 || true
    rocm-smi --showdriverversion 2>&1 || true
    rocm-smi --showfw 2>&1 || true
    rocm-smi --shownodesbw 2>&1 || true
  else
    echo "rocm-smi not found"
  fi
  echo
  echo "=== amd-smi (if present) ==="
  if command -v amd-smi >/dev/null 2>&1; then
    amd-smi version 2>&1 || true
    amd-smi list 2>&1 || true
    amd-smi static 2>&1 || true
    amd-smi topology 2>&1 || true
  else
    echo "amd-smi not found"
  fi
  echo
  echo "=== hipinfo / rocminfo agents ==="
  if command -v rocminfo >/dev/null 2>&1; then
    rocminfo 2>&1 | grep -E "Agent|Name:|Marketing|Device Type|Compute Unit|Max Queue|Pool Allocable" | head -n 200
  fi
  echo
  echo "=== disk space (needed before downloading Nano ~60 GiB weights) ==="
  df -h . "${HOME}" /tmp 2>/dev/null || df -h
  echo
  echo "### finished: $(date -u -Iseconds)"
} > "${OUT_DIR}/mi300x-extra.txt"

echo "[mi300x/collect-env] extra probes written to ${OUT_DIR}/mi300x-extra.txt"
echo "${OUT_DIR}"
