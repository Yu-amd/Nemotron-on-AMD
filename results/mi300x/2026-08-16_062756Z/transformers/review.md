# Review: Nemotron 3.5 Lightning 30B BF16 Transformers smoke

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: Lightning 30B-A3B BF16, revision `d468880b6ad3c6e0d21377ce7242adaea4cc884d`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850, 1× Instinct MI300X VF, greedy, `enable_thinking=false` (harness), `prompts/smoke-tests.json`, SDPA.  
**Not claimed:** Optimized, Production-ready, vLLM, FlashInfer, Nano 30B, FP8, Radeon, Ryzen AI.

This is **not** Nano. Architecture `NemotronHForCausalLM` / `nemotron_h`. `trust_remote_code` not required. Load ~59.0 GiB allocated / ~60.0 GiB reserved (~74 s). No `--mamba-backend flashinfer`. First argv-bug dir `062425Z` did not load.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM vs storage, three sentences. |
| simple-reasoning | Reasonable | Exact `1536 GB` and `8 × 192`. |
| code | Reasonable | Iterative factorial; wrapped in a markdown fence despite “no text around the function.” |
| summarization | Reasonable | Two sentences; hit 96-token cap mid-clause (no period on sentence 2). |
| instruction-following | Reasonable | Exact JSON keys `gpu_name` / `hbm_gb` / `status`. |

## Caveats

- Still an SR-IOV VF.
- Informal tok/s not recorded as a benchmark.
- Do not copy this label onto Omni or Nano FP8.

Logs: `logs/family-smoke.log`.
