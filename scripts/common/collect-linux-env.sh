#!/usr/bin/env bash
# Collect a timestamped Linux environment snapshot without modifying the system.
# Intended for both the local Ryzen AI laptop and remote Instinct hosts.
#
# Usage:
#   bash scripts/common/collect-linux-env.sh [output-dir]
#
# If output-dir is omitted, a timestamped directory under ./results is used.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y-%m-%d_%H%M%S)Z"

if [[ $# -ge 1 ]]; then
  OUT_DIR="$1"
else
  OUT_DIR="${REPO_ROOT}/results/unclassified/${STAMP}/environment"
fi

mkdir -p "${OUT_DIR}"

log() {
  printf '[collect-linux-env] %s\n' "$*"
}

run_cmd() {
  local name="$1"
  shift
  local outfile="${OUT_DIR}/${name}.txt"
  {
    echo "### command: $*"
    echo "### started: $(date -u -Iseconds)"
    echo
    if command -v "$1" >/dev/null 2>&1 || [[ "$1" == python3 ]] || [[ "$1" == pip ]] || [[ "$1" == bash ]]; then
      "$@" 2>&1 || echo "### exit_code: $?"
    else
      echo "### SKIPPED: command not found: $1"
    fi
    echo
    echo "### finished: $(date -u -Iseconds)"
  } > "${outfile}"
  log "wrote ${outfile}"
}

log "output directory: ${OUT_DIR}"
log "repo root: ${REPO_ROOT}"

{
  echo "date_utc=$(date -u -Iseconds)"
  echo "date_local=$(date -Iseconds)"
  echo "hostname=$(hostname 2>/dev/null || echo unknown)"
  echo "user=$(id -un 2>/dev/null || echo unknown)"
  echo "pwd=$(pwd)"
  echo "repo_root=${REPO_ROOT}"
} > "${OUT_DIR}/session.txt"

run_cmd date date -u
run_cmd hostname hostname
run_cmd uname uname -a
run_cmd os-release bash -c 'cat /etc/os-release 2>/dev/null || echo "no /etc/os-release"'
run_cmd kernel-release uname -r
run_cmd lscpu lscpu
run_cmd cpuinfo bash -c 'head -n 80 /proc/cpuinfo'
run_cmd meminfo bash -c 'cat /proc/meminfo'
run_cmd free free -h
run_cmd lspci-vga bash -c 'lspci -nnk | grep -A 8 -E "VGA|3D|Display|Accelerator|Processing accelerators" || lspci | grep -iE "vga|display|3d|amd|instinct|radeon|npu" || echo "lspci found no matching devices"'
run_cmd lspci-full lspci -nn
run_cmd ls-accel bash -c 'ls -l /dev/dri /dev/kfd /dev/accel 2>/dev/null || echo "no /dev/dri, /dev/kfd, or /dev/accel"'
run_cmd dmesg-amd bash -c 'dmesg -T 2>/dev/null | grep -iE "amdgpu|amdxdna|kfd|rocm" | tail -n 80 || echo "dmesg not readable or no AMD kernel messages"'

run_cmd rocminfo rocminfo
run_cmd rocm-smi rocm-smi
run_cmd rocm-smi-showall rocm-smi --showallinfo
run_cmd rocm-smi-topo rocm-smi --showtoponuma
run_cmd rocm-version bash -c 'cat /opt/rocm/.info/version 2>/dev/null; cat /opt/rocm/bin/.rocmversion 2>/dev/null; ls -d /opt/rocm* 2>/dev/null; echo ROCM_PATH="${ROCM_PATH:-unset}"'
run_cmd amd-smi amd-smi
run_cmd amd-smi-static amd-smi static
run_cmd hipconfig hipconfig --full

run_cmd python-version python3 --version
run_cmd python-which bash -c 'command -v python3; python3 -c "import sys; print(sys.executable); print(sys.version)"'
run_cmd pip-version bash -c 'python3 -m pip --version 2>/dev/null || pip --version 2>/dev/null || echo "pip not found"'
run_cmd pip-list bash -c 'python3 -m pip list 2>/dev/null || echo "pip list failed"'

run_cmd torch-probe python3 - <<'PY'
import sys
print("python", sys.version.replace("\n", " "))
print("executable", sys.executable)
try:
    import torch
except Exception as e:
    print("torch_import_error", type(e).__name__, e)
    sys.exit(0)
print("torch", torch.__version__)
print("torch.version.hip", getattr(torch.version, "hip", None))
print("torch.version.cuda", getattr(torch.version, "cuda", None))
print("torch.cuda.is_available", torch.cuda.is_available())
print("torch.cuda.device_count", torch.cuda.device_count())
if torch.cuda.is_available() and torch.cuda.device_count() > 0:
    for i in range(torch.cuda.device_count()):
        print(f"device[{i}]", torch.cuda.get_device_name(i))
        try:
            props = torch.cuda.get_device_properties(i)
            print(f"device[{i}].total_memory_bytes", props.total_memory)
            print(f"device[{i}].props", props)
        except Exception as e:
            print(f"device[{i}].props_error", type(e).__name__, e)
PY

run_cmd groups id
run_cmd env-rocm bash -c 'env | grep -E "^(ROCM|HIP|HSA|AMD|CUDA|HF_|TRANSFORMERS_|TORCH_|VLLM_|PYTORCH_)" | sort || echo "no matching environment variables"'

log "done. snapshot at ${OUT_DIR}"
echo "${OUT_DIR}"
