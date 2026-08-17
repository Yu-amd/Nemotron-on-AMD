# Nemotron on AMD — Technical Validation Report

Audience: engineers, solution architects, and technical BD.  
Date: **2026-08-16**. Hands-on hardware: 1× Instinct **MI300X VF** (SR-IOV), ~191.7 GiB HBM, and a Strix Point **Ryzen AI 9 HX 370** laptop (gfx1150, 93 GiB RAM).

Companion plain-language note: [`executive-report.md`](executive-report.md). Ledger: [`evidence-summary.md`](evidence-summary.md). Matrix: [`../docs/compatibility-matrix.md`](../docs/compatibility-matrix.md).

## 1. Conclusion

**Optimized** and **Production-ready** are not earned. Missing `E=128,N=1856` fused-MoE JSON and Mamba SSU JSON for `AMD_Instinct_MI300X`; ROCm custom paged attention falls back to Triton. Do not copy NVIDIA FlashInfer / NVFP4 flags.

### Generative (language models)

| Claim | Status | Bound |
| --- | --- | --- |
| Nano 30B-A3B BF16 Transformers greedy, thinking off, `prompts/smoke-tests.json` | **Validated** | Pinned revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850. Artifact `results/mi300x/2026-08-16_031205Z/`. First FAIL kept (`172557Z`). |
| Nano 30B BF16 Transformers thinking on/off | **Runs** | Same revision, `prompts/reasoning-tests.json`. `024048Z`. |
| Nano 30B BF16 vLLM OpenAI-compatible serve | **Runs** / **PASS WITH CAVEATS** | AMD image `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0`, vLLM `0.23.1.dev1`. First API PASS `223840Z`. Characterization conc 1/2/4 `022238Z`. Context ladder through **128K** `024220Z`. **Not** 256K/1M. **Not** Optimized. Only Nano 30B has a vLLM ladder. |
| Nano 30B FP8 Transformers | **FAIL** | `mamba-ssm` import (`062923Z`). **R-FNUZ**. Do not install CUDA mamba-ssm. |
| Nano 30B GGUF Q4_K_M (Unsloth, community) | **Validated** | llama.cpp greedy thinking-off on laptop CPU `225528Z`, Vulkan UMA `225631Z`, MI300X HIP `231304Z`. Not official NVIDIA 30B GGUF. Dedicated 512 MB **doesn't fit**. |
| Nano 4B BF16 Transformers greedy thinking-off | **Validated** | `054423Z`, revision `dfaf35de…`. Not MoE. |
| Nano 4B BF16 vLLM | **Runs** | OpenAI API `max-model-len=8192` (`170637Z`). Not 128K. |
| Nano 4B FP8 Transformers | **Runs**, not Validated | Looping `A` on all five prompts (`170427Z`). **R-FNUZ**. |
| Nano 4B GGUF Q4_K_M (official NVIDIA) | **Validated** | CPU `214142Z`, Vulkan UMA `214348Z`, MI300X HIP `215228Z`. First harness FAIL kept (`214028Z-cpu`). Dedicated 512 MB **doesn't fit**. |
| Lightning 30B-A3B BF16 Transformers greedy thinking-off | **Validated** | `062756Z`, revision `d468880b…`. Not Nano. No FlashInfer. |
| Lightning 30B BF16 vLLM | **Runs** | OpenAI API `max-model-len=8192` (`170852Z`). Not the 128K ladder. |
| Lightning GGUF Q4_0 (ggml-org) | **Validated** | CPU `223932Z`, Vulkan UMA `224120Z`, MI300X HIP `225542Z`. Q8_0 / BF16 GGUF **NOT TESTED**. |
| Nano Omni 30B BF16 | **FAIL** | RADIO `min_resolution_step` after FA2/Tee workarounds (`063955Z`; earlier FA2 `062426Z`). |
| Nano Omni 30B FP8 | **FAIL** | `mamba-ssm` (`063016Z`). **R-FNUZ**. |
| Super 120B BF16 on this 1× MI300X | **NOT TESTED** | Fit **2×** OAM. Do not download on the current 1-GPU VF. |
| Super 120B FP8 Transformers | **FAIL** | `mamba-ssm` (`063022Z`). Fit **1×**. **R-FNUZ** + LatentMoE + MTP. |
| Ultra BF16 / NVFP4 | **NOT TESTED** | BF16 Fit **8×** MI300X/MI325X, **4× tight** MI350X/MI355X. NVFP4 Fit **2×** plus **R-NVFP4**. **Doesn't fit** MI350P / Radeon / Ryzen AI. Not downloaded. |
| Discrete Radeon Nemotron | **NOT TESTED** | No discrete Radeon in this phase. |
| Ryzen AI NPU | **NOT TESTED** | **R-NPU**. Driver present ≠ model support. |
| Fused-MoE autotune JSON for MI300X | **FAIL** | Nano 30B BF16 `020625Z`, `ActorDiedError`, no JSON. |

