# Review: Transformers smoke, thinking off

**Date:** 2026-08-15  
**Artifact:** `result.json` (`result=PASS`, `passed=5/5`)  
**Claim allowed after this review:** **Runs** for this stack and prompt set.  
**Not claimed:** Validated (HF revision unset), Optimized, Production-ready, vLLM serving, thinking-on, long context.

## Stack

- Device: AMD Instinct MI300X VF (SR-IOV), gfx942, ~191.7 GiB HBM
- Runtime: Transformers 5.15.0, PyTorch 2.12.0+rocm7.14.0, HIP 7.14.60850
- Checkpoint: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` (`model_revision` was not recorded)
- Sampling: greedy, `enable_thinking=false`, `max_new_tokens=128`
- Load: ~63.2 GB allocated (~58.9 GiB); `trust_remote_code` not required despite `config.auto_map`

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | Three sentences distinguishing volatile RAM vs non-volatile storage. |
| simple-reasoning | Reasonable | `8 × 192 = 1536` with a one-line calculation. |
| code | Reasonable | Iterative factorial, `n == 0` returns 1, no extra prose. |
| summarization | Reasonable | Two sentences; keeps MI300X 192 GB, ROCm/PyTorch/vLLM, and empirical-evaluation caveat. |
| instruction-following | Reasonable | Exact JSON with the three requested keys and values. |

## Caveats

- First attempt `results/mi300x/2026-08-15_172557Z` **FAIL**ed all five prompts on harness `AttributeError` (`BatchEncoding` vs Tensor). That failure is TOKENIZER/harness, not architecture. Preserve it.
- First generation was ~5.8 tok/s; later prompts ~22–31 tok/s. Treat as unoptimized Transformers generate, not a benchmark.
- Peak reserved ~65.6 GiB during this short-context run.
- Hugging Face snapshot/revision not pinned.
- Thinking-on and vLLM remain **NOT TESTED**.
