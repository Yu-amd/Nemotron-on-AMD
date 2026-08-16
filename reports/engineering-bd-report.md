# Nemotron on AMD — Technical Validation Report

Audience: engineers, solution architects, and technical BD.  
Date: **2026-08-16**. Hands-on target: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` on 1× Instinct **MI300X VF** (SR-IOV), ~191.7 GiB HBM.

Companion plain-language note: [`executive-report.md`](executive-report.md). Ledger: [`evidence-summary.md`](evidence-summary.md).

## 1. Conclusion

| Claim | Status | Bound |
| --- | --- | --- |
| Transformers greedy, thinking off, `prompts/smoke-tests.json` | **Validated** | Pinned revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850. Artifact `results/mi300x/2026-08-16_031205Z/`. |
| Transformers thinking on/off | **Runs** | Same revision, `prompts/reasoning-tests.json`. `024048Z`. |
| vLLM OpenAI-compatible serve | **Runs** / **PASS WITH CAVEATS** | AMD image `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0`, vLLM `0.23.1.dev1`, torch `2.11.0+rocm7.14.0`, Python 3.14. First API PASS `223840Z` (revision unset in metadata). Later serves pinned the same snapshot. |
| Short-context engineering characterization | **Runs**, not a benchmark | Conc 1/2/4, `022238Z`. |
| Context ladder 4K→128K needle/haystack | **Runs**, not a benchmark | `024220Z`. **Not** 256K/1M. |
| Fused-MoE autotune JSON for MI300X | **FAIL** | `020625Z`, `ActorDiedError`, no JSON. |
| Super BF16 on this 1× MI300X | **NOT TESTED** | Fit **2×** OAM. Do not download on the current 1-GPU VF. |
| Ultra BF16 | **NOT TESTED** | Fit **8×** MI300X/MI325X, **4× tight** MI350X/MI355X. **Doesn't fit** MI350P / Radeon / Ryzen AI. |
| Discrete Radeon Nemotron | **NOT TESTED** | No discrete Radeon in this phase. |
| Ryzen AI laptop llama.cpp | **Validated** greedy thinking-off | Official Nano 4B, Lightning Q4_0, Unsloth 30B Q4_K_M on CPU and Vulkan UMA. Dedicated 512 MB **doesn't fit**. NPU **NOT TESTED**. |

**Optimized** and **Production-ready** are not earned. Missing `E=128,N=1856` fused-MoE JSON and Mamba SSU JSON for `AMD_Instinct_MI300X`; ROCm custom paged attention falls back to Triton.

## 2. Scope and non-goals

Hands-on hardware: this MI300X VF (KVM/QEMU + SR-IOV) and a Strix Point laptop. Other Instinct SKUs are spec-only (**NOT YET VALIDATED**).

Not copied onto AMD: TensorRT-LLM, NIM, NVFP4, `--mamba-backend flashinfer`, `VLLM_USE_FLASHINFER_MOE_FP4`, CUDA vLLM wheels, 1M context, Super/Ultra downloads.

## 3. Model family (official IDs)

| Model | Official BF16 ID | Params | First AMD call |
| --- | --- | --- | --- |
| Nano 30B-A3B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 30B / 3.5B active, hybrid Mamba-2 MoE + 6 GQA | Execute |
| Nano 4B | `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | ~3.97B; official GGUF sibling | Later local |
| Super | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | 120B / 12B, LatentMoE + MTP | BF16 Fit **2×** MI300X; **doesn't fit** PCIe/laptop |
| Ultra | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | 550B / 55B | BF16 Fit **8×** MI300X; **4× tight** MI350X |
| Nano Omni | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | ~31B / ~3B | **NOT TESTED** |
| Lightning 3.5 | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | 30B / 3B | Inventoried; **not first** |
| Embed 1B | `nvidia/Nemotron-3-Embed-1B-BF16` | ~1.14B encoder | Later local |
| Safety 4B / 8B | Gemma-3 4B / Llama 3.1 8B IDs in inventory | 4B / 8B | Later; not hybrid Nano |

