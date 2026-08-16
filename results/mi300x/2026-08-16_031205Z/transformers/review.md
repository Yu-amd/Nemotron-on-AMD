# Review: pinned Transformers smoke (thinking off)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: Nano 30B BF16, revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850, 1× Instinct MI300X VF, greedy, `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, vLLM Validated, thinking-on as Validated, 256K/1M, Radeon, Ryzen AI.

This is a pinned reproduction of `2026-08-15_172810Z` (that run left `model_revision` unset). Environment snapshot for the host remains `results/mi300x/2026-08-15_172057Z/environment/`.

## Stack

- Device: AMD Instinct MI300X VF (SR-IOV)
- Load ~58.9 GiB allocated in 8.83 s from HF cache
- `trust_remote_code` not required
- Cached `config.json`: `model_type=nemotron_h`, `auto_map` names `modeling_nemotron_h.py` which is **not** in the snapshot; Transformers 5.15.0 still loads. `max_position_embeddings=262144`. See `config-excerpt.json`.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM volatile / storage non-volatile, three sentences. |
| simple-reasoning | Reasonable | `8 × 192 = 1536`. |
| code | Reasonable | Iterative factorial, `n == 0` returns 1, no extra prose. |
| summarization | Reasonable | Two sentences; MI300X 192 GB, ROCm/PyTorch/vLLM, empirical caveat. |
| instruction-following | Reasonable | Exact JSON keys `gpu_name` / `hbm_gb` / `status`. |

## Material caveats

- Still an SR-IOV VF, not a proven full OAM card.
- First smoke FAIL `172557Z` remains in the record (TOKENIZER/harness).
- Informal generate rates ~9 tok/s then ~28–30 tok/s are **not** a benchmark.
- `config.auto_map` is present; native Transformers `nemotron_h` was sufficient here.
- vLLM remains **Runs** / **PASS WITH CAVEATS** (Docker/torch 2.11 split; missing MI300X MoE/Mamba configs). Do not copy this Validated label onto serving or 128K.

Logs: `logs/transformers-smoke-test.log`.
