#!/usr/bin/env bash
# Collect a local Ryzen AI / Strix Point environment snapshot.
# Does not install packages, download models, or modify the system.
#
# Usage (from repo root):
#   bash scripts/ryzen-ai/collect-env.sh
#   bash scripts/ryzen-ai/collect-env.sh [output-dir]

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y-%m-%d_%H%M%S)Z"
OUT_DIR="${1:-${REPO_ROOT}/results/ryzen-ai/${STAMP}/environment}"

mkdir -p "${OUT_DIR}"
echo "[ryzen-ai/collect-env] writing to ${OUT_DIR}"

bash "${REPO_ROOT}/scripts/common/collect-linux-env.sh" "${OUT_DIR}"

# Additional Strix Point / Ryzen AI probes. Failures are recorded, not fatal.
{
  echo "### extra Ryzen AI probes"
  echo "### started: $(date -u -Iseconds)"
  echo
  echo "=== xdna / accel devices ==="
  ls -l /dev/accel /dev/dri 2>/dev/null || true
  echo
  echo "=== kernel modules of interest ==="
  lsmod 2>/dev/null | grep -iE "amdgpu|amdxdna|kfd|drm" || echo "lsmod/grep found no matching modules"
  echo
  echo "=== possible NPU sysfs ==="
  find /sys/class /sys/devices -maxdepth 4 \( -iname '*xdna*' -o -iname '*npu*' -o -iname '*accel*' \) 2>/dev/null | head -n 80 || true
  echo
  echo "=== vulkaninfo (if present) ==="
  if command -v vulkaninfo >/dev/null 2>&1; then
    vulkaninfo --summary 2>&1 | head -n 120
  else
    echo "vulkaninfo not found"
  fi
  echo
  echo "=== clinfo (if present) ==="
  if command -v clinfo >/dev/null 2>&1; then
    clinfo -l 2>&1 || clinfo 2>&1 | head -n 80
  else
    echo "clinfo not found"
  fi
  echo
  echo "### finished: $(date -u -Iseconds)"
} > "${OUT_DIR}/ryzen-ai-extra.txt"

echo "[ryzen-ai/collect-env] extra probes written to ${OUT_DIR}/ryzen-ai-extra.txt"
echo "${OUT_DIR}"
