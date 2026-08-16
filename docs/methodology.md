# Methodology

## Principles

1. **Evidence over catalogs.** Official NVIDIA and AMD docs tell us what *should* work on NVIDIA, or what AMD lists as ROCm-supported. They do not tell us Nemotron Runs on AMD until we run it.
2. **Track the current product per line**, not every historical Hugging Face ID. Precision/role siblings of that product (BF16 / FP8 / NVFP4 / Base) stay. Inventory “latest repo” is not an AMD run on floating `main`: tests still pin a revision. Policy: [`nemotron-family.md`](nemotron-family.md).
3. **Separate layers.** Memory feasibility, architecture/kernels, Transformers, vLLM, tokenizer/chat template, and precision are different failure layers.
4. **Do not overwrite runs.** Every experiment gets `results/<platform>/<timestamp>/`.
5. **Do not modify the host stack first.** Isolated venv. No OS/ROCm/kernel upgrades unless a recorded blocker requires it and we stop to explain why.
6. **Failures stay in the record.** Changing packages until something works without preserving the first failure hides AMD software gaps.

## Test order (Nano on MI300X)

```text
collect-env
→ inspect-only venv / ROCm mapping
→ ROCm PyTorch + Transformers install (no CUDA wheels, no vLLM yet)
→ Transformers load + greedy smoke prompts
→ reasoning-template probes
→ vLLM serve (conservative max-model-len)
→ OpenAI-compatible API
→ memory / context ladder 4K → 8K → … (never jump to 1M)
→ engineering characterization (not an official benchmark)
```

That Nano 30B BF16 sequence is **done**. Further MI300X targets: [`mi300x-next-tests.md`](mi300x-next-tests.md) (A small models → B Lightning/Omni BF16 → C FP8 FNUZ). Do not reuse a Nano 30B result as a PASS for those rows.

## How a PASS is earned

A compatibility-matrix **PASS** requires:

- `run-metadata.json`
- environment snapshot
- command used
- JSON result with prompts and generations **or** a classified FAIL
- link from the matrix row to the result path

A memory calculator result is **never** a PASS.

## How a FAIL is recorded

See [`troubleshooting.md`](troubleshooting.md). Classify:

`MODEL ARCHITECTURE | TRANSFORMERS | PYTORCH | ROCM | VLLM | KERNEL | PRECISION | MEMORY | TOKENIZER | CHAT TEMPLATE | CUSTOM CODE | OTHER`

Keep the original stderr.

## Sampling for smoke tests

The official Nano BF16 card recommends `temperature=1.0` / `top_p=1.0` for reasoning-on, and greedy decoding for reasoning-off.

This repo's first Transformers smoke test uses **`enable_thinking=False` and greedy (`temperature=0`)** so the first question is “does it generate at all reproducibly,” not “does sampling look like NVIDIA's quality tables.”

Reasoning-on is a **separate** probe in `prompts/reasoning-tests.json`.

## Super and Ultra

Before download:

1. Estimate raw weight bytes (`scripts/common/estimate_weight_memory.py`).
2. Compare to 192 GB HBM and to NVIDIA's own minimum GPU counts.
3. On **OAM Instinct** (MI300X / MI325X / MI350X / MI355X), if BF16 cannot fit one GPU, record **2× / 4× / 8×**, not “doesn't fit.” On **MI350P, Radeon, and Ryzen AI**, if it does not fit one PCIe card or this laptop, record **doesn't fit**. Do not invent a workaround to manufacture a PASS.

## NVIDIA-only instructions we will not copy blindly

Explicitly called out when we see them:

- TensorRT-LLM (`trtllm-serve`, `_autodeploy`)
- NIM containers and `nvcr.io` CUDA images
- `VLLM_USE_FLASHINFER_MOE_FP4` / FlashInfer MoE backends
- `--mamba-backend flashinfer`
- `--quantization modelopt_fp4`
- CUDA wheel indexes (`download.pytorch.org/whl/cu*`, default `pip install vllm`)
- NVFP4 as a drop-in AMD precision