### Embed / parse / ASR / safety (1× MI300X Transformers)

All of these are **Runs** unless marked FAIL. None is MTEB, OCR eval, ASR WER, or a red-team.

| Product | Status | Evidence |
| --- | --- | --- |
| Embed 1B BF16 | **Runs** mean-pool cosine. Not MTEB. | `054857Z` |
| Embed 8B BF16 | **Runs** cosine. Yarn warning. | `055129Z` |
| text rerank 1B v2 | **Runs** relevant > irrelevant. Custom `llama_bidirec`. | `055206Z` |
| VL embed 1B v2 BF16 | **Runs** dummy PNG forward. Empty `CausalLMOutputWithPast` (no embedding tensor). | `062402Z` |
| VL embed 1B v2 FP8 | **FAIL** `create_bidirectional_mask`. **R-FNUZ**. | `170519Z` |
| VL rerank 1B v2 BF16 | **Runs** **text** path only. Images not passed. | `055737Z` |
| VL rerank 1B v2 FP8 | **FAIL** ranking (relevant < irrelevant). Loaded. **R-FNUZ**. | `170557Z` |
| ColEmbed VL 3B / 4B / 8B v2 | **Runs** dummy PNG. | `055802Z`, `061905Z`, `061921Z` |
| Omni embed 3B | **Runs** dummy image. Not Nano Omni LM. | `061940Z` |
| Parse 2.0 | **Runs** dummy PNG generate. Not OCR eval. | `063558Z` |
| ASR 3.5 0.6B | **Runs** Transformers pipeline. Tone → empty text. | `060037Z` |
| Content Safety 3.5 | **Runs** `User Safety: safe` shape. Gemma-3, not hybrid Nano. | `055324Z` |
| Safety Guard 8B v3 | **Runs** generate. First prompt was chat (“Paris”), not a Guard schema. | `055356Z` |

## 2. Scope and non-goals

Hands-on hardware: this MI300X VF (KVM/QEMU + SR-IOV) and a Strix Point laptop. Other Instinct SKUs are spec-only (**NOT YET VALIDATED**).

Not copied onto AMD: TensorRT-LLM, NIM, NVFP4, `--mamba-backend flashinfer`, `VLLM_USE_FLASHINFER_MOE_FP4`, CUDA vLLM wheels, 1M context, Super **BF16** / Ultra downloads.

Lightning **FP8**: no official HF ID in the 2026-08-16 NVIDIA-org census. Not substituted with NVFP4.

## 3. Model family (official IDs)

