# Nemotron 3 Nano 30B-A3B

**First AMD execution target (BF16, 1× MI300X). Transformers greedy thinking-off: Validated (pinned `031205Z`). vLLM serve/characterization/128K ladder: Runs / PASS WITH CAVEATS. Not Optimized. Not 256K/1M.**

| | |
| --- | --- |
| Official BF16 ID | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` |
| Official FP8 ID | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8` |
| Official NVFP4 ID | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4` |
| Parameters | 30B total / 3.5B active |
| Architecture | Hybrid MoE: Mamba-2 + MoE (128+1 experts, top-6) + 6 GQA layers |
| Context | 1M max; HF default 256k |
| License | NVIDIA Nemotron Open Model License |
| Transformers | ≥ 5.3.0 (card). Official snippet has **no** `trust_remote_code` |
| vLLM (NVIDIA) | ≥ 0.12.0; plugin `nano_v3_reasoning_parser.py`; parsers `nano_v3` + `qwen3_coder` |
| Release | 2025-12-15 |

Card: https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 (checked 2026-08-15).

Related: Nano 4B official GGUF is **Validated** on llama.cpp CPU/Vulkan/HIP. Community Unsloth Nano 30B Q4_K_M GGUF is **Validated** on the same three backends (`225528Z`, `225631Z`, `231304Z`). That is **not** an official NVIDIA 30B GGUF.

## Memory (raw weights only)

| Precision | ~GB | ~GiB | 1× MI300X 192 GB |
| --- | --- | --- | --- |
| BF16 | 60 | 55.9 | Load observed ~58.9 GiB allocated on 1× MI300X VF. Short-context generate **PASS WITH CAVEATS** (`results/mi300x/2026-08-15_172810Z/`) |
| FP8 | 30 | 27.9 | Fits; format **Unknown** |
| 4-bit / GGUF | 24.57 GB Unsloth Q4_K_M measured | 22.88 | Community file llama.cpp **Validated** HIP (`231304Z`). NVFP4 **not assumed portable**. Official NVIDIA 30B GGUF: none found |

## Chat / reasoning

- `enable_thinking=True` (default on card) vs `False`
- Reasoning-on sampling: temperature 1.0, top_p 1.0
- Reasoning-off Transformers snippet: greedy
- Tool calling sampling: 0.6 / 0.95

This repo’s first smoke test is **greedy + thinking off**. See `prompts/`.

## NVIDIA-only (do not copy to MI300X blindly)

- TRT-LLM `nano_v3` backend
- NIM
- Listed HW: H100-80GB, A100
- NVFP4 + `VLLM_USE_FLASHINFER_MOE_FP4`
- SGLang `--attention-backend flashinfer`

## Scripts

```bash
python scripts/mi300x/transformers-smoke-test.py \
  --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --output-dir results/mi300x/<RUN_ID>
```
