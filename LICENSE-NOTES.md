# License notes

This engineering repository records how to test Nemotron on AMD hardware. It does **not** relicense NVIDIA model weights, AMD software, or third-party runtimes.

## This repository

Source files in this repo (scripts, documentation, prompts) are project work product for technical validation. They contain no model weights.

## NVIDIA model weights (not shipped here)

Checked **2026-08-15** against Hugging Face cards. Always re-read the live card before download or redistribution.

| Model class | Example HF ID | Governing license named on the card |
| --- | --- | --- |
| Nemotron 3 Nano 30B / 4B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | NVIDIA Nemotron Open Model License |
| Nemotron 3 Super | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | NVIDIA Nemotron Open Model License |
| Nemotron 3 Ultra | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | OpenMDW License Agreement v1.1 |
| Nemotron 3 Nano Omni | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | NVIDIA Open Model Agreement |
| Nemotron 3.5 Lightning | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | OpenMDW License Agreement v1.1 |
| Nemotron 3 Embed | `nvidia/Nemotron-3-Embed-1B-BF16` | OpenMDW 1.1 (card also notes Apache-2.0 parent) |
| Content Safety Reasoning 4B | `nvidia/Nemotron-Content-Safety-Reasoning-4B` | Read the live card before use |
| Llama 3.1 Nemotron Safety Guard 8B v3 | `nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3` | Read the live card before use |

NIM containers, TensorRT-LLM, and `nvcr.io` images are additionally covered by NVIDIA software / AI product terms. Those are **NVIDIA-specific runtimes**, not AMD validation paths.

## AMD software

ROCm, HIP, `rocm-smi`, `amd-smi`, and related tools are AMD-licensed. This repo does not redistribute them.

## Secrets

Never commit `HF_TOKEN`, SSH keys, passwords, or private hostnames. Placeholders: `<HF_TOKEN>`, `<MI300X_HOST>`, `<MI300X_USER>`.
