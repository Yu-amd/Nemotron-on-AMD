# Nemotron Embed (and related retrieval / safety)

**NOT TESTED** on AMD. Later local / Radeon candidates — not the MI300X phase-1 target.

## Nemotron 3 Embed 1B

| | |
| --- | --- |
| HF ID | `nvidia/Nemotron-3-Embed-1B-BF16` |
| NVFP4 sibling | `nvidia/Nemotron-3-Embed-1B-NVFP4` (NVIDIA-specific until proven) |
| Params | ~1.14B |
| Arch | Bidirectional Transformer encoder (pruned Ministral-3-3B) |
| Dim | 2048 |
| Max seq | 32768 |
| License | OpenMDW 1.1 |
| Transformers | ≥ 5.2.0; NVIDIA examples use FlashAttention-2 (use SDPA if that is CUDA-only) |
| Raw BF16 memory | ~2.3 GB |

Card: https://huggingface.co/nvidia/Nemotron-3-Embed-1B-BF16 (checked 2026-08-15).

## Nemotron 3 Embed 8B

| | |
| --- | --- |
| HF ID | `nvidia/Nemotron-3-Embed-8B-BF16` |
| Params | ~8B |
| Dim | 4096 |
| Raw BF16 memory | ~16 GB |

## Older Nemotron-branded embed

- `nvidia/llama-embed-nemotron-8b`
- `nvidia/llama-nemotron-embed-1b-v2`
- `nvidia/llama-nemotron-embed-vl-1b-v2`

These are **not** the Nemotron 3 hybrid MoE LMs. Track separately if we test them.

## Safety

| | |
| --- | --- |
| HF ID | `nvidia/Nemotron-Content-Safety-Reasoning-4B` |
| Arch | Gemma-3-4B-it classifier |
| Raw BF16 memory | ~8 GB |
| AMD | **NOT TESTED** |

| | |
| --- | --- |
| HF ID | `nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3` |
| Arch | Llama 3.1 8B Instruct + safety LoRA |
| Raw BF16 memory | ~16 GB |
| AMD | **NOT TESTED**; more like a generic Llama-3.1 bring-up than Nano |

Do not cite an Embed or Guard result as evidence that Nemotron 3 Nano Runs.
