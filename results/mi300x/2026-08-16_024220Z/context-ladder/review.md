# Review: vLLM context ladder (4K → 128K)

**Date:** 2026-08-16  
**Artifact:** `context-ladder/summary.json`  
**Label:** Engineering context ladder only. **Not** an official benchmark.  
**Claim allowed after this review:** **Runs** for this Docker stack, pinned BF16 Nano snapshot, needle/haystack prompts through **128K**, thinking off, greedy.  
**Not claimed:** 256K, 1M, Optimized, Production-ready, real-document long context, decode tok/s as a product number.

## Stack

- Device: AMD Instinct MI300X VF (~191.67 GiB HBM)
- Image: `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0`
- vLLM `0.23.1.dev1+g9ddef7117.d20260715`, torch `2.11.0+rocm7.14.0`
- Revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`
- Serve flags: BF16, TP=1, `gpu-memory-utilization=0.80`, `--generation-config vllm`, no FlashInfer / NVFP4 / TRT-LLM
- Prompt: unique HEAD (`indigo`) and TAIL (`4172`) with repeated filler; question requires both markers

Each longer `max-model-len` was a **new** Docker serve after the previous stage passed.

## Results

| max_model_len | Prompt tokens | e2e | Model reply | Verdict |
| --- | --- | --- | --- | --- |
| 16384 | 3973 (~4K) | 2.541 s | `COLOR=indigo NUMBER=4172` | PASS |
| 16384 | 7991 (~8K) | 0.300 s | same | PASS |
| 16384 | 15986 (~16K) | 0.844 s | same | PASS |
| 32768 | 31976 | 3.337 s | same | PASS |
| 65536 | 63956 | 7.150 s | same | PASS |
| 131072 | 127916 | 19.211 s | same | PASS |

4K was slower than 8K because the first request paid Triton JIT (`fused_moe_kernel`). Weights 58.91 GiB and available KV 91.13 GiB at every stage. Logged GPU KV token capacity changed with `max_model_len` (10.37M at 16K → 14.86M at 128K); the “maximum concurrency” log lines are cache-capacity arithmetic, not measured throughput.

Monitor peak (5 s samples): 100% GPU use, 748 W, 79 C junction, 154.86 GiB VRAM.

256K and 1M were **not** attempted.

## Material caveats

- Same missing MI300X fused-MoE `E=128,N=1856` and Mamba SSU configs as prior serve runs.
- Same ROCm custom paged-attention Triton fallback.
- Filler haystack ≠ customer long documents or RULER.
- Prompt tokens are slightly under the round targets (chat-template slack).
- Not Optimized. Do not quote e2e seconds as a product number without this stack, revision, length, and date.

Server was stopped after the last stage. Logs: `vllm-16384/` … `vllm-131072/`. Orchestrator: `logs/orchestrator.log`.
