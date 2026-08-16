# Review: Lightning 30B-A3B ggml-org GGUF on Strix Point iGPU (llama.cpp Vulkan)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `vulkan-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf`, revision `9d425fe18d84ab04da6aabb757d2e2807083d054`, sha256 `61f87e75974e4b535dcdf9aad056541a9514f1dfa4538b463b081d19b7a00e3c`, llama.cpp **b10453** Ubuntu **Vulkan** binary, **iGPU** `Vulkan0` = `AMD Radeon Graphics (RADV GFX1150)`, **53/53 layers offloaded**, greedy thinking-off smoke on this Strix Point laptop.  
**Not claimed:** NPU/XDNA, discrete Radeon, HIP, MI300X, Optimized, Production-ready, Transformers, vLLM, Lightning BF16/Q8_0, MTP sidecar.

This is **iGPU**, never “Ryzen AI NPU.” Dedicated `amd-smi` VRAM is still **512 MB** (**R-IGPU** vs that number). Vulkan reports **~47 GiB** free unified memory (`48427 MiB`). Fit for this 17.60 GiB Q4_0 is **1× against UMA**, not against 512 MB dedicated.

Same-day CPU Validated run of this file: `results/ryzen-ai/2026-08-16_223932Z/`.

## Stack

- `--n-gpu-layers 99 -dev Vulkan0`
- Verbose probe: `using device Vulkan0 (AMD Radeon Graphics (RADV GFX1150))`, `offloaded 53/53 layers to GPU`, Vulkan0 model buffer **17658.09 MiB**
- Architecture: `nemotron_h_moe`

## Prompt-by-prompt

Same five greedy thinking-off prompts as the CPU Validated Lightning run; answers are the same class (RAM vs storage, 1536 GB, factorial, two-sentence MI300X summary, exact JSON).

## Material caveats

- Mesa RADV, not ROCm HIP. Laptop ROCm remains **6.4.3**.
- NPU is still **R-NPU**.
- Do not copy this onto Unsloth 30B until that file is run.
