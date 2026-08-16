# Review: Nano 4B official GGUF on Strix Point CPU (llama.cpp)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` file `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf`, revision `ba223d14e45525f7fae81db77ea8cabeb2fc6c25`, sha256 `be5d9a656a51922f24f1f09a759cebb694e1f5d9728bf0ef9f8c972c5a0b5ef2`, llama.cpp **b10453** Ubuntu CPU binary (`3cb7ffb1a`), **CPU** (`--n-gpu-layers 0`) on this Ryzen AI 9 HX 370 laptop (93 GiB RAM), greedy, jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, iGPU, NPU, Vulkan, HIP, MI300X, Transformers, vLLM, Nano **30B**.

Environment snapshot for this reboot session: `results/ryzen-ai/2026-08-16_214028Z/environment/`. First harness FAIL (empty summarization parse) is preserved at `results/ryzen-ai/2026-08-16_214028Z-cpu/` — model had generated; parser missed a truncated multi-line echo.

## Stack

- Runtime: llama.cpp CLI, **not** Ollama / Lemonade / LM Studio
- Arch in GGUF metadata: `nemotron_h` (dense hybrid; not `nemotron_h_moe`)
- Observed ~22 tok/s decode in the CLI footer — **not** a benchmark
- `--single-turn` is required. Bare `-no-cnv` is parsed as `-n` and can dump interactive `>` to disk.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM volatile vs storage persistent |
| simple-reasoning | Reasonable | `1536 GB` from 8×192 |
| code | Reasonable | Iterative factorial; extra negative-input raise is acceptable |
| summarization | Reasonable | Two sentences; MI300X/ROCm and empirical Nemotron caveat. Hit 96-token cap mid-clause |
| instruction-following | Reasonable | Exact JSON keys `gpu_name` / `hbm_gb` / `status` |

Logs: `logs/llama-*.stdout.log`.
