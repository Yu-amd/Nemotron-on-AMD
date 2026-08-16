#!/usr/bin/env bash
# Read-only ROCm / HIP / NPU presence check for the local Ryzen AI machine.
# Does not install or upgrade anything.
#
# Usage:
#   bash scripts/ryzen-ai/check-rocm.sh

set -u

echo "=== ROCm presence check (read-only) ==="
echo "date: $(date -u -Iseconds)"
echo

check() {
  local label="$1"
  shift
  printf '%-28s ' "${label}:"
  if "$@" >/dev/null 2>&1; then
    echo "PRESENT"
  else
    echo "NOT FOUND"
  fi
}

check "rocminfo" command -v rocminfo
check "rocm-smi" command -v rocm-smi
check "amd-smi" command -v amd-smi
check "hipcc" command -v hipcc
check "hipconfig" command -v hipconfig
check "/opt/rocm" test -d /opt/rocm
check "/dev/kfd" test -e /dev/kfd
check "/dev/dri" test -d /dev/dri
check "/dev/accel" test -d /dev/accel

echo
echo "=== /opt/rocm version files ==="
if [[ -f /opt/rocm/.info/version ]]; then
  cat /opt/rocm/.info/version
else
  echo "no /opt/rocm/.info/version"
fi

echo
echo "=== GPU vs NPU reminder ==="
echo "ROCm/HIP on the integrated Radeon GPU is NOT evidence of XDNA NPU execution."
echo "NPU claims require a separate runtime path (for example IREE/ONNX/XRT) and a recorded Nemotron run."
