set -euo pipefail
REPO=/root/Nemotron-on-AMD
cd "$REPO"
RUN="$(cat /tmp/nemotron-char-run.dir)"
STAMP="$(cat /tmp/nemotron-char-run.id)"
exec > >(tee -a "${RUN}/logs/orchestrator.log") 2>&1
echo "[char] start ${STAMP} $(date -u -Iseconds)"
echo "[char] label=Engineering characterization only"

docker rm -f nemotron-moe-tune >/dev/null 2>&1 || true
docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true

memsnap() {
  local name="$1"
  {
    echo "timestamp_utc=$(date -u -Iseconds)"
    echo "phase=${name}"
    echo
    echo "=== rocm-smi ==="
    rocm-smi --showmeminfo vram --showuse --showtemp --showpower 2>&1 || true
    echo
    echo "=== amd-smi static ==="
    amd-smi static 2>&1 | head -80 || true
    echo
    echo "=== amd-smi metric ==="
    amd-smi metric 2>&1 || true
  } > "${RUN}/benchmark/memory-${name}.txt"
  echo "[char] snapshot ${name}"
}

memsnap before-serve

nohup bash scripts/mi300x/monitor-gpu.sh 2 "${RUN}/logs/gpu-monitor.tsv" \
  > "${RUN}/logs/gpu-monitor.stdout" 2>&1 &
echo $! > "${RUN}/logs/gpu-monitor.pid"
echo "[char] monitor pid=$(cat "${RUN}/logs/gpu-monitor.pid")"

nohup bash scripts/mi300x/launch-vllm.sh --docker \
  --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --revision 2d59de1cbd51c0adf384eb906b766d1aee0e0517 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.80 \
  --output-dir "${RUN}/vllm" \
  > "${RUN}/logs/launch-nohup.out" 2>&1 &
echo $! > "${RUN}/logs/vllm-launch.pid"
echo "[char] launch pid=$(cat "${RUN}/logs/vllm-launch.pid")"

ok=0
for i in $(seq 1 180); do
  if curl -fsS --max-time 5 http://127.0.0.1:8000/v1/models >/dev/null 2>&1; then
    ok=1
    echo "[char] health ready after ${i} polls ($(date -u -Iseconds))"
    break
  fi
  if docker ps -a --filter name=nemotron-nano-vllm --format '{{.Status}}' | grep -q '^Exited'; then
    echo "[char] ERROR: vLLM container exited"
    docker logs nemotron-nano-vllm 2>&1 | tail -80 || true
    tail -80 "${RUN}/vllm/logs/vllm.stderr.log" || true
    break
  fi
  sleep 5
done

if [[ "${ok}" -ne 1 ]]; then
  echo "[char] FAILED to become healthy"
  kill "$(cat "${RUN}/logs/gpu-monitor.pid")" >/dev/null 2>&1 || true
  docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true
  echo fail > /tmp/nemotron-char-run.status
  exit 1
fi

{
  echo "timestamp_utc=$(date -u -Iseconds)"
  echo "hostname=$(hostname)"
  echo "run_id=${STAMP}"
  echo "revision=2d59de1cbd51c0adf384eb906b766d1aee0e0517"
  echo "max_model_len=8192"
  echo "label=Engineering characterization only"
  echo
  docker inspect --format 'container={{.Name}} image={{.Config.Image}} image_id={{.Image}} created={{.Created}}' nemotron-nano-vllm
  docker image inspect --format 'repo_digest={{index .RepoDigests 0}} id={{.Id}}' \
    rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0 || true
} > "${RUN}/environment/session.txt"

memsnap after-load-idle

echo "[char] warmup (Triton JIT; not scored)"
python3 - <<'PY'
import json, urllib.request, time
base = "http://127.0.0.1:8000/v1"
body = {
    "model": "nemotron-nano-bf16",
    "messages": [{"role": "user", "content": "Say hi in one word."}],
    "max_tokens": 16,
    "temperature": 0,
    "chat_template_kwargs": {"enable_thinking": False},
}
for i in range(2):
    t0 = time.perf_counter()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        payload = json.loads(resp.read().decode())
    print(f"warmup {i+1} {time.perf_counter()-t0:.2f}s tokens={payload.get('usage')}")
PY

memsnap after-warmup

echo "[char] benchmark concurrency 1 2 4"
python3 scripts/mi300x/benchmark.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model nemotron-nano-bf16 \
  --output-dir "${RUN}" \
  --concurrency 1 2 4 \
  --requests-per-conc 4 \
  --max-tokens 128 \
  --timeout 300

memsnap after-characterization

grep -E 'Model loading took|KV cache|Maximum concurrency|gpu_memory|Engine 000' \
  "${RUN}/vllm/logs/vllm.stdout.log" "${RUN}/vllm/logs/vllm.stderr.log" \
  > "${RUN}/benchmark/vllm-memory-log-excerpt.txt" || true

echo "[char] stop monitor and server"
kill "$(cat "${RUN}/logs/gpu-monitor.pid")" >/dev/null 2>&1 || true
wait "$(cat "${RUN}/logs/gpu-monitor.pid")" >/dev/null 2>&1 || true
docker rm -f nemotron-nano-vllm >/dev/null 2>&1 || true
memsnap after-stop

echo "[char] done $(date -u -Iseconds)"
echo ok > /tmp/nemotron-char-run.status
