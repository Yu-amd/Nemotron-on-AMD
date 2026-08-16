#!/usr/bin/env bash
# Create an isolated Python virtualenv for MI300X validation.
# Default is inspect-only. Installation happens only with --install.
#
# This script never modifies system Python and never installs CUDA wheels.
#
# Usage (on the MI300X machine, from this repo):
#   bash scripts/mi300x/setup-python-env.sh
#   bash scripts/mi300x/setup-python-env.sh --install
#   bash scripts/mi300x/setup-python-env.sh --venv .venv-mi300x --install
#
# Hugging Face authentication, if needed, must be provided by the operator:
#   export HF_TOKEN=<HF_TOKEN>
# Do not write tokens into this repository.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv-mi300x"
DO_INSTALL=0
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<'EOF'
Create / inspect an isolated MI300X Python environment.

Options:
  --venv PATH     Virtualenv path (default: .venv-mi300x at repo root)
  --install       After inspection, install ROCm PyTorch + Transformers
                  into the venv. Refuses CUDA-indexed wheels.
  --python BIN    Python interpreter used to create the venv
  -h, --help      Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --install)
      DO_INSTALL=1
      shift
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

echo "[setup-python-env] repo: ${REPO_ROOT}"
echo "[setup-python-env] venv: ${VENV_DIR}"
echo "[setup-python-env] python: ${PYTHON_BIN}"
echo

echo "=== host Python (system, unmodified) ==="
"${PYTHON_BIN}" --version
command -v "${PYTHON_BIN}"
"${PYTHON_BIN}" -c "import sys; print(sys.executable)"
echo

echo "=== ROCm detection ==="
ROCM_INFO_VERSION="unknown"
HIP_VERSION="unknown"
if [[ -f /opt/rocm/.info/version ]]; then
  ROCM_INFO_VERSION="$(tr -d '[:space:]' < /opt/rocm/.info/version)"
  echo "found /opt/rocm/.info/version: ${ROCM_INFO_VERSION}"
fi
if command -v hipconfig >/dev/null 2>&1; then
  HIP_VERSION="$(hipconfig --version 2>/dev/null | head -n 1 | tr -d '[:space:]' || echo unknown)"
  echo "hipconfig --version: ${HIP_VERSION}"
  echo "HIP_PATH=${HIP_PATH:-unset}"
fi
# Prefer HIP runtime version when /opt/rocm/.info is a wrapper (seen: 7.0.2 info + HIP 7.14).
ROCM_VERSION="${ROCM_INFO_VERSION}"
HIP_MAJOR_MINOR="$(echo "${HIP_VERSION}" | grep -oE '^[0-9]+\.[0-9]+' || true)"
INFO_MAJOR_MINOR="$(echo "${ROCM_INFO_VERSION}" | grep -oE '^[0-9]+\.[0-9]+' || true)"
if [[ -n "${HIP_MAJOR_MINOR}" && "${HIP_MAJOR_MINOR}" != "${INFO_MAJOR_MINOR}" ]]; then
  echo "WARNING: /opt/rocm/.info/version (${ROCM_INFO_VERSION}) disagrees with HIP (${HIP_VERSION})."
  echo "Using HIP ${HIP_MAJOR_MINOR} for PyTorch wheel selection."
  ROCM_VERSION="${HIP_VERSION}"
fi
if command -v rocminfo >/dev/null 2>&1; then
  echo "rocminfo is present"
else
  echo "WARNING: rocminfo not found on PATH"
fi
if command -v rocm-smi >/dev/null 2>&1; then
  echo "rocm-smi is present"
  rocm-smi --showproductname 2>/dev/null || true
else
  echo "WARNING: rocm-smi not found on PATH"
fi
GFX=""
if command -v rocminfo >/dev/null 2>&1; then
  set +o pipefail
  GFX="$(rocminfo 2>/dev/null | awk '/Name:[[:space:]]+gfx/{print $2; exit}')"
  set -o pipefail
  echo "detected_gfx=${GFX:-unknown}"
fi
echo

# Map detected ROCm to a conservative PyTorch wheel index.
# Checked 2026-08-15: pytorch.org ROCm indexes plus AMD repo.amd.com for ROCm 7.14.
# They MUST be revalidated against the actual host ROCm before --install.
PYTORCH_INDEX=""
PYTORCH_SPEC="torch"
ROCM_MAJOR_MINOR="$(echo "${ROCM_VERSION}" | grep -oE '^[0-9]+\.[0-9]+' || true)"
case "${ROCM_MAJOR_MINOR}" in
  6.2) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm6.2" ;;
  6.3) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm6.3" ;;
  6.4) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm6.4" ;;
  7.0) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm7.0" ;;
  7.1) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm7.0" ;;  # closest published index; revalidate
  7.2) PYTORCH_INDEX="https://download.pytorch.org/whl/rocm7.2" ;;
  7.14)
    # AMD ROCm AI ecosystem docs, 2026-08-15:
    # https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html
    PYTORCH_INDEX="https://repo.amd.com/rocm/whl-multi-arch/"
    case "${GFX}" in
      gfx942) PYTORCH_SPEC="torch[device-gfx942]==2.12.0+rocm7.14.0" ;;
      gfx950) PYTORCH_SPEC="torch[device-gfx950]==2.12.0+rocm7.14.0" ;;
      *) PYTORCH_SPEC="torch[device-all]==2.12.0+rocm7.14.0" ;;
    esac
    ;;
  *)
    echo "No canned PyTorch ROCm index for detected version '${ROCM_VERSION}'."
    echo "Inspect https://pytorch.org/get-started/locally/ and AMD ROCm docs before installing."
    ;;
