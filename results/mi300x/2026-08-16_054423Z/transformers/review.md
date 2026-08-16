# Review: Nano 4B BF16 Transformers smoke (thinking off)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: Nano 4B BF16, revision `dfaf35de3e30f1867dd8dbc38a7fc9fb52d3914f`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850, 1× Instinct MI300X VF, greedy, `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, vLLM, GGUF, Nano **30B**, Radeon, Ryzen AI.

Environment snapshot for the host remains `results/mi300x/2026-08-15_172057Z/environment/`. This is **not** a Nano 30B result. Architecture is dense hybrid (`NemotronHForCausalLM`), not MoE.

## Stack

- Device: AMD Instinct MI300X VF (SR-IOV)
- Load ~7.44 GiB allocated in 17.4 s (includes first HF download of `model.safetensors` ~7.95 GB)
- `trust_remote_code` not required
- `config.json`: `model_type=nemotron_h`, `auto_map` present (same native Transformers path as Nano 30B)

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM vs storage; volatile vs persistent. |
| simple-reasoning | Reasonable | `8 × 192 = 1536 GB`. |
| code | Reasonable | Iterative factorial; extra negative-input raise is acceptable. |
| summarization | Reasonable | Two sentences; MI300X/ROCm and empirical Nemotron caveat. Hit 96-token cap mid-clause. |
| instruction-following | Reasonable | Exact JSON keys `gpu_name` / `hbm_gb` / `status`. |

## Material caveats

- Still an SR-IOV VF.
- Informal ~42–51 tok/s is **not** a benchmark.
- Official GGUF sibling **NOT TESTED**.
- Do not copy this label onto Lightning, Omni, or Nano 30B FP8.

Logs: `logs/transformers-smoke-test.log`.