Snapshot used for all Nano BF16 GPU runs after cache fill: `refs/main` = `2d59de1cbd51c0adf384eb906b766d1aee0e0517`. Cached `config.json`: `model_type=nemotron_h`, `max_position_embeddings=262144`, 128 routed + 1 shared expert, top-6, `moe_intermediate_size=1856`. `auto_map` names `modeling_nemotron_h.py`, which is **not** in the snapshot; Transformers 5.15.0 still loads without `trust_remote_code`. See `results/mi300x/2026-08-16_031205Z/transformers/config-excerpt.json`.

## 4. Hardware

| SKU | Memory | ISA | Role | Nemotron |
| --- | --- | --- | --- | --- |
| MI300X VF | ~191.7 GiB HBM | gfx942 CDNA3 | Execute | Validated Transformers smoke; vLLM Runs through 128K |
| MI325X | 256 GB HBM3E | gfx942 | Theory | **NOT YET VALIDATED** |
| MI350X / MI355X | 288 GB HBM3E | gfx950 CDNA4 | Theory | **NOT YET VALIDATED** |
| MI350P | 144 GB HBM3E PCIe | CDNA4 (LLVM unconfirmed) | Theory | **NOT YET VALIDATED**; Super BF16 does not fit; not named on the ROCm Instinct GPU table fetched 2026-08-16 |
| Radeon W7900 / AI PRO R9700 / RX 7900/9000 | 16–48 GB class | RDNA3/4 | Docs only | **NOT TESTED**; 30B BF16 not practical |
| Strix Point iGPU | 512 MB dedicated VRAM reported; ~47 GiB Vulkan UMA | gfx1150, ROCm 6.4.3 | Local | Dedicated VRAM **doesn't fit** 18–25 GB GGUFs. Vulkan UMA **Validated** llama.cpp for Nano 4B, Lightning Q4_0, Unsloth 30B Q4_K_M. NPU **NOT TESTED**. vLLM gfx1150 wants ROCm 7.0.2+ |
| Strix Point NPU | XDNA `aie2` present | DSP | Local | **NOT APPLICABLE** until a Nemotron path exists |

Host split: `/opt/rocm/.info/version` **7.0.2**; HIP / amd-smi / torch **7.14**. Wheel choice follows HIP.

## 5. Software paths

| Stack | NVIDIA card | This repo |
| --- | --- | --- |
| Transformers | ≥5.3.0; official snippet has no `trust_remote_code` | `.venv-mi300x`, 5.15.0, **Validated** smoke |
| vLLM | ≥0.12.0, `nano_v3` plugin, `qwen3_coder`, `--trust-remote-code` | Docker only: AMD CDNA ROCm 7.14 image; host CPython 3.12 has no matching 7.14 wheel |
| llama.cpp | Official Nano 4B GGUF; community Nano 30B GGUF; ggml-org Lightning Q4_0 | **Validated** greedy thinking-off: Nano 4B, Lightning Q4_0, Unsloth 30B Q4_K_M on laptop CPU, Vulkan UMA, and 1× MI300X HIP. Not NPU. Not discrete Radeon. Not official NVIDIA 30B GGUF |
| TRT-LLM / NIM / FlashInfer | First-class NVIDIA | Documented as NVIDIA-specific; not used |

## 6. Method

Env snapshot → isolated venv (no CUDA wheels, no OS/ROCm upgrades) → Transformers greedy thinking-off → thinking probes → conservative vLLM → OpenAI API → memory + conc 1/2/4 → context 4K→128K. New timestamped `results/` dirs. Failures classified (`MODEL ARCHITECTURE | TRANSFORMERS | …`). Full PASS rules: [`docs/methodology.md`](../docs/methodology.md), [`docs/terminology.md`](../docs/terminology.md).

## 7. MI300X evidence (in time order)

Environment: [`results/mi300x/2026-08-15_172057Z/environment/`](../results/mi300x/2026-08-15_172057Z/environment/).

