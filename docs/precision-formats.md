# Precision formats

Checked **2026-08-15**. This document separates **open model weights** from **NVIDIA-specific optimized checkpoints/runtimes**.

Raw storage math: `scripts/common/estimate_weight_memory.py`. Bytes/param below are *payload only*.

## Summary

| Format | Bytes/param (payload) | Portable in principle to AMD? | Status on this project |
| --- | --- | --- | --- |
| BF16 | 2 | Yes, if PyTorch/ROCm and kernels exist | Nano 30B Transformers greedy smoke on 1× MI300X VF: **PASS WITH CAVEATS** / **Runs**. FP8/NVFP4 still **NOT TESTED**. |
| FP16 | 2 | Usually yes where BF16 is yes | Not the NVIDIA-preferred Nano checkpoint |
| FP8 | 1 | **Not automatically.** MI300 series uses **FP8 FNUZ**; MI350 series uses **OCP FP8**. NVIDIA checkpoints are typically OCP E4M3/E5M2. | **NOT TESTED**. High risk of silent mismatch or load failure. |
| NVFP4 | 0.5 + extra scales | **Do not assume portable.** NVIDIA 4-bit float + ModelOpt / FlashInfer / TRT-LLM. | Treat as NVIDIA-specific until an AMD kernel path is demonstrated. |
| INT8 | 1 | Possible via generic quantizers; Nemotron official INT8 checkpoint **not confirmed** | **NOT TESTED** |
| INT4 | 0.5 | Possible via GGUF/AWQ/GPTQ if the **architecture** is supported | **NOT TESTED** |
| GGUF variants | depends (Q8/Q6/Q5/Q4, …) | llama.cpp HIP or Vulkan, if the architecture is implemented | Community Nano GGUF exists; **AMD not tested** |

## BF16

NVIDIA ships first-class BF16 checkpoints for Nano, Super, Ultra, Omni, and Embed.

On AMD Instinct, BF16 is a native CDNA datatype. That makes BF16 the **least wrong** first precision for MI300X.

BF16 still requires:

- a HIP-enabled PyTorch that sees the GPU
- Mamba-2, MoE (and for Super/Ultra, LatentMoE + MTP) kernels in Transformers/vLLM
- enough HBM for weights **plus** KV, SSM state, and framework overhead

**Open weights:** Nano/Super/Ultra BF16 repos. **Not NVIDIA-only runtime:** they can be consumed by Transformers. **Still NVIDIA-tuned:** official software integration lists NVIDIA GPUs only.

## FP16

Same storage cost as BF16. NVIDIA Nano serving docs emphasize BF16, not FP16. Do not cast BF16 weights to FP16 as a “portability trick” without measuring numerics.

## FP8

NVIDIA provides official FP8 Nemotron checkpoints.

AMD Instinct notes (ROCm inference optimization, checked 2026-08-15):

- **MI300X / MI325X (CDNA3):** FP8 **FNUZ**
- **MI350X / MI355X (CDNA4):** **OCP** FP8, plus MXFP8/6/4

A Hugging Face FP8 Nemotron checkpoint that loads on H100/B200 does **not** imply MI300X can run it.

Until we run it, classify MI300X FP8 Nemotron as **THEORETICALLY FEASIBLE** at best (memory), **Unknown / requires validation** for kernels.

## NVFP4

NVFP4 is the most important non-portable format in this family.

Facts from NVIDIA cards (2026-08-15):

- Super and Ultra were **pretrained with an NVFP4 recipe**.
- Official NVFP4 **inference** checkpoints exist for Nano, Super, Ultra, Omni.
- NVIDIA vLLM NVFP4 snippets use CUDA-centric flags (`VLLM_USE_FLASHINFER_MOE_FP4`, `quantization modelopt_fp4`).
- NVIDIA positions NVFP4 as Blackwell-efficient; some secondary write-ups say NVFP4 kernel acceleration is Blackwell-specific. Treat that as **NVIDIA guidance**, not an AMD measurement.

