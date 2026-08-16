# Project scope

## Question

Which NVIDIA Nemotron models can run on AMD Instinct, Radeon, and Ryzen AI hardware, through which software stack, with what precision, memory requirements, performance characteristics, and caveats?

## What we will claim

Only statements that can be attached to:

- a named checkpoint ID and revision
- a named AMD device
- a named software stack and versions
- a `results/<platform>/<timestamp>/` directory

## First execution target

```text
nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
BF16
1× AMD Instinct MI300X (192 GB HBM)
Transformers on ROCm PyTorch, then vLLM if Transformers succeeds
```

Success for that target means load, generate, inspect output, serve, reproduce. It does **not** mean 1M context, NVFP4, or production serving.

## In scope

- Inventory of the NVIDIA Nemotron brand ([`nemotron-family.md`](nemotron-family.md)), with phase-1 card detail on Nano / Super / Ultra / Omni / Embed / safety / Lightning ([`model-inventory.md`](model-inventory.md)). Next execution queue: [`mi300x-next-tests.md`](mi300x-next-tests.md)
- Instinct MI300X hands-on validation
- Theoretical Instinct MI325X / MI350X / MI355X / MI350P assessment (fit vs HBM; no PASS without a run)
- Radeon ROCm support research
- Strix Point CPU / iGPU / NPU discovery
- Precision portability analysis, especially NVFP4 vs BF16 vs FP8
- Conservative Super and Ultra feasibility math before any large download

## Out of scope for this phase

- Downloading Super **BF16** or any Ultra checkpoint
- Super **FP8** is queued as a 1× FNUZ research load only ([`mi300x-next-tests.md`](mi300x-next-tests.md) C3); it is not a promised PASS
- Attempting 1M context
- Changing system ROCm, kernel, or OS on either machine
- Treating NVIDIA CUDA/NIM/TensorRT-LLM recipes as AMD recipes (no `--mamba-backend flashinfer`)
- Claiming XDNA NPU support without a Nemotron NPU execution path
- Marketing copy for AMD or NVIDIA
- NVFP4 as an AMD-native test in the current queue

## Hardware we actually have

| Machine | What we know | Execution role |
| --- | --- | --- |
| Remote Instinct server | 1× MI300X, 192 GB HBM (operator-stated). OS/ROCm/PyTorch **unknown until `collect-env.sh` runs there.** | Primary validation |
| Local laptop | AMD Ryzen AI 9 HX 370, Radeon 890M gfx1150, XDNA NPU present, 93 GiB RAM, Ubuntu 24.04.3, ROCm 6.4.3. Evidence: `results/ryzen-ai/2026-08-15_171202Z/` (repeat of `2026-08-15_162031Z`) | Discovery now; small-model experiments later |

SSH hostnames, usernames, and tokens are **not** stored in this repository. Use `<MI300X_HOST>`, `<MI300X_USER>`, `<HF_TOKEN>`.
