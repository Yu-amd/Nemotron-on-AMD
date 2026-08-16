# Review: vLLM engineering characterization

**Date:** 2026-08-16  
**Artifact:** `benchmark/characterization.json`, `benchmark/memory-summary.json`  
**Label:** Engineering characterization only. **Not** an official benchmark.  
**Claim allowed after this review:** **Runs** at this Docker stack, pinned BF16 Nano snapshot, `max-model-len=8192`, short greedy prompts, concurrency 1/2/4.  
**Not claimed:** Validated, Optimized, Production-ready, long context, decode-only tok/s as a product number.

## Stack

- Device: AMD Instinct MI300X VF (SR-IOV), ~191.67 GiB HBM
- Image: `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0` (`sha256:ac1be45dac88…`)
- vLLM: `0.23.1.dev1+g9ddef7117.d20260715`
- PyTorch `2.11.0+rocm7.14.0`, HIP 7.14.60850
- Checkpoint: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`
- Flags: BF16, TP=1, `max-model-len=8192`, `gpu-memory-utilization=0.80`, `--generation-config vllm`, `--trust-remote-code`, `qwen3_coder`, `nano_v3` plugin
- NVIDIA FlashInfer / NVFP4 / TRT-LLM flags not used
- Tuned MoE JSON: none (`VLLM_TUNED_CONFIG_FOLDER` unset; prior autotune FAIL `2026-08-16_020625Z`)

## Memory

Source: `benchmark/memory-*.txt`, vLLM logs, `logs/gpu-monitor.tsv`.

| Phase | VRAM used | GPU use | Package power |
| --- | --- | --- | --- |
| Before serve | 0.279 GiB | 0% | 158 W |
| After load (idle serve) | 154.65 GiB | 0% | 196 W |
| After 2 warmup chats | 154.83 GiB | 18% | 294 W |
| After conc 1/2/4 | 154.85 GiB | 45% | 405 W |
| Monitor peak (2s samples) | 154.87 GiB | 100% | 651 W |
| Immediate `docker rm` | 143.81 GiB | 1% | 214 W |
| Later host check | 0.279 GiB | 0% | — |

vLLM log: weights **58.91 GiB / 25.85 s**; available KV cache **91.13 GiB**; logged GPU KV size **7,780,352 tokens**; “maximum concurrency for 8,192 tokens per request: 949.75x” is a cache-capacity line, **not** a measured throughput.

Idle allocated VRAM is dominated by `--gpu-memory-utilization 0.80` KV reservation, not by the short generate itself. Peak used during this ladder is only ~0.22 GiB above idle.

Immediate post-stop VRAM was still ~144 GiB; a later host check returned to the 0.279 GiB baseline. Treat that as teardown lag, not a leak claim.

## Short generate / concurrency

Prompt: factorial Python function; `temperature=0`, `enable_thinking=False`, `max_tokens=128`, streaming. Two warmup chats (3 completion tokens each) were **not scored**. Scored requests: 4 per concurrency level.

TTFT is first SSE chunk, not a decode-only timer. `output_tokens_per_sec` is completion tokens / end-to-end, **including** prefill.

| Concurrency | Requests | Success | Wall | Completion tokens | Aggregate completion tok/s | Per-request e2e mean | Per-request TTFT p50 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4 | 4/4 | 1.292 s | 244 | 188.8 | 0.323 s | 0.027 s |
| 2 | 8 | 8/8 | 1.695 s | 488 | 287.9 | 0.423 s | 0.052 s |
| 4 | 16 | 16/16 | 2.007 s | 989 | 492.8 | 0.490 s | 0.053 s |

Context: ~42 prompt tokens; typically 61 completion tokens (one conc-4 request produced 74). This is **not** a 8K-context result even though `max-model-len=8192`.

Do not quote a naked tokens/sec number without this hardware, image, revision, BF16, 8192 serve cap, short prompt, concurrency, and date.

## Material caveats (do not hide)

- Same missing MI300X fused-MoE config `E=128,N=1856` as `223840Z`.
- Same missing Mamba SSU config; Triton SSU backend.
- Same ROCm custom paged-attention fallback (Triton).
- Triton JIT still fired on first warmup (`_fwd_kernel` and related); warmup 1 was 1.89 s vs warmup 2 at 0.03 s.
- Sample size is small (28 scored requests). No context ladder beyond this serve cap.
- Pinning the revision here does **not** by itself earn **Validated** for the earlier Transformers/API runs.
- Not Optimized: autotune still FAIL; default kernels still in use.

Command: `vllm/launch-command.txt`. Logs: `vllm/logs/`, `logs/orchestrator.log`. Monitor: `logs/gpu-monitor.tsv`. Server was stopped after the run.
