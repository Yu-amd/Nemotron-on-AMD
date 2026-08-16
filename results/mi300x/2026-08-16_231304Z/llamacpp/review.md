# Review: Unsloth Nano 30B-A3B GGUF on 1× MI300X VF (llama.cpp HIP)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `hip-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: `unsloth/Nemotron-3-Nano-30B-A3B-GGUF` `Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf`, revision `9ad8b366c308f931b2a96b9306f0b41aef9cd405`, sha256 `0e7f6e51fdd9039928749d07eed9e846dbfd97681646544c5406bcdd788e5940`, llama.cpp source tag **b10453** (`3cb7ffb`) **HIP** build `GPU_TARGETS=gfx942` against existing HIP **7.14**, device **ROCm0** = AMD Instinct MI300X VF, greedy jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Official NVIDIA 30B GGUF, Optimized, Production-ready, vLLM, Transformers, Vulkan, Radeon, laptop.

Environment snapshot for the host remains `results/mi300x/2026-08-15_172057Z/environment/`. File was Hub-downloaded and hashed on the laptop, then rsync'd; host `sha256sum` matched.

## Stack

- `llama-cli --list-devices`: `ROCm0: AMD Instinct MI300X VF (196288 MiB, 195956 MiB free)`
- Verbose probe: `using device ROCm0 (AMD Instinct MI300X VF)`, `offloaded 53/53 layers to GPU`, ROCm0 model buffer **23197.47 MiB**
- Architecture: `nemotron_h_moe`
- Community Unsloth conversion, not `nvidia/` 30B GGUF
- Left the jupyter `rocm` container alone

## Prompt-by-prompt

Same greedy thinking-off set as the laptop Validated Unsloth runs (RAM vs storage, 1536 GB, factorial, two-sentence MI300X summary truncated at 96 tokens, exact JSON).

## Material caveats

- Still an SR-IOV VF.
- HIP binary reports `build 1` (local source build of tag b10453).
- Docker AMD `rocm/llama.cpp` b6652 was **not** used.
