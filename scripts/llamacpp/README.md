# llama.cpp scripts

Isolated from Transformers / vLLM. Do not install CUDA wheels. Do not upgrade OS/ROCm/kernel. Do not download Super BF16, Ultra, or NVFP4.

Binaries and GGUF files live under `tools/llamacpp/` (gitignored). Results still go to `results/<platform>/<utc>Z/`.

## Fetch a pinned GitHub release

```bash
# CPU (laptop or any x86_64 host)
bash scripts/llamacpp/fetch-release.sh --backend cpu --tag b10453

# Vulkan (this Strix Point laptop; Mesa RADV is already installed)
bash scripts/llamacpp/fetch-release.sh --backend vulkan --tag b10453
```

Tag **b10453** (2026-08-16) has Ubuntu CPU + Vulkan tarballs. It does **not** ship an Ubuntu ROCm tarball. MI300X HIP is a source build: `scripts/llamacpp/build-hip.sh`.

## Download a GGUF without guessing cache behaviour

```bash
bash scripts/llamacpp/download-gguf.sh \
  --repo nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF \
  --file NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf \
  --revision ba223d14e45525f7fae81db77ea8cabeb2fc6c25
```

## Smoke test

Greedy, thinking-off by default, `prompts/smoke-tests.json`.

```bash
python3 scripts/llamacpp/smoke-test.py \
  --llama-cli tools/llamacpp/releases/b10453/cpu/llama-cli \
  --model tools/llamacpp/gguf/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf \
  --n-gpu-layers 0 \
  --platform ryzen-ai \
  --output-dir results/ryzen-ai/<utc>Z
```

Vulkan / HIP: `--n-gpu-layers 99` and a binary that actually links that backend. Logs must show Vulkan or ROCm, not CPU-only, before claiming iGPU or Instinct GPU.
