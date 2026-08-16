# Review: vLLM OpenAI-compatible serve

**Date:** 2026-08-15  
**Artifact:** `openai-api/summary.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for this Docker stack, BF16 Nano, `max-model-len=8192`.  
**Not claimed:** Validated (HF revision unset), Optimized, Production-ready, long context, native pip venv vLLM.

## Stack

- Device: AMD Instinct MI300X VF (SR-IOV)
- Image: `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0` (`sha256:ac1be45dac88…`)
- vLLM: `0.23.1.dev1+g9ddef7117.d20260715`
- Python 3.14.6, PyTorch `2.11.0+rocm7.14.0`, HIP 7.14.60850
- Checkpoint: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` (`model_revision` not recorded)
- Flags: BF16, TP=1, `max-model-len=8192`, `gpu-memory-utilization=0.80`, `--trust-remote-code`, `qwen3_coder`, `nano_v3` plugin
- NVIDIA FlashInfer / NVFP4 / TRT-LLM flags not used
- Load: 58.91 GiB in 25.9 s (from HF cache)

## API tests

| Test | Verdict | Note |
| --- | --- | --- |
| health | ok | `/health` |
| list_models | ok | served name `nemotron-nano-bf16` |
| chat, thinking off | Reasonable | RAM vs storage in three sentences |
| chat, thinking on | Reasonable | `8×192=1536`; reasoning field populated; answer in content |
| sequential 1/2/3 | Reasonable | replies `1`, `2`, `3` |

## Material caveats (do not hide)

- Host Python is 3.12; AMD’s ROCm 7.14 vLLM wheel/image path is Python 3.14. This **Runs** result is Docker, not `.venv-mi300x`.
- Transformers stack used torch **2.12.0+rocm7.14.0**; this image uses torch **2.11.0+rocm7.14.0**.
- Default fused-MoE and Mamba SSU configs missing for `AMD_Instinct_MI300X` — vLLM warns performance may be sub-optimal.
- ROCm custom paged attention unavailable; Triton fallback.
- Triton JIT during first requests (latency spikes, not a benchmark).
- `generation_config.json` overrode server defaults to temperature 1.0 / top_p 1.0.
- KV cache size logged as 7,780,352 tokens at this memory util; we **did not** test beyond 8192 context.
- Engine snapshot of ~18.8 gen tok/s is not an engineering characterization, not a product number.

Command: `vllm/launch-command.txt`. Logs: `vllm/logs/`.
