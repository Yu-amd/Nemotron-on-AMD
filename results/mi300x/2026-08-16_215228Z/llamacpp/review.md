# Review: Nano 4B official GGUF on 1× MI300X VF (llama.cpp HIP)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `hip-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf`, revision `ba223d14e45525f7fae81db77ea8cabeb2fc6c25`, sha256 `be5d9a656a51922f24f1f09a759cebb694e1f5d9728bf0ef9f8c972c5a0b5ef2`, llama.cpp source tag **b10453** (`3cb7ffb`) **HIP** build `GPU_TARGETS=gfx942` against existing HIP **7.14**, device **ROCm0** = AMD Instinct MI300X VF, greedy jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, vLLM, Transformers, Vulkan, Radeon, laptop, Nano **30B**.

Host `cmake` was not installed; `cmake` 3.28.3 and `ninja-build` were added from Ubuntu noble. **ROCm/kernel were not upgraded.** `hipconfig -R` (`/opt/rocm-7.0.2/core-7.14`) lacks `hip-lang` CMake; the HIP build used `/opt/rocm-7.0.2` as `HIP_PATH`. First cmake FAIL (missing `cmake`) and missing `hip_fp16.h` (wrong HIP_PATH) were build-system issues before this PASS.

Environment snapshot for the host remains `results/mi300x/2026-08-15_172057Z/environment/`.

## Stack

- `llama-cli --list-devices`: `ROCm0: AMD Instinct MI300X VF (196288 MiB, 195956 MiB free)`
- Verbose probe: `using device ROCm0 (AMD Instinct MI300X VF)`
- Architecture in GGUF: `nemotron_h`
- Left the jupyter `rocm` container alone

## Prompt-by-prompt

Same greedy thinking-off set as the laptop Validated runs (RAM vs storage, 1536 GB, factorial, two-sentence MI300X summary truncated at 96 tokens, exact JSON).

## Material caveats

- Still an SR-IOV VF.
- HIP binary reports `build 1` (local source build of tag b10453), not the GitHub Ubuntu tarball.
- Docker AMD `rocm/llama.cpp` b6652 was **not** used (too old for later MoE GGUF).
- Do not copy this onto Unsloth 30B or Lightning GGUF.
