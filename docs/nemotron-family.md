# Nemotron family catalog

**Checked:** 2026-08-16. NVIDIA org census: **183** Hugging Face repos whose id contains `nemotron`. This file’s **table is the tracked set**: latest product per NVIDIA line on [developer.nvidia.com/nemotron](https://developer.nvidia.com/nemotron).

This is inventory, not an AMD PASS list. Nano 30B BF16 remains the only **vLLM** result. A result on Embed, Parse, Guard, or ASR is not a Nano LM result. Queue: [`mi300x-next-tests.md`](mi300x-next-tests.md).

**Latest product ≠ floating `main`.** Inventory uses the current repo ID. AMD runs still pin a commit.

Fit: OAM Instinct **1× / 2× / 4× / 8×** (never “doesn't fit”). MI350P / Radeon / this Ryzen AI laptop: one device; otherwise **doesn't fit**. Precision siblings (BF16 / FP8 / NVFP4 / Base) of a tracked product stay. Lightning 3.5 does not replace Nano 30B.

Not in this table (census appendix only): superseded versions (Parse v1.1/v1.2, OCR v1, Content Safety 3, Cascade 8B, GenRM pre-2603), Nemotron Labs research SKUs, training auxiliaries, and prior generations (Nano v2, Nemotron-H, Llama Nemotron, Nemotron 4, 2023 `nemotron-3-8b-*`, distilled OpenMath/OpenCode/AceReason).

---

## Tracked products (12)

All IDs are under `nvidia/` unless noted. Transformers-on-MI300X status below is **not** a vLLM result.

| Product | Size | Latest checkpoints | AMD (1× MI300X VF Transformers unless noted) | Fit MI300X | Fit MI350P | Fit Ryzen AI laptop |
| --- | --- | --- | --- | --- | --- | --- |
| Nano 30B-A3B | 30B / 3.5B MoE | `NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`, `-FP8`, `-NVFP4`, `-Base-BF16` | BF16 **Validated** + vLLM **Runs**. FP8 **FAIL** `mamba-ssm`. NVFP4 **NOT TESTED**. Community Unsloth Q4_K_M GGUF llama.cpp **Validated** CPU/Vulkan/HIP (`225528Z`, `225631Z`, `231304Z`) — not official NVIDIA 30B GGUF | **1×** | **1×** | BF16 **doesn't fit**; Unsloth Q4_K_M CPU + Vulkan UMA **1×**; dedicated iGPU **doesn't fit** |
| Nano 4B | ~4B dense hybrid | `NVIDIA-Nemotron-3-Nano-4B-BF16`, `-FP8`, `-GGUF` | BF16 **Validated** greedy (`054423Z`) + vLLM **Runs** (`170637Z`). FP8 **Runs** looping `A` (`170427Z`, **R-FNUZ**, not Validated). GGUF Q4_K_M **Validated** laptop CPU (`214142Z`), iGPU Vulkan (`214348Z`), and 1× MI300X HIP (`215228Z`) | **1×** | **1×** | CPU **1×**; Vulkan UMA **1×** |
| Super 120B-A12B | 120B / 12B | `NVIDIA-Nemotron-3-Super-120B-A12B-BF16`, `-FP8`, `-NVFP4`, `-Base-BF16`; `Nemotron-3-Super-120B-A12B-BF16-MTPv2` | **NOT TESTED**. Do not download BF16 on 1× VF | BF16 **2×**; FP8 **1×** | BF16 **doesn't fit**; FP8 **1× tight** | **doesn't fit** |
| Ultra 550B-A55B | 550B / 55B | `NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16`, `-NVFP4`, `-Base-BF16`, `-GenRM` | **NOT TESTED**. Do not download | BF16 **8×**; NVFP4 **2×** | **doesn't fit** | **doesn't fit** |
| Nano Omni 30B-A3B | 31B / ~3B + A/V | `Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`, `-FP8`, `-NVFP4` | **NOT TESTED** | **1×** | **1×** | BF16 **doesn't fit** |
| 3.5 Lightning 30B-A3B | 30B / 3B | `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`, `-NVFP4`, `-Base-BF16`, `-NVFP4-DFlash`, `-NVFP4-DSpark`; GGUF at `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` | BF16 **Validated** greedy (`062756Z`) + vLLM **Runs** (`170852Z`). No FlashInfer. No official FP8. GGUF Q4_0 **Validated** llama.cpp CPU/Vulkan/HIP | **1×** | **1×** | BF16 **doesn't fit**; GGUF Q4_0 CPU + Vulkan UMA **1×**; dedicated iGPU **doesn't fit** |
| Embed | 1B / 8B encoder | `Nemotron-3-Embed-1B-BF16`, `-NVFP4`; `Nemotron-3-Embed-8B-BF16` | BF16 **Runs** (cosine smoke). NVFP4 **NT** | **1×** | **1×** | CPU **1×** |
| Retriever (rerank / VL) | ~1B–8B | `llama-nemotron-rerank-1b-v2`; `llama-nemotron-embed-vl-1b-v2`; `llama-nemotron-rerank-vl-1b-v2`; ColEmbed VL 3B/4B/8B v2; `omni-embed-nemotron-3b` | Text rerank **Runs**. VL rerank **Runs** text-only. ColEmbed 3B/4B/8B + omni-embed **Runs** dummy image. VL embed 1B BF16 load **Runs** empty tensor. VL embed/rerank **FP8 FAIL** (`170519Z`, `170557Z`) | **1×** | **1×** | CPU **1×** |
| Parse 2.0 | <1B VLM | `NVIDIA-Nemotron-Parse-2.0` | **Runs** dummy PNG (`063558Z`). Not OCR eval | **1×** | **1×** | **1×** if kernels exist |
| ASR Streaming 3.5 | 0.6B | `nemotron-3.5-asr-streaming-0.6b` | **Runs** Transformers pipeline (empty tone). Not NeMo CUDA. | **1×** | **1×** | **1×** if weights load; NPU **n/a** |
| Content Safety 3.5 | 4B Gemma-3 | `Nemotron-3.5-Content-Safety` | **Runs** label shape | **1×** | **1×** | CPU **1×** |
| Safety Guard 8B v3 | 8B Llama 3.1 | `Llama-3.1-Nemotron-Safety-Guard-8B-v3` | **Runs** generate; Guard schema not applied | **1×** | **1×** | CPU **1×** |

NVFP4 on Instinct is a format caveat (**R-NVFP4**), not a Fit miss. Nano community GGUF (`unsloth/Nemotron-3-Nano-30B-A3B-GGUF`) is not an official NVIDIA 30B GGUF.

## What this repo has actually run

| Checkpoint | Platform | Result |
| --- | --- | --- |
| `NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` rev `2d59de1…` | 1× MI300X VF | Transformers greedy thinking-off **Validated**; vLLM serve / 128K ladder **Runs**. Not Optimized. |
| `NVIDIA-Nemotron-3-Nano-4B-GGUF` Q4_K_M rev `ba223d14…` | Strix Point CPU + iGPU Vulkan; 1× MI300X HIP | llama.cpp greedy thinking-off **Validated** (`214142Z`, `214348Z`, `215228Z`). Not NPU. |
| `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` Q4_0 rev `9d425fe1…` | Strix Point CPU + iGPU Vulkan; 1× MI300X HIP | llama.cpp greedy thinking-off **Validated** (`223932Z`, `224120Z`, `225542Z`). Not official NVIDIA GGUF org. Not NPU. |
| `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` Q4_K_M rev `9ad8b366…` | Strix Point CPU + iGPU Vulkan; 1× MI300X HIP | llama.cpp greedy thinking-off **Validated** (`225528Z`, `225631Z`, `231304Z`). Community conversion. Not official NVIDIA 30B GGUF. Not NPU. |
| `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` rev `d468880b…` | 1× MI300X VF | Transformers greedy **Validated** (`062756Z`). vLLM **Runs** (`170852Z`). Not Nano. |
| `NVIDIA-Nemotron-3-Nano-4B-FP8` rev `3fe6dab7…` | 1× MI300X VF | **Runs** tokens; output looping `A`. **R-FNUZ**. Not Validated (`170427Z`). |
| `NVIDIA-Nemotron-Parse-2.0` rev `635b84d9…` | 1× MI300X VF | **Runs** dummy PNG. |
| `Nemotron-3-Embed-1B-BF16` / `-8B-BF16` | 1× MI300X VF | Transformers **Runs** cosine smoke. |
| `llama-nemotron-rerank-1b-v2` | 1× MI300X VF | **Runs**. |
| ColEmbed VL 3B/4B/8B v2; `omni-embed-nemotron-3b`; VL rerank **text** | 1× MI300X VF | **Runs** (dummy image or text pair). |
| `nemotron-3.5-asr-streaming-0.6b` | 1× MI300X VF | **Runs** empty synthetic transcript. |
| `Nemotron-3.5-Content-Safety`; Guard 8B v3 | 1× MI300X VF | **Runs** generate/shape. Not a safety eval. |

SKU grid for that subset: [`compatibility-matrix.md`](compatibility-matrix.md). Card notes: [`model-inventory.md`](model-inventory.md).

---

## Appendix: all 183 NVIDIA org IDs containing “nemotron” (2026-08-16)

```
AceMath-RL-Nemotron-7B
AceReason-Nemotron-1.1-7B
AceReason-Nemotron-14B
AceReason-Nemotron-7B
DLER-Llama-Nemotron-8B-Merge-Research
Llama-3.1-Nemotron-70B-Instruct
Llama-3.1-Nemotron-70B-Instruct-HF
Llama-3.1-Nemotron-70B-Reward
Llama-3.1-Nemotron-70B-Reward-HF
Llama-3.1-Nemotron-8B-UltraLong-1M-Instruct
Llama-3.1-Nemotron-8B-UltraLong-2M-Instruct
Llama-3.1-Nemotron-8B-UltraLong-4M-Instruct
Llama-3.1-Nemotron-Nano-4B-v1.1
Llama-3.1-Nemotron-Nano-8B-v1
Llama-3.1-Nemotron-Nano-VL-8B-V1
Llama-3.1-Nemotron-Nano-VL-8B-V1-FP4-QAD
Llama-3.1-Nemotron-Nano-VL-8B-V1-mcore
Llama-3.1-Nemotron-Safety-Guard-8B-v3
Llama-3.3-Nemotron-70B-Edit
Llama-3.3-Nemotron-70B-Feedback
Llama-3.3-Nemotron-70B-Reward
Llama-3.3-Nemotron-70B-Reward-Multilingual
Llama-3.3-Nemotron-70B-Reward-Principle
Llama-3.3-Nemotron-70B-Select
Llama-3_1-Nemotron-51B-Instruct
Llama-3_1-Nemotron-Ultra-253B-CPT-v1
Llama-3_1-Nemotron-Ultra-253B-v1
Llama-3_1-Nemotron-Ultra-253B-v1-FP8
Llama-3_3-Nemotron-Super-49B-GenRM
Llama-3_3-Nemotron-Super-49B-GenRM-Multilingual
Llama-3_3-Nemotron-Super-49B-v1
Llama-3_3-Nemotron-Super-49B-v1-FP8
Llama-3_3-Nemotron-Super-49B-v1_5
Llama-3_3-Nemotron-Super-49B-v1_5-FP8
Llama-3_3-Nemotron-Super-49B-v1_5-NVFP4
llama-embed-nemotron-8b
llama-nemotron-colembed-vl-3b-v2
llama-nemotron-embed-1b-v2
llama-nemotron-embed-vl-1b-v2
llama-nemotron-embed-vl-1b-v2-fp8
llama-nemotron-rerank-1b-v2
llama-nemotron-rerank-vl-1b-v2
llama-nemotron-rerank-vl-1b-v2-fp8
nemocurator-fineweb-nemotron-4-edu-classifier
nemotron-3-8b-base-4k
nemotron-3-8b-chat-4k-rlhf
nemotron-3-8b-chat-4k-sft
nemotron-3-8b-chat-4k-steerlm
nemotron-3-8b-qa-4k
Nemotron-3-Content-Safety
Nemotron-3-Embed-1B-BF16
Nemotron-3-Embed-1B-NVFP4
Nemotron-3-Embed-8B-BF16
Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16
Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8
Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4
Nemotron-3-Super-120B-A12B-BF16-MTPv2
nemotron-3.5-asr-streaming-0.6b
Nemotron-3.5-Content-Safety
Nemotron-4-340B-Base
Nemotron-4-340B-Instruct
Nemotron-4-340B-Reward
Nemotron-4-Mini-Hindi-4B-Base
Nemotron-4-Mini-Hindi-4B-Instruct
Nemotron-Cascade-14B-Thinking
Nemotron-Cascade-2-30B-A3B
Nemotron-Cascade-8B
Nemotron-Cascade-8B-Intermediate-ckpts
Nemotron-Cascade-8B-Thinking
nemotron-climb-fasttext-classifiers
nemotron-climb-proxy-models
nemotron-colembed-vl-4b-v2
nemotron-colembed-vl-8b-v2
Nemotron-Content-Safety-Reasoning-4B
Nemotron-Elastic-12B
Nemotron-Flash-1B
Nemotron-Flash-3B
Nemotron-Flash-3B-Instruct
nemotron-graphic-elements-v1
Nemotron-H-47B-Base-8K
Nemotron-H-47B-Reasoning-128K
Nemotron-H-47B-Reasoning-128K-FP8
Nemotron-H-4B-Base-8K
Nemotron-H-4B-Instruct-128K
Nemotron-H-56B-Base-8K
Nemotron-H-8B-Base-8K
Nemotron-H-8B-Reasoning-128K
Nemotron-H-8B-Reasoning-128K-FP8
Nemotron-Labs-Audex-2B
Nemotron-Labs-Audex-30B-A3B
nemotron-labs-audio-visual-flamingo-hf
Nemotron-Labs-Diffusion-14B
Nemotron-Labs-Diffusion-14B-Base
Nemotron-Labs-Diffusion-3B
Nemotron-Labs-Diffusion-3B-Base
Nemotron-Labs-Diffusion-8B
Nemotron-Labs-Diffusion-8B-Base
Nemotron-Labs-Diffusion-VLM-8B
Nemotron-Labs-TwoTower-30B-A3B-Base-BF16
Nemotron-Mini-4B-Instruct
Nemotron-Mini-4B-Instruct-ONNX-INT4
nemotron-ocr-v1
nemotron-ocr-v2
Nemotron-Orchestrator-8B
nemotron-page-elements-v3
Nemotron-Research-GooseReason-4B-Instruct
Nemotron-Research-Reasoning-Qwen-1.5B
nemotron-speech-streaming-en-0.6b
nemotron-table-structure-v1
Nemotron-Terminal-14B
Nemotron-Terminal-32B
Nemotron-Terminal-8B
NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16
NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
NVIDIA-Nemotron-3-Nano-30B-A3B-FP8
NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4
NVIDIA-Nemotron-3-Nano-4B-BF16
NVIDIA-Nemotron-3-Nano-4B-FP8
NVIDIA-Nemotron-3-Nano-4B-GGUF
NVIDIA-Nemotron-3-Super-120B-A12B-Base-BF16
NVIDIA-Nemotron-3-Super-120B-A12B-BF16
NVIDIA-Nemotron-3-Super-120B-A12B-FP8
NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4
NVIDIA-Nemotron-3-Ultra-550B-A55B-Base-BF16
NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16
NVIDIA-Nemotron-3-Ultra-550B-A55B-GenRM
NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4
NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Base-BF16
NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16
NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4
NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash
NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark
NVIDIA-Nemotron-Labs-3-Elastic-30B-A3B-BF16
NVIDIA-Nemotron-Labs-3-Elastic-30B-A3B-FP8
NVIDIA-Nemotron-Labs-3-Elastic-30B-A3B-NVFP4
NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-BF16
NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-FP8
NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
NVIDIA-Nemotron-Labs-Teacher-Chat
NVIDIA-Nemotron-Labs-Teacher-Competition-Coding
NVIDIA-Nemotron-Labs-Teacher-General-Reasoning
NVIDIA-Nemotron-Labs-Teacher-Instruction-Following
NVIDIA-Nemotron-Labs-Teacher-STEM
NVIDIA-Nemotron-Nano-12B-v2
NVIDIA-Nemotron-Nano-12B-v2-Base
NVIDIA-Nemotron-Nano-12B-v2-VL-BF16
NVIDIA-Nemotron-Nano-12B-v2-VL-FP8
NVIDIA-Nemotron-Nano-12B-v2-VL-NVFP4-QAD
NVIDIA-Nemotron-Nano-9B-v2
NVIDIA-Nemotron-Nano-9B-v2-Base
NVIDIA-Nemotron-Nano-9B-v2-FP8
NVIDIA-Nemotron-Nano-9B-v2-Japanese
NVIDIA-Nemotron-Nano-9B-v2-NVFP4
NVIDIA-Nemotron-Parse-2.0
NVIDIA-Nemotron-Parse-v1.1
NVIDIA-Nemotron-Parse-v1.1-TC
NVIDIA-Nemotron-Parse-v1.2
NVIDIA-NemotronLabs-VoiceChat-11B
omni-embed-nemotron-3b
OpenCodeReasoning-Nemotron-1.1-14B
OpenCodeReasoning-Nemotron-1.1-32B
OpenCodeReasoning-Nemotron-1.1-7B
OpenCodeReasoning-Nemotron-14B
OpenCodeReasoning-Nemotron-32B
OpenCodeReasoning-Nemotron-32B-IOI
OpenCodeReasoning-Nemotron-7B
OpenMath-Nemotron-1.5B
OpenMath-Nemotron-14B
OpenMath-Nemotron-14B-Kaggle
OpenMath-Nemotron-32B
OpenMath-Nemotron-7B
OpenReasoning-Nemotron-1.5B
OpenReasoning-Nemotron-14B
OpenReasoning-Nemotron-32B
OpenReasoning-Nemotron-7B
Qwen-2.5-Nemotron-32B-Reward
Qwen-3-Nemotron-32B-Reward
Qwen3-Nemotron-14B-BRRM
Qwen3-Nemotron-235B-A22B-GenRM
Qwen3-Nemotron-235B-A22B-GenRM-2603
Qwen3-Nemotron-32B-GenRM-Principle
Qwen3-Nemotron-32B-RLBFF
Qwen3-Nemotron-8B-BRRM
```

Prefix each line with `nvidia/`. Community Unsloth GGUF is **not** in this org list.