| Run | Result | What it proved |
| --- | --- | --- |
| `172557Z` | **FAIL** | Load ~58.9 GiB OK. Generate died: `BatchEncoding` vs Tensor (`encoded.shape`). Layer TOKENIZER/harness. Preserved. |
| `172810Z` | **PASS** / **Runs** | 5/5 greedy smoke. Revision **unset**. Review judged reasonable. |
| `223840Z` | **PASS** / **Runs** | vLLM health, models, thinking off/on (1536 + reasoning field), sequential 1/2/3. Load 58.91 GiB / 25.9 s. Revision unset in metadata. |
| `020625Z` | **FAIL** | `benchmark_moe.py --tune` ~2h17m; Ray `ActorDiedError` ~99% of a 4.48k pass; no JSON; `OOMKilled=false`. |
| `022238Z` | characterization | Weights 58.91 GiB; idle VRAM after load ~154.7 GiB at `gpu-memory-utilization=0.80` (KV reserved 91.13 GiB). Conc 1/2/4 all 100% success. |
| `024048Z` | **PASS** / **Runs** | Thinking on/off 5/5. Opening `<think>` is template-prefill; `</think>` leaks in Transformers decode. |
| `024220Z` | ladder **PASS WITH CAVEATS** | Serve 16K/32K/64K/128K. Needle recovered `COLOR=indigo NUMBER=4172` at ~4K–128K. 128K: 127916 prompt tokens, 19.2 s e2e. |
| `031205Z` | **Validated** | Pinned reproduction of `smoke-tests.json`, 5/5. Same allocated ~58.9 GiB. |
| `215228Z` | **Validated** | llama.cpp HIP gfx942 official Nano 4B Q4_K_M, 5/5, 43/43 layers on ROCm0. |
| `225542Z` | **Validated** | llama.cpp HIP gfx942 Lightning ggml-org Q4_0, 5/5, 53/53 layers on ROCm0. |
| `231304Z` | **Validated** | llama.cpp HIP gfx942 Unsloth Nano 30B Q4_K_M, 5/5, 53/53 layers on ROCm0. Community file. |

Do not quote tokens/s without hardware, image/venv, revision, precision, context, concurrency, and date.

### Informal performance (engineering characterization only)

Transformers `generate` (`172810Z`): ~6 tok/s first prompt, ~22–31 tok/s later short prompts. Pinned smoke (`031205Z`): ~9 tok/s then ~28–30 tok/s.

vLLM streaming, greedy, thinking off, ~42 prompt / ~61 completion tokens, `max-model-len=8192`, image as above, revision `2d59de1…` (`022238Z`):

| Concurrency | Success | Wall | Aggregate completion tok/s (tokens / wall) |
| --- | --- | --- | --- |
| 1 | 4/4 | 1.29 s | 188.8 |
| 2 | 8/8 | 1.70 s | 287.9 |
| 4 | 16/16 | 2.01 s | 492.8 |

TTFT is first SSE chunk, not decode-only. Monitor peak: 100% GPU, 651 W, 154.87 GiB VRAM.

Context ladder e2e (same stack, thinking off, 12 completion tokens): ~4K 2.54 s (JIT), ~8K 0.30 s, ~16K 0.84 s, ~32K 3.34 s, ~64K 7.15 s, ~128K 19.21 s. Monitor peak 748 W / 79 C / 154.86 GiB. Filler haystack ≠ RULER / customer documents.

Logged KV at 128K serve: 14.86M tokens capacity, “113× concurrency at 131072” is cache arithmetic, not measured QPS.

## 8. Radeon

**NOT TESTED.** Official ROCm list includes W7900 48 GB, AI PRO R9700, RX 7900 XTX, RX 9070 XT. Realistic Nemotron class: Nano 4B / Embed / quantized Nano, not 30B BF16. Hybrid Mamba-MoE on gfx1100/1201 is unproven.

## 9. Ryzen AI (three targets)

