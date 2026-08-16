# Nemotron 3 Nano Omni

Multimodal sibling of Nano. **NOT TESTED** on AMD. Not the first MI300X target.

| Precision | HF ID | Listed size (card) |
| --- | --- | --- |
| BF16 | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | 62 GB |
| FP8 | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8` | 33 GB |
| NVFP4 | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4` | 21 GB |

Card (NVFP4 page lists all three): https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4 (checked 2026-08-15).

| | |
| --- | --- |
| Parameters | 31B total / ~3B active (card) — **do not mix with text Nano 30B/3.5B** |
| Modalities in | video, audio, image, text |
| Modality out | text |
| Context listed | 256k |
| Reasoning | `enable_thinking` |
| vLLM extras | video pruning / media kwargs; `nano_v3` + `qwen3_coder` |

## AMD notes

- BF16 62 GB **fits** 192 GB HBM on paper. Multimodal preprocessing and custom kernels are extra failure layers.
- NVFP4 remains NVIDIA-specific until proven.
- License on the BF16 README (2026-08-15): **NVIDIA Open Model Agreement** (not the Nano text Nemotron Open Model License). Re-read at download time.

Do not start Omni until text Nano BF16 Transformers on MI300X has a recorded result.