**Do not:**

- rename NVFP4 as “INT4” or “FP4 on AMD”
- assume bitsandbytes/GGUF can read NVFP4 shards
- treat an NVFP4 disk size as an AMD memory requirement for a runnable model

**Do:**

- keep BF16 (and maybe FP8 later) as the AMD open-weight path
- record NVFP4 as **NVIDIA-specific optimized checkpoint/runtime** unless/until ROCm vLLM or another AMD stack documents Nemotron NVFP4

Payload math (0.5 bytes/param) undercounts scales/metadata; Omni’s card lists NVFP4 at 21 GB vs ~14 GB naive 30B×0.5.

## INT8 / INT4

No official NVIDIA Nemotron 3 Nano **INT8/INT4 Hugging Face** checkpoint was confirmed in this pass (FP8 and NVFP4 are the published quantized official formats).

INT8/INT4 on AMD would likely come from:

- Bitsandbytes / AutoGPTQ / AWQ — **Unknown** for hybrid Mamba-MoE on ROCm
- llama.cpp GGUF — community Nano GGUF exists; architecture support in a HIP build is untested
- PyTorch `ao` / AMD Quark — **Unknown / requires validation** for this family

## GGUF

Observed:

- **Official** NVIDIA GGUF: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` file `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf` (2.84 GB, revision `ba223d14…`). **Validated** on this Strix Point laptop: CPU (`214142Z`) and Vulkan iGPU RADV GFX1150 UMA (`214348Z`). **Validated** on 1× MI300X VF HIP gfx942 (`215228Z`).
- NVIDIA Spark llama.cpp playbook downloads community `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` for the **30B** class. That is not an official NVIDIA 30B GGUF repo. Hub Q4_K_M size is **24.57 GB** (22.88 GiB), not the old 14 GiB calculator. **NOT TESTED** on AMD.
- Lightning: NVIDIA card (checked 2026-08-16) points at `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF`. Tree has Q4_0 **18.90 GB**, Q8_0 **33.59 GB**, BF16 **63.18 GB**. Q4_0 llama.cpp **Validated** on laptop CPU/Vulkan UMA and 1× MI300X HIP. Q8_0 / BF16 GGUF **NOT TESTED.**
- Dedicated iGPU VRAM on this laptop is **512 MB**. Vulkan still reported **~47 GiB** UMA. Fit vs 512 MB ≠ Fit vs Vulkan UMA.

| Quant (payload estimate on 30B) | Raw GiB | Local 93 GiB RAM? |
| --- | --- | --- |
| Unsloth Q8_0 (measured) | 31.2 (33.51 GB) | Theoretically possible; **NOT TESTED** |
| Unsloth Q4_K_M (measured) | 22.88 (24.57 GB) | llama.cpp **Validated** on laptop CPU/Vulkan UMA and 1× MI300X HIP (`225528Z`, `225631Z`, `231304Z`). Community file |
| Calculator-only Q4 | 14.0 | Do not use this number for Unsloth Nano 30B — Hub file is larger |
| BF16 GGUF | 55.9 | Tight vs 93 GiB once context + runtime exist; do not download yet |

MoE GGUF files often differ from naive params×bytes because unused experts are still stored. Use actual file size after a directory listing, not this table, for disk planning.

## Open weights vs NVIDIA-optimized runtime

```text
Open weights (example):
  nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
  → Transformers / (hopefully) ROCm vLLM / (maybe) llama.cpp GGUF conversion

NVIDIA-specific optimized path (examples):
  NVFP4 checkpoints + FlashInfer/ModelOpt
  TensorRT-LLM nano_v3 backend
  NIM containers on nvcr.io
  CUDA vLLM wheels
```

Portability work in this repo starts at the **open BF16 weights**, not at NIM or NVFP4.
