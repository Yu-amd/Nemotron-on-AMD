# Review: Lightning 30B-A3B ggml-org GGUF on 1× MI300X VF (llama.cpp HIP)

**Date:** 2026-08-16  
**Artifact:** `llamacpp/result.json` (`result=PASS`, 5/5) plus `list-devices.txt` and `hip-offload-excerpt.log`  
**Claim allowed after this review:** **Validated** for this exact pair: `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf`, revision `9d425fe18d84ab04da6aabb757d2e2807083d054`, sha256 `61f87e75974e4b535dcdf9aad056541a9514f1dfa4538b463b081d19b7a00e3c`, llama.cpp source tag **b10453** (`3cb7ffb`) **HIP** build `GPU_TARGETS=gfx942` against existing HIP **7.14**, device **ROCm0** = AMD Instinct MI300X VF, greedy jinja `enable_thinking=false`, `prompts/smoke-tests.json`.  
**Not claimed:** Optimized, Production-ready, vLLM, Transformers, Vulkan, Radeon, laptop, Lightning BF16, MTP sidecar.

Environment snapshot for the host remains `results/mi300x/2026-08-15_172057Z/environment/`. File was Hub-downloaded and hashed on the laptop, then rsync'd; host `sha256sum` matched.

## Stack

- `llama-cli --list-devices`: `ROCm0: AMD Instinct MI300X VF (196288 MiB, 195956 MiB free)`
- Verbose probe: `using device ROCm0 (AMD Instinct MI300X VF)`, `offloaded 53/53 layers to GPU`, ROCm0 model buffer **17658.15 MiB**
- Architecture: `nemotron_h_moe`
- Left the jupyter `rocm` container alone

## Prompt-by-prompt

Same greedy thinking-off set as the laptop Validated Lightning runs (RAM vs storage, 1536 GB, factorial, two-sentence MI300X summary, exact JSON).

## Material caveats

- Still an SR-IOV VF.
- HIP binary reports `build 1` (local source build of tag b10453), not the GitHub Ubuntu tarball.
- Docker AMD `rocm/llama.cpp` b6652 was **not** used (too old for `nemotron_h_moe`).
