# Review: Unsloth Nano 30B-A3B GGUF on Strix Point iGPU (llama.cpp Vulkan)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `vulkan-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` `Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf`, revision `9ad8b366c308f931b2a96b9306f0b41aef9cd405`, sha256 `0e7f6e51fdd9039928749d07eed9e846dbfd97681646544c5406bcdd788e5940`, llama.cpp **b10453** Ubuntu **Vulkan** binary, **iGPU** `Vulkan0` = `AMD Radeon Graphics (RADV GFX1150)`, **53/53 layers offloaded**, greedy thinking-off smoke on this Strix Point laptop.  
**Not claimed:** Official NVIDIA 30B GGUF, NPU/XDNA, discrete Radeon, HIP, MI300X, Optimized, Production-ready, Transformers, vLLM.

This is **iGPU**, never “Ryzen AI NPU.” Dedicated `amd-smi` VRAM is still **512 MB** (**R-IGPU** vs that number). Vulkan reports **~47 GiB** free unified memory (`48427 MiB`). Fit for this 22.88 GiB Q4_K_M is **1× against UMA**, not against 512 MB dedicated. Vulkan0 model buffer **23197.42 MiB**.

Same-day CPU Validated run: `results/ryzen-ai/2026-08-16_225528Z/`.

## Stack

- `--n-gpu-layers 99 -dev Vulkan0`
- Community Unsloth conversion, `nemotron_h_moe`
- Mesa RADV, not ROCm HIP. Laptop ROCm remains **6.4.3**. NPU is still **R-NPU**.

## Prompt-by-prompt

Same five greedy thinking-off prompts as the CPU Validated Unsloth run.
