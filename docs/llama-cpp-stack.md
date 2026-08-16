# llama.cpp / GGUF stack

This stack is **separate** from Transformers and vLLM. A Validated Transformers or vLLM cell is **not** llama.cpp evidence. A GGUF file is **not** NVFP4.

**Checked:** 2026-08-16  
**Runtimes in this stack:** official `llama.cpp` binaries (CPU, Vulkan, HIP/ROCm). Not Ollama, not Lemonade, not LM Studio, even if those wrap llama.cpp.

Hardware actually available for execution:

| Machine | Role | llama.cpp backends that can be attempted here |
| --- | --- | --- |
| Instinct **MI300X VF** (`gfx942`, ~191.7 GiB HBM, HIP 7.14) | GPU HIP | HIP built against the **existing** ROCm/HIP (do not upgrade). Official Linux ROCm tarballs are not published on every llama.cpp tag. |
| This **Strix Point** laptop (Ryzen AI 9 HX 370, 93 GiB RAM, `gfx1150` iGPU **512 MB** dedicated, ROCm **6.4.3**) | CPU, then Vulkan iGPU | Official Ubuntu CPU + Vulkan binaries. HIP iGPU is a later experiment; 512 MB dedicated VRAM is **R-IGPU**. NPU is **R-NPU**. |
| Discrete Radeon | none in lab | Fit only. HIP/Vulkan **NOT YET VALIDATED**. |

Do not treat a DGX Spark / CUDA llama.cpp cookbook as an AMD result.

## How Fit is counted (this stack)

Same device-class rules as [`compatibility-matrix.md`](compatibility-matrix.md):

- **OAM Instinct:** 1× / 2× / 4× / 8× from **on-disk GGUF bytes**, not naive BF16 calculator. Never “doesn't fit.”
- **MI350P / Radeon / this laptop:** one device or **doesn't fit**. Laptop Fit must name **CPU** vs **iGPU** vs **NPU**.
- Dedicated iGPU VRAM on this Strix Point is **512 MB**. Any GGUF larger than that **doesn't fit** the iGPU as a discrete-VRAM target. Vulkan on an APU may still use unified RAM — that is a **test**, not a Fit PASS.

## Inventory (GGUF that exist; not AMD runs)

File sizes are Hugging Face LFS sizes checked 2026-08-16 via the Hub API. Architecture strings are from the Hub cards.

| Product | Hugging Face ID | Source | Arch | File used for Fit | On-disk | Laptop CPU | Laptop iGPU (512 MB) | 1× MI300X |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nano 4B | `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` | **Official NVIDIA** | `nemotron_h` | `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf` | **2.84 GB** (2.64 GiB) | **1×** | dedicated 512 MB **doesn't fit**; Vulkan UMA **1×** (tested) | **1×** |
| Lightning 30B-A3B | `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` | NVIDIA card points here (ggml-org conversion) | `nemotron_h_moe` | `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf` | **18.90 GB** (17.60 GiB) | **1×** | dedicated 512 MB **doesn't fit**; Vulkan UMA **1×** (tested) | **1×** |
| Lightning 30B-A3B | same repo | same | `nemotron_h_moe` | `…-Q8_0.gguf` | **33.59 GB** | **1×** | **doesn't fit** | **1×** |
| Lightning 30B-A3B | same repo | same | `nemotron_h_moe` | `…-BF16.gguf` | **63.18 GB** | **1× tight** vs 93 GiB RAM + context | **doesn't fit** | **1×** |
| Nano 30B-A3B | `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` | Community. NVIDIA Spark playbook uses this. **Not** an official NVIDIA 30B GGUF org repo | `nemotron_h_moe` | `Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf` | **24.57 GB** (22.88 GiB) | **1×** | dedicated 512 MB **doesn't fit**; Vulkan UMA **1×** (tested) | **1×** |
| Nano Omni 30B | `unsloth/NVIDIA-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-GGUF` | Community | `nemotron_h_moe` | several text GGUFs | ~19–33 GB class | **1×** | **doesn't fit** | **1×** |
| Super 120B-A12B | `unsloth/NVIDIA-Nemotron-3-Super-120B-A12B-GGUF` | Community | hybrid + LatentMoE + MTP | UD-Q4_K_M listed **64.5 GB** | **1× tight** vs 93 GiB | **doesn't fit** | **1×** |
| Ultra | — | No official or community Ultra GGUF identified in this pass | — | — | n/a | n/a | n/a |
| Embed / Parse / ASR / VL / NVFP4 shards | — | **Not** this stack | — | NVFP4 safetensors are **not** GGUF (**R-NVFP4**) | n/a | n/a | n/a |
| Safety Guard 8B | generic Llama GGUF (if any) | Not an official Nemotron GGUF | `llama` | **NOT TESTED** | **1×** | **doesn't fit** iGPU | **1×** |

