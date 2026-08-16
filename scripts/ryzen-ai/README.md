# Ryzen AI scripts

These scripts are **read-only discovery tools** for the local Strix Point laptop.

They do **not**:

- install packages
- modify system Python
- download Nemotron weights
- claim NPU execution

## What to run first

From the repository root:

```bash
bash scripts/ryzen-ai/collect-env.sh
bash scripts/ryzen-ai/check-rocm.sh
```

Outputs land under:

```text
results/ryzen-ai/<timestamp>Z/environment/
```

Previous runs are never overwritten.

## Three distinct compute targets

| Target | What it is | How we would prove Nemotron runs on it |
| --- | --- | --- |
| CPU | Zen 5 cores on the Strix Point APU | llama.cpp / Transformers CPU generate |
| Radeon iGPU | Integrated RDNA GPU, typically gfx1150 on Strix Point | ROCm/HIP, Vulkan, or llama.cpp GPU offload with GPU-identifying logs |
| XDNA NPU | Ryzen AI NPU, separate from the iGPU | A dedicated NPU runtime (not ROCm GPU) plus evidence that Nemotron executed there |

If a model runs through ROCm on the integrated Radeon GPU, that is **iGPU evidence only**. It is **not** an NPU result.

## What we will not do yet

Do not download Nano 30B BF16 on this laptop until memory headroom is documented. Candidate local workloads, if later approved:

- Nemotron 3 Embed 1B
- Nemotron safety-guard class models (~8B)
- Nemotron 3 Nano 4B quantized / GGUF
- Community GGUF of Nano 30B only after RAM/VRAM estimates pass
