# Review: Unsloth Nano 30B-A3B GGUF on Strix Point CPU (llama.cpp)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` file `Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf`, revision `9ad8b366c308f931b2a96b9306f0b41aef9cd405`, sha256 `0e7f6e51fdd9039928749d07eed9e846dbfd97681646544c5406bcdd788e5940` (24 574 373 664 bytes), llama.cpp **b10453** Ubuntu CPU binary (`3cb7ffb1a`), **CPU** (`--n-gpu-layers 0`) on this Ryzen AI 9 HX 370 laptop (93 GiB RAM), greedy, jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Official NVIDIA 30B GGUF, Optimized, Production-ready, iGPU, NPU, Vulkan, HIP, MI300X, Transformers, vLLM.

This is a **community** Unsloth conversion (Spark cookbook lineage), not `nvidia/` 30B GGUF. Actual Q4_K_M is **24.57 GB**, not the old 14 GiB calculator. Environment snapshot: `results/ryzen-ai/2026-08-16_214028Z/environment/`.

## Stack

- Runtime: llama.cpp CLI
- Architecture: `nemotron_h_moe`
- `--single-turn` is required.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM volatile vs storage persistent |
| simple-reasoning | Reasonable | `1536` from 8×192 |
| code | Reasonable | Iterative factorial with 0 base case |
| summarization | Reasonable | Two-sentence class; hit 96-token cap mid-clause |
| instruction-following | Reasonable | Exact JSON keys |

Logs: `logs/llama-*.stdout.log`.