Do **not** download Super BF16, any Ultra, or NVFP4 in this stack. Do **not** download Lightning **BF16 GGUF** on the laptop (63 GiB weights vs 93 GiB RAM is tight once context exists). Super community GGUF is inventoried for Fit only in this pass.

Lightning Q4_K_M is advertised on some Hub pages; the `ggml-org` tree checked 2026-08-16 actually contains **Q4_0 / Q8_0 / BF16**, not Q4_K_M. Use the files that exist.

## Architecture requirement

Nano **4B** GGUF is dense hybrid Mamba-2 + MLP + 4 attention (`nemotron_h`). Nano **30B** / Lightning GGUF are MoE hybrids (`nemotron_h_moe`). llama.cpp added `nemotron_h_moe` after CPU `nemotron_h`. Pin a **recent** llama.cpp (this repo's scripts default to GitHub release **b10453**, published 2026-08-16). An old AMD `rocm/llama.cpp` Docker tag such as **b6652** is **too old** for `nemotron_h_moe`.

HIP/Vulkan still have to implement those graphs. “Architecture exists in llama.cpp” ≠ it ran on this GPU.

## What we will not claim

- Ollama `ollama run nemotron-…` as a llama.cpp result (different launcher, unpinned binary).
- CUDA / DGX Spark generation as AMD HIP/Vulkan.
- iGPU result as NPU.
- GGUF Q4 as NVFP4 or as Instinct MXFP4.

## How a PASS is earned

Same as [`methodology.md`](methodology.md): timestamped `results/<platform>/<utc>Z/`, `run-metadata.json`, command, llama.cpp version + backend, GGUF repo + revision + filename + sha256, prompts, generations or classified FAIL. First FAIL dirs are never overwritten.

Scripts: [`scripts/llamacpp/README.md`](../scripts/llamacpp/README.md).

## Execution recorded 2026-08-16

| Platform | Backend | File | Result | Evidence |
| --- | --- | --- | --- | --- |
| Strix Point laptop | llama.cpp b10453 **CPU** `-ngl 0` | official Nano 4B Q4_K_M | **Validated** greedy thinking-off 5/5 | `results/ryzen-ai/2026-08-16_214142Z/` |
| Strix Point laptop | llama.cpp b10453 **Vulkan** `Vulkan0` RADV GFX1150 | official Nano 4B Q4_K_M | **Validated** 5/5; 43/43 layers; ~47 GiB UMA (not 512 MB dedicated) | `results/ryzen-ai/2026-08-16_214348Z/` |
| Strix Point laptop | llama.cpp CLI without `--single-turn` | Nano 4B | Harness FAIL (interactive `>` flood). First FAIL kept | `results/ryzen-ai/2026-08-16_214028Z-cpu/` |
| 1× MI300X VF | llama.cpp HIP gfx942 (source b10453, HIP 7.14) | official Nano 4B Q4_K_M | **Validated** greedy thinking-off 5/5; 43/43 layers on ROCm0 | `results/mi300x/2026-08-16_215228Z/` |
| Strix Point laptop | llama.cpp b10453 **CPU** `-ngl 0` | Lightning ggml-org Q4_0 | **Validated** 5/5 | `results/ryzen-ai/2026-08-16_223932Z/` |
| Strix Point laptop | llama.cpp b10453 **Vulkan** `Vulkan0` | Lightning ggml-org Q4_0 | **Validated** 5/5; 53/53 layers; model buffer ~17658 MiB | `results/ryzen-ai/2026-08-16_224120Z/` |
| 1× MI300X VF | llama.cpp HIP gfx942 | Lightning ggml-org Q4_0 | **Validated** 5/5; 53/53 layers on ROCm0; model buffer ~17658 MiB | `results/mi300x/2026-08-16_225542Z/` |
| Strix Point laptop | llama.cpp b10453 **CPU** `-ngl 0` | Unsloth Nano 30B Q4_K_M | **Validated** 5/5 (community file) | `results/ryzen-ai/2026-08-16_225528Z/` |
| Strix Point laptop | llama.cpp b10453 **Vulkan** `Vulkan0` | Unsloth Nano 30B Q4_K_M | **Validated** 5/5; 53/53 layers; model buffer ~23197 MiB | `results/ryzen-ai/2026-08-16_225631Z/` |
| 1× MI300X VF | llama.cpp HIP gfx942 | Unsloth Nano 30B Q4_K_M | **Validated** 5/5; 53/53 layers on ROCm0; model buffer ~23197 MiB (community file) | `results/mi300x/2026-08-16_231304Z/` |

NPU remains **R-NPU**. Discrete Radeon remains **NOT TESTED**.

CPU on the MI300X **host** is not an Instinct GPU result.
