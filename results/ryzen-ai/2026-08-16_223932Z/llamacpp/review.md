# Review: Lightning 30B-A3B ggml-org GGUF on Strix Point CPU (llama.cpp)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Validated** for this exact pair: `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` file `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf`, revision `9d425fe18d84ab04da6aabb757d2e2807083d054`, sha256 `61f87e75974e4b535dcdf9aad056541a9514f1dfa4538b463b081d19b7a00e3c` (18 890 809 584 bytes), llama.cpp **b10453** Ubuntu CPU binary (`3cb7ffb1a`), **CPU** (`--n-gpu-layers 0`) on this Ryzen AI 9 HX 370 laptop (93 GiB RAM), greedy, jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, iGPU, NPU, Vulkan, HIP, MI300X, Transformers, vLLM, Lightning BF16/Q8_0, MTP sidecar, Unsloth 30B.

There is **no Q4_K_M** in this ggml-org tree. NVIDIA's Lightning card points at this Q4_0. Environment snapshot for this reboot session: `results/ryzen-ai/2026-08-16_214028Z/environment/`.

## Stack

- Runtime: llama.cpp CLI, **not** Ollama / Lemonade / LM Studio / vLLM
- Architecture: `nemotron_h_moe` (not dense Nano 4B `nemotron_h`)
- Observed ~19–21 tok/s decode in the CLI footer — **not** a benchmark
- `--single-turn` is required. Bare `-no-cnv` is parsed as `-n`.
- MTP draft GGUF was **not** used for this smoke.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| basic-language | Reasonable | RAM volatile vs storage persistent |
| simple-reasoning | Reasonable | `1536 GB` from 8×192 |
| code | Reasonable | Iterative factorial with 0 base case |
| summarization | Reasonable | Two sentences; MI300X/ROCm and empirical Nemotron caveat |
| instruction-following | Reasonable | Exact JSON keys `gpu_name` / `hbm_gb` / `status` |

Logs: `logs/llama-*.stdout.log`.
