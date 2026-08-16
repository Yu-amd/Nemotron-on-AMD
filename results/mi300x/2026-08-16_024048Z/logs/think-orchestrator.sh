set -euo pipefail
REPO=/root/Nemotron-on-AMD
cd "$REPO"
RUN="$(cat /tmp/nemotron-think-run.dir)"
exec > >(tee -a "${RUN}/logs/orchestrator.log") 2>&1
echo "[think] start $(date -u -Iseconds) dir=${RUN}"
source "${REPO}/.venv-mi300x/bin/activate"
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"
python scripts/mi300x/transformers-smoke-test.py \
  --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --revision 2d59de1cbd51c0adf384eb906b766d1aee0e0517 \
  --prompts prompts/reasoning-tests.json \
  --max-new-tokens 512 \
  --output-dir "${RUN}"
rc=$?
echo "[think] python_exit=${rc} $(date -u -Iseconds)"
if [[ ${rc} -eq 0 ]]; then echo ok > /tmp/nemotron-think-run.status; else echo fail > /tmp/nemotron-think-run.status; fi
exit ${rc}