esac

echo "detected_rocm_info_version=${ROCM_INFO_VERSION}"
echo "detected_hip_version=${HIP_VERSION}"
echo "detected_rocm_version=${ROCM_VERSION}"
echo "detected_rocm_major_minor=${ROCM_MAJOR_MINOR:-unknown}"
echo "proposed_pytorch_index=${PYTORCH_INDEX:-unset}"
echo "proposed_pytorch_spec=${PYTORCH_SPEC}"
echo
echo "vLLM ROCm notes (docs.vllm.cc, checked 2026-08-15):"
echo "  - vLLM supports AMD GPUs with ROCm 6.3+"
echo "  - Prebuilt wheels: rocm700 (ROCm 7.0, Python 3.12, vLLM 0.14.0-0.18.0) and ROCm 7.2.1 nightlies"
echo "  - Official image: vllm/vllm-openai-rocm  (AMD rocm/vllm images are deprecated)"
echo "  - Hardware list includes MI300 (gfx942) and Ryzen AI 300 (gfx1150, requires ROCm 7.0.2+)"
echo "  - Python 3.12 is required for ROCm wheels; other Pythons can silently pull a CUDA wheel"
echo "  - Do NOT pip install the default CUDA vLLM wheel on this host."
echo "  - Nemotron 3 Super cookbook pins vLLM 0.18.1 on NVIDIA; ROCm wheel availability must be checked."
echo "  - Nemotron 3 Nano cookbook asks for vllm>=0.12.0 on NVIDIA."
echo "  - Nemotron 3 Nano Omni cookbook asks for vLLM 0.20.0 on NVIDIA."
echo "  - Nemotron 3.5 Lightning BF16 cookbook uses --mamba-backend flashinfer (NVIDIA-specific; do not copy)."
echo

if ! "${PYTHON_BIN}" -m venv --help >/dev/null 2>&1; then
  echo "ERROR: python venv module is missing. On Ubuntu this is python3.12-venv." >&2
  echo "That package is required for an isolated env. It does not replace system Python or ROCm." >&2
  exit 1
fi

if [[ -d "${VENV_DIR}" && ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "[setup-python-env] removing incomplete venv at ${VENV_DIR}"
  rm -rf "${VENV_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[setup-python-env] creating venv at ${VENV_DIR}"
  if ! "${PYTHON_BIN}" -m venv "${VENV_DIR}"; then
    echo "ERROR: venv creation failed. If ensurepip is missing, install python3.12-venv (Ubuntu)." >&2
    exit 1
  fi
else
  echo "[setup-python-env] reusing existing venv at ${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo
echo "=== venv Python ==="
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
echo

echo "=== current venv packages of interest ==="
python -m pip list | grep -iE "torch|hip|rocm|transformers|vllm|accelerate|safetensors|tokenizers|huggingface" || echo "(none installed yet)"
echo

python "${REPO_ROOT}/scripts/common/check-python-env.py" || true

if [[ "${DO_INSTALL}" -eq 0 ]]; then
  cat <<EOF

Inspect-only mode finished. No packages were installed.

If the ROCm detection above looks correct, install into the venv with:

  bash scripts/mi300x/setup-python-env.sh --venv ${VENV_DIR} --install

Proposed Transformers-first stack (Nano BF16 smoke test):

  source ${VENV_DIR}/bin/activate
  python -m pip install -U pip
  python -m pip install "${PYTORCH_SPEC:-torch}" --index-url ${PYTORCH_INDEX:-<SET_AFTER_CONFIRMING_ROCM>}
  python -m pip install "transformers>=5.3.0" accelerate safetensors tokenizers huggingface_hub

Do not install CUDA wheels. Do not install vLLM until Transformers smoke tests pass.
Do not put HF_TOKEN into this repo. Export it in the shell if gated downloads are required.
EOF
  exit 0
fi

if [[ -z "${PYTORCH_INDEX}" ]]; then
  echo "ERROR: refusing to --install because ROCm version '${ROCM_VERSION}' has no canned PyTorch index." >&2
  echo "Confirm the host ROCm version, then install torch from the matching ROCm wheel index." >&2
  exit 1
fi

if [[ "${PYTORCH_INDEX}" == *"/whl/cu"* ]]; then
  echo "ERROR: refusing CUDA wheel index: ${PYTORCH_INDEX}" >&2
  exit 1
fi

echo "[setup-python-env] installing into venv"
echo "  index: ${PYTORCH_INDEX}"
echo "  spec:  ${PYTORCH_SPEC}"
python -m pip install -U pip
python -m pip install "${PYTORCH_SPEC}" --index-url "${PYTORCH_INDEX}"
python -m pip install "transformers>=5.3.0" accelerate safetensors tokenizers huggingface_hub

echo
echo "=== post-install probe ==="
python "${REPO_ROOT}/scripts/common/check-python-env.py"
python - <<'PY'
import torch
print("torch", torch.__version__)
print("hip", getattr(torch.version, "hip", None))
print("cuda_build", getattr(torch.version, "cuda", None))
print("is_available", torch.cuda.is_available())
print("device_count", torch.cuda.device_count())
if torch.cuda.is_available() and torch.cuda.device_count() > 0:
    print("device0", torch.cuda.get_device_name(0))
if getattr(torch.version, "cuda", None) and not getattr(torch.version, "hip", None):
    raise SystemExit("ERROR: installed torch looks like a CUDA build. Uninstall it and use a ROCm wheel.")
PY

echo
echo "Transformers stack installed. vLLM is intentionally NOT installed yet."
echo "Next: run scripts/mi300x/transformers-smoke-test.py after collecting env and downloading the Nano BF16 model."
