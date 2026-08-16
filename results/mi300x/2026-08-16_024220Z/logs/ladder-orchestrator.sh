set -euo pipefail
REPO=/root/Nemotron-on-AMD
cd "$REPO"
RUN="$(cat /tmp/nemotron-ladder-run.dir)"
STAMP="$(cat /tmp/nemotron-ladder-run.id)"
exec > >(tee -a "${RUN}/logs/orchestrator.log") 2>&1
echo "[ladder] start ${STAMP} $(date -u -Iseconds)"
echo "[ladder] Engineering context ladder only. Not a benchmark. Stop before 1M."

source "${REPO}/.venv-mi300x/bin/activate"
export HF_HOME="${HF_HOME:-/root/.cache/huggingface}"

docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true

nohup bash scripts/mi300x/monitor-gpu.sh 5 "${RUN}/logs/gpu-monitor.tsv" \
  > "${RUN}/logs/gpu-monitor.stdout" 2>&1 &
echo $! > "${RUN}/logs/gpu-monitor.pid"

wait_healthy() {
  local i
  for i in $(seq 1 240); do
    if curl -fsS --max-time 5 http://127.0.0.1:8000/v1/models >/dev/null 2>&1; then
      echo "[ladder] health ready after ${i} polls"
      return 0
    fi
    if docker ps -a --filter name=nemotron-nano-vllm --format '{{.Status}}' | grep -q '^Exited'; then
      echo "[ladder] container exited while waiting for health"
      tail -80 "${1}/logs/vllm.stderr.log" || true
      return 1
    fi
    sleep 5
  done
  echo "[ladder] health timeout"
  return 1
}

stop_server() {
  docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true
  sleep 2
}

declare -a SUMMARY_LINES=()
FAILED=0

run_stage() {
  local max_len="$1"
  shift
  local lengths=("$@")
  local vllm_dir="${RUN}/vllm-${max_len}"
  echo "[ladder] ===== stage max_model_len=${max_len} lengths=${lengths[*]} ====="
  stop_server
  nohup bash scripts/mi300x/launch-vllm.sh --docker \
    --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --revision 2d59de1cbd51c0adf384eb906b766d1aee0e0517 \
    --max-model-len "${max_len}" \
    --gpu-memory-utilization 0.80 \
    --output-dir "${vllm_dir}" \
    > "${RUN}/logs/launch-${max_len}.out" 2>&1 &
  echo $! > "${RUN}/logs/vllm-launch.pid"
  if ! wait_healthy "${vllm_dir}"; then
    echo "stage_${max_len}=FAIL_START" >> "${RUN}/context-ladder/stages.txt"
    FAILED=1
    grep -E 'out of memory|OOM|ERROR|Error' "${vllm_dir}/logs/vllm.stderr.log" | tail -20 || true
    return 1
  fi
  {
    echo "timestamp_utc=$(date -u -Iseconds)"
    echo "max_model_len=${max_len}"
    docker inspect --format 'container={{.Name}} image={{.Config.Image}} image_id={{.Image}}' nemotron-nano-vllm
  } > "${vllm_dir}/session.txt"
  python scripts/mi300x/context-ladder.py \
    --base-url http://127.0.0.1:8000/v1 \
    --model nemotron-nano-bf16 \
    --tokenizer nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --revision 2d59de1cbd51c0adf384eb906b766d1aee0e0517 \
    --output-dir "${RUN}" \
    --max-model-len "${max_len}" \
    --timeout 1800 \
    --lengths "${lengths[@]}"
  local rc=$?
  cp -f "${RUN}/context-ladder/latest.json" "${RUN}/context-ladder/ladder-max${max_len}.json"
  if [[ ${rc} -ne 0 ]]; then
    echo "stage_${max_len}=FAIL_PROMPT" >> "${RUN}/context-ladder/stages.txt"
    FAILED=1
    stop_server
    return 1
  fi
  echo "stage_${max_len}=PASS" >> "${RUN}/context-ladder/stages.txt"
  stop_server
  return 0
}

# 4K/8K prompts on a 16K serve (8K serve already exists as prior evidence; this tests actual window fill).
if run_stage 16384 4096 8192 16384 \
  && run_stage 32768 32768 \
  && run_stage 65536 65536 \
  && run_stage 131072 131072; then
  echo "[ladder] all staged lengths passed"
else
  echo "[ladder] stopped after first unsuccessful stage"
fi

kill "$(cat "${RUN}/logs/gpu-monitor.pid")" >/dev/null 2>&1 || true
stop_server
echo "[ladder] done failed=${FAILED} $(date -u -Iseconds)"
if [[ ${FAILED} -eq 0 ]]; then echo ok > /tmp/nemotron-ladder-run.status
else echo fail > /tmp/nemotron-ladder-run.status
fi
