# Review: Nano 4B official GGUF on Strix Point iGPU (llama.cpp Vulkan)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `vulkan-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: same Q4_K_M GGUF as the CPU run (`ba223d14…`, sha256 `be5d9a656a5…`), llama.cpp **b10453** Ubuntu **Vulkan** binary, **iGPU** `Vulkan0` = `AMD Radeon Graphics (RADV GFX1150)`, **43/43 layers offloaded**, greedy thinking-off smoke on this Strix Point laptop.  
**Not claimed:** NPU/XDNA, discrete Radeon, HIP, MI300X, Optimized, Production-ready, Transformers, vLLM.

This is **iGPU**, never “Ryzen AI NPU.” Dedicated `amd-smi` VRAM is still **512 MB**. Vulkan reports **~47 GiB** free unified memory (`48427 MiB`). Fit for this file is **1×** against that UMA window, not against 512 MB.

Earlier same-day Vulkan-binary smoke without `--device Vulkan0` (`2026-08-16_214213Z`) also generated 5/5 but the CLI TUI did not print backend lines. Do not use that directory as the iGPU proof. This directory pins `Vulkan0` and keeps a verbose offload excerpt.

## Stack

- `--n-gpu-layers 99 -dev Vulkan0`
- Verbose probe: `using device Vulkan0 (AMD Radeon Graphics (RADV GFX1150))`, `offloaded 43/43 layers to GPU`, Vulkan0 model buffer ~2428 MiB
- Decode in that probe ~24 tok/s — **not** a benchmark; similar to CPU on this 4B Q4, so throughput is not the claim

## Prompt-by-prompt

Same five greedy thinking-off prompts as the CPU Validated run; answers are the same class (RAM vs storage, 1536 GB, factorial, two-sentence MI300X summary truncated at 96 tokens, exact JSON).

## Material caveats

- Mesa RADV, not ROCm HIP. Laptop ROCm remains **6.4.3**.
- NPU is still **R-NPU**.
- Do not copy this onto Unsloth 30B or Lightning GGUF until those files are run.