Evidence: [`results/ryzen-ai/2026-08-15_171202Z/environment/`](../results/ryzen-ai/2026-08-15_171202Z/environment/). Ryzen AI 9 HX 370, 93 GiB RAM, gfx1150, NPU `aie2`.

Nano 30B raw payload vs 93 GiB RAM (weights only, calculator): BF16/FP16 55.9 GiB; FP8/INT8/Q8 27.9; Q4 14.0. Do not download 30B locally. Priority if the laptop is later in scope: Embed 1B, safety 4B, official Nano 4B GGUF — each logged as CPU **or** iGPU **or** NPU, never “Ryzen AI” as one device.

## 10. Precision

BF16 is the native Instinct path we ran. MI300X FP8 is FNUZ; NVIDIA FP8 checkpoints are typically OCP — **Unknown / requires validation**. NVFP4 is NVIDIA-specific until proven; MI350 MXFP4 is not NVFP4. No official Nano 30B INT8/INT4 HF sibling confirmed. Official Nano 4B GGUF exists.

## 11. Limitations already seen on this VF

- NVIDIA software-integration GPUs: H100/A100 (Nano); Super/Ultra are multi-GPU NVIDIA tables.
- Host Python 3.12 vs vLLM image Python 3.14; Transformers torch 2.12 vs vLLM torch 2.11.
- Hybrid Mamba + MoE: default configs missing; Triton paged-attn fallback; Triton JIT on first request of a new shape.
- MoE autotune died; do not copy H100/B200 JSON.
- SR-IOV VF ≠ proven full OAM card.
- Tool-calling prompts exist (`qwen3_coder` enabled) and were **not** scored as a PASS.

## 12–13. What to run vs what not to run

| Goal | Configuration | Status |
| --- | --- | --- |
| Correctness proof | Transformers 5.15, torch 2.12+rocm7.14, greedy, thinking off, pinned `2d59de1…` | **Validated** `031205Z` |
| Serving candidate | Same weights, AMD CDNA vLLM Docker, `nano_v3` + `qwen3_coder`, `max-model-len` 8K–128K | **Runs** |
| Memory / conc / 128K filler | `benchmark.py` / `context-ladder.py` | Engineering characterization only |
| Do not | Super/Ultra download; NVFP4; 1M; FlashInfer flags; NPU claims | — |

## 14. Optimization opportunities (observed gaps only)

- gfx942 fused-MoE `E=128,N=1856` and Mamba SSU JSON (autotune FAIL is the data point)
- Stable ROCm paged attention for hybrid Mamba (block size vs Triton fallback)
- FP8 FNUZ vs OCP if customers insist on NVIDIA FP8 checkpoints
- NVFP4 vs MXFP4 naming trap on MI350
- llama.cpp HIP/Vulkan for official Nano 4B, Lightning ggml-org Q4_0, and Unsloth Nano 30B Q4_K_M — **Validated** greedy thinking-off; not Optimized

These are not committed AMD work items.

## 15. BD language

| Phrase | Use today? |
| --- | --- |
| **Validated** | Transformers greedy thinking-off Nano BF16 on this VF (`031205Z`); llama.cpp greedy thinking-off Nano 4B / Lightning Q4_0 / Unsloth 30B Q4_K_M on HIP + laptop CPU/Vulkan |
| **Experimental / Runs** | vLLM serve, 128K ladder, thinking-on, characterization |
| **Feasible but unvalidated** | Super FP8 on 1× MI300X; discrete Radeon |
| **Not applicable** | NVFP4 as an AMD-native precision until a path exists |
| **Unknown** | FP8 on MI300X; NPU; Optimized kernels |

Unsafe: “Nemotron supports AMD,” “production-ready on Instinct,” “runs on Ryzen AI NPU.”

## 16. Next steps

1. Optional pinned vLLM API re-run if serving should become Validated.
2. Optional 256K; never jump to 1M.
3. No Super/Ultra download, no NVFP4, no second MoE autotune unless asked.
4. Discrete Radeon still untested. NPU still **NOT TESTED**.