| Model | Official BF16 (or primary) ID | Params | AMD evidence in this repo |
| --- | --- | --- | --- |
| Nano 30B-A3B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 30B / 3.5B active, hybrid Mamba-2 MoE + 6 GQA | Transformers **Validated**; vLLM **Runs** through 128K; Unsloth GGUF **Validated** CPU/Vulkan/HIP; FP8 **FAIL** |
| Nano 4B | `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | ~3.97B dense hybrid; official GGUF sibling | Transformers **Validated**; vLLM **Runs** 8K; official GGUF **Validated** CPU/Vulkan/HIP; FP8 **Runs** (looping, not Validated) |
| Lightning 3.5 | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | 30B / 3B | Transformers **Validated**; vLLM **Runs** 8K; ggml-org Q4_0 **Validated** CPU/Vulkan/HIP. No FlashInfer. |
| Super | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | 120B / 12B, LatentMoE + MTP | BF16 Fit **2×** MI300X, not downloaded. FP8 **FAIL** `mamba-ssm`. **Doesn't fit** PCIe/laptop in BF16. |
| Ultra | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | 550B / 55B | BF16 Fit **8×** MI300X; **4× tight** MI350X. Not downloaded. |
| Nano Omni | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | ~31B / ~3B | BF16 **FAIL** RADIO; FP8 **FAIL** `mamba-ssm` |
| Embed 1B / 8B | `nvidia/Nemotron-3-Embed-1B-BF16`, `…-Embed-8B-BF16` | ~1.14B / ~8B encoder | **Runs** cosine. Not MTEB. |
| Retriever / VL / ColEmbed / omni-embed | Llama-Nemotron and omni-embed IDs in inventory | 1B–8B class | **Runs** text or dummy image. VL embed FP8 and VL rerank FP8 **FAIL**. |
| Parse 2.0 / ASR 3.5 | `nvidia/NVIDIA-Nemotron-Parse-2.0`, `nvidia/nemotron-3.5-asr-streaming-0.6b` | Parse / 0.6B | **Runs**. Not OCR/WER eval. |
| Safety 4B / 8B | Gemma-3 4B / Llama 3.1 8B IDs in inventory | 4B / 8B | **Runs**. Not hybrid Nano. Not a red-team. |

Snapshot used for all **Nano 30B BF16** GPU runs after cache fill: `refs/main` = `2d59de1cbd51c0adf384eb906b766d1aee0e0517`. Cached `config.json`: `model_type=nemotron_h`, `max_position_embeddings=262144`, 128 routed + 1 shared expert, top-6, `moe_intermediate_size=1856`. `auto_map` names `modeling_nemotron_h.py`, which is **not** in the snapshot; Transformers 5.15.0 still loads without `trust_remote_code`. See `results/mi300x/2026-08-16_031205Z/transformers/config-excerpt.json`. Nano 4B and Lightning use **different** pinned revisions (`dfaf35de…`, `d468880b…`).

## 4. Hardware

| SKU | Memory | ISA | Role | Nemotron |
| --- | --- | --- | --- | --- |
| MI300X VF | ~191.7 GiB HBM | gfx942 CDNA3 | Execute | Nano/Lightning BF16 Transformers **Validated**; vLLM **Runs** (Nano 30B through 128K; Nano 4B and Lightning at 8K); llama.cpp HIP **Validated** for three GGUFs; family embed/tools **Runs**; Omni BF16 + Nano/Omni/Super FP8 **FAIL** |
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
| Transformers | ≥5.3.0; official snippet has no `trust_remote_code` | `.venv-mi300x`, 5.15.0. Nano 30B / Nano 4B / Lightning BF16 **Validated** smoke. Family embed/tools **Runs**. Omni BF16 and several FP8 **FAIL**. |
| vLLM | ≥0.12.0, `nano_v3` plugin, `qwen3_coder`, `--trust-remote-code` | Docker only: AMD CDNA ROCm 7.14 image; host CPython 3.12 has no matching 7.14 wheel. **Runs** for Nano 30B, Nano 4B, Lightning BF16. Only Nano 30B has 128K ladder / conc characterization. |
| llama.cpp | Official Nano 4B GGUF; community Nano 30B GGUF; ggml-org Lightning Q4_0 | **Validated** greedy thinking-off on laptop CPU, Vulkan UMA, and 1× MI300X HIP. Not NPU. Not discrete Radeon. Not official NVIDIA 30B GGUF. AMD Docker `rocm/llama.cpp` b6652 is too old for `nemotron_h_moe`. |
| TRT-LLM / NIM / FlashInfer | First-class NVIDIA | Documented as NVIDIA-specific; not used |

## 6. Method

Env snapshot → isolated venv (no CUDA wheels, no OS/ROCm upgrades) → Transformers greedy thinking-off → thinking probes → conservative vLLM → OpenAI API → memory + conc 1/2/4 → context 4K→128K. Family queue: small models, then Lightning/Omni BF16, then FP8 FNUZ research, then vLLM for already-Validated 1× BF16. llama.cpp: pinned b10453 CPU → Vulkan → HIP; `--single-turn` required. New timestamped `results/` dirs. Failures classified (`MODEL ARCHITECTURE | TRANSFORMERS | …`). Full PASS rules: [`docs/methodology.md`](../docs/methodology.md), [`docs/terminology.md`](../docs/terminology.md).

A Transformers PASS is not a vLLM PASS. A GGUF PASS is not a Transformers PASS.

## 7. MI300X evidence

Environment: [`results/mi300x/2026-08-15_172057Z/environment/`](../results/mi300x/2026-08-15_172057Z/environment/).

### 7.1 Nano 30B-A3B BF16 (in time order)

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

Do not quote tokens/s without hardware, image/venv, revision, precision, context, concurrency, and date.

#### Informal performance (engineering characterization only; Nano 30B BF16)

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

### 7.2 Other generative Transformers / vLLM on this VF

| Run | Model | Result | Note |
| --- | --- | --- | --- |
| `054423Z` | Nano 4B BF16 | **Validated** | Greedy thinking-off 5/5. Not MoE. |
| `170637Z` | Nano 4B BF16 vLLM | **Runs** | OpenAI `8192`. Not Validated serving. |
| `170427Z` | Nano 4B FP8 | **Runs**, not Validated | Looping `A`. **R-FNUZ**. |
| `062756Z` | Lightning 30B BF16 | **Validated** | Greedy thinking-off 5/5. No FlashInfer. |
| `170852Z` | Lightning 30B BF16 vLLM | **Runs** | OpenAI `8192`. Not Nano. Not 128K. |
| `062426Z` / `063955Z` | Omni 30B BF16 | **FAIL** | FA2 then RADIO `min_resolution_step`. |
| `062923Z` | Nano 30B FP8 | **FAIL** | `mamba-ssm`. **R-FNUZ**. |
| `063016Z` | Omni 30B FP8 | **FAIL** | `mamba-ssm`. **R-FNUZ**. |
| `063022Z` | Super 120B FP8 | **FAIL** | `mamba-ssm`. Fit **1×**. |

Queue IDs and revisions: [`docs/mi300x-next-tests.md`](../docs/mi300x-next-tests.md).

### 7.3 llama.cpp HIP gfx942

| Run | File | Result |
| --- | --- | --- |
| `215228Z` | Official Nano 4B Q4_K_M | **Validated** 5/5, 43/43 layers on ROCm0 |
| `225542Z` | Lightning ggml-org Q4_0 | **Validated** 5/5, 53/53 layers on ROCm0, buffer ~17658 MiB |
| `231304Z` | Unsloth Nano 30B Q4_K_M | **Validated** 5/5, 53/53 layers on ROCm0, buffer ~23197 MiB. Community file. |

HIP `llama-cli` built at tag b10453, `GPU_TARGETS=gfx942`. `--llama-arg=-dev --llama-arg=ROCm0`. `--single-turn` required.

### 7.4 Embed / parse / ASR / safety (canonical dirs)

Earlier FAIL or retry dirs exist (`055228Z`, `055234Z`, `055241Z`, `055257Z`, `055303Z`, `055308Z`, `055715Z`, `055835Z`, `055910Z`, `055953Z`, `060030Z`, `061846Z`, `061956Z`, `062418Z`, `062739Z`, `063238Z`, and Omni retries). Canonical **Runs** / **FAIL** dirs are those in §1.

## 8. Radeon

**NOT TESTED.** Official ROCm list includes W7900 48 GB, AI PRO R9700, RX 7900 XTX, RX 9070 XT. Realistic Nemotron class: Nano 4B / Embed / quantized Nano, not 30B BF16. Hybrid Mamba-MoE on gfx1100/1201 is unproven.

## 9. Ryzen AI (three targets)

Environment: [`results/ryzen-ai/2026-08-15_171202Z/environment/`](../results/ryzen-ai/2026-08-15_171202Z/environment/). Reboot session: `2026-08-16_214028Z`. Ryzen AI 9 HX 370, 93 GiB RAM, gfx1150, NPU `aie2`, ROCm 6.4.3.

Each backend is logged separately. “Ryzen AI” is not one device.

| Backend | Nano 4B Q4_K_M (official) | Lightning Q4_0 (ggml-org) | Nano 30B Q4_K_M (Unsloth) |
| --- | --- | --- | --- |
| CPU `-ngl 0` | **Validated** `214142Z` | **Validated** `223932Z` | **Validated** `225528Z` |
| iGPU Vulkan UMA (~47 GiB visible) | **Validated** `214348Z` | **Validated** `224120Z` | **Validated** `225631Z` |
| Dedicated 512 MB VRAM | **doesn't fit** | **doesn't fit** | **doesn't fit** |
| NPU | **NOT TESTED** / **R-NPU** | **NOT TESTED** | **NOT TESTED** |

First CPU harness FAIL (CLI without `--single-turn`): `214028Z-cpu`. Preserved.

Nano 30B **BF16** still **doesn't fit** this laptop. Do not treat Unsloth Q4_K_M as official NVIDIA 30B GGUF. Embed / safety / Parse / ASR on this laptop remain **NOT TESTED**.

## 10. Precision

BF16 is the native Instinct path we ran for Nano 30B, Nano 4B, and Lightning. MI300X FP8 is FNUZ; NVIDIA FP8 checkpoints are typically OCP — **R-FNUZ**. Executed FP8 outcomes: Nano 30B / Omni / Super **FAIL** `mamba-ssm`; Nano 4B FP8 **Runs** looping `A`; VL embed FP8 **FAIL** mask API; VL rerank FP8 **FAIL** ranking. NVFP4 is NVIDIA-specific until proven; MI350 MXFP4 is not NVFP4. No official Nano 30B INT8/INT4 HF sibling confirmed. Official Nano 4B GGUF exists and is **Validated**. Community Unsloth Nano 30B GGUF and ggml-org Lightning Q4_0 are **Validated**. Lightning Q8_0 / BF16 GGUF **NOT TESTED**.

## 11. Limitations already seen on this VF

- NVIDIA software-integration GPUs: H100/A100 (Nano); Super/Ultra are multi-GPU NVIDIA tables.
- Host Python 3.12 vs vLLM image Python 3.14; Transformers torch 2.12 vs vLLM torch 2.11.
- Hybrid Mamba + MoE: default configs missing; Triton paged-attn fallback; Triton JIT on first request of a new shape.
- MoE autotune died; do not copy H100/B200 JSON.
- SR-IOV VF ≠ proven full OAM card.
- Tool-calling prompts exist (`qwen3_coder` enabled) and were **not** scored as a PASS.
- Omni BF16 needs a working RADIO / vision path; FA2 workarounds did not finish the job.
- FP8 on MI300X is not a drop-in of NVIDIA OCP checkpoints.
- AMD `rocm/llama.cpp` Docker b6652 cannot load `nemotron_h_moe`.

## 12–13. What to run vs what not to run

| Goal | Configuration | Status |
| --- | --- | --- |
| Correctness proof, Nano 30B | Transformers 5.15, torch 2.12+rocm7.14, greedy, thinking off, pinned `2d59de1…` | **Validated** `031205Z` |
| Correctness proof, Nano 4B / Lightning | Same venv, their pinned revisions | **Validated** `054423Z`, `062756Z` |
| Serving candidate | Same BF16 weights, AMD CDNA vLLM Docker. Nano 30B 8K–128K; Nano 4B / Lightning 8K only | **Runs** |
| GGUF local / Instinct | llama.cpp b10453 CPU, Vulkan, or HIP gfx942; `--single-turn` | **Validated** for the three files above |
| Memory / conc / 128K filler | Nano 30B BF16 `benchmark.py` / `context-ladder.py` | Engineering characterization only |
| Do not | Super/Ultra download; NVFP4; 1M; FlashInfer flags; NPU claims; CUDA mamba-ssm | — |

## 14. Optimization opportunities (observed gaps only)

- gfx942 fused-MoE `E=128,N=1856` and Mamba SSU JSON (autotune FAIL is the data point)
- Stable ROCm paged attention for hybrid Mamba (block size vs Triton fallback)
- FP8 FNUZ vs OCP if customers insist on NVIDIA FP8 checkpoints (`mamba-ssm` FAIL is the current data)
- NVFP4 vs MXFP4 naming trap on MI350
- Omni RADIO / vision stack on ROCm
- llama.cpp HIP/Vulkan for official Nano 4B, Lightning ggml-org Q4_0, and Unsloth Nano 30B Q4_K_M — **Validated** greedy thinking-off; not Optimized

These are not committed AMD work items.

## 15. BD language

| Phrase | Use today? |
| --- | --- |
| **Validated** | Transformers greedy thinking-off Nano 30B / Nano 4B / Lightning BF16 on this VF; llama.cpp greedy thinking-off official Nano 4B, Lightning Q4_0, Unsloth 30B Q4_K_M on HIP + laptop CPU/Vulkan |
| **Experimental / Runs** | vLLM serve (all three BF16 LMs); Nano 30B 128K ladder, thinking-on, characterization; family embed/parse/ASR/safety; Nano 4B FP8 looping tokens |
| **Failed as executed** | Omni BF16 RADIO; Nano 30B / Omni / Super FP8 `mamba-ssm`; VL embed FP8 mask; VL rerank FP8 ranking; MoE autotune JSON |
| **Feasible but unvalidated** | Super FP8 *memory* on 1× MI300X (execution **FAIL**); discrete Radeon; Lightning Q8_0 GGUF |
| **Not applicable** | NVFP4 as an AMD-native precision until a path exists; NPU until a path exists |
| **Unknown** | Optimized kernels; 256K/1M; other Instinct SKUs |

Unsafe: “Nemotron supports AMD,” “production-ready on Instinct,” “runs on Ryzen AI NPU,” “official NVIDIA 30B GGUF.”

## 16. Next steps

1. Optional pinned vLLM API re-run if serving should become Validated (start with Nano 30B).
2. Optional 256K on Nano 30B; never jump to 1M. Nano 4B / Lightning ladders are still untested.
3. No Super/Ultra download, no NVFP4, no second MoE autotune unless asked.
4. Discrete Radeon still untested. NPU still **NOT TESTED**.
5. Lightning Q8_0 GGUF, Omni GGUF, and laptop embed/safety remain **NOT TESTED**.
