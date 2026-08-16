# Terminology

These words are used as **project status vocabulary**. Do not interchange them in the compatibility matrix, README status table, or customer-facing reports.

## Validation result labels

| Label | Meaning |
| --- | --- |
| **PLANNED** | We intend to run this test. No evidence exists yet. |
| **NOT TESTED** | In scope, not yet executed. |
| **IN PROGRESS** | A run is underway or logs are being analyzed. |
| **BLOCKED** | We cannot proceed without a change we have identified (missing GPU, missing kernel, gated download, insufficient memory, CUDA-only dependency). |
| **PASS** | Recorded evidence that the stated test succeeded on the stated stack. Must link to `results/`. |
| **PASS WITH CAVEATS** | Succeeded, but a limitation is material (wrong tokenizer behavior, reasoning traces leak, partial tool calling, context much shorter than claimed, etc.). |
| **FAIL** | The stated test was attempted and did not succeed. Preserve the log. |
| **THEORETICALLY FEASIBLE** | Memory, architecture, or vendor docs make a run plausible. **Not a PASS.** |
| **NOT PRACTICAL** | Single PCIe card (MI350P, Radeon) or this Ryzen AI laptop cannot hold the weights. Do not use this label on OAM Instinct (MI300X / MI325X / MI350X / MI355X) when a 2×/4×/8× count exists. |
| **NOT APPLICABLE** | Wrong device class or the model has no path there (for example NVFP4 claimed as an Instinct kernel path without an AMD implementation). |
| **NOT YET VALIDATED** | Assessment is theoretical or documented from vendor spec only. |

## Maturity labels (never skip levels)

### Runs

The checkpoint loaded on the named AMD device through the named runtime and generated tokens. The command, environment, and output are stored. Output has not necessarily been judged reasonable, and the test has not necessarily been reproduced.

### Validated

A Runs configuration that was reproduced (or reviewed as a first-run with complete artifacts) where:

- environment snapshot exists
- model id and revision are recorded
- prompts are the repo's deterministic set (or a documented superset)
- generated text is judged reasonable for those prompts
- known caveats are listed

Validated does **not** mean fast, quantized, long-context, or supportable as a product.

### Optimized

Validated, plus evidence that an AMD-relevant optimization changed performance or memory with measurements (same hardware, same checkpoint family, recorded before/after). Kernel work, FP8 that actually executes on the GPU, MoE/Mamba backend changes, and serving flags belong here — only after they are measured.

### Production-ready

Optimized, plus operational evidence someone else could run without this repo's authors on the call: install recipe, failure modes, tool calling if claimed, context lengths actually tested, license, and monitoring. This project has **not** reached this level for any Nemotron model on AMD.

## Other terms used carefully

| Term | Meaning here |
| --- | --- |
| **Open weights** | A checkpoint you can download (subject to license and gating). Not the same as a portable runtime. |
| **NVIDIA-specific runtime** | TensorRT-LLM, NIM, FlashInfer-only flags, NVFP4 kernels, CUDA-only wheels. |
| **Fits in memory** | Raw weights + naive overhead appear smaller than device memory. Matrix Fit values: **1×** / **1× tight** / **2×** / **4×** / **8×** on OAM Instinct; **doesn't fit** on MI350P, Radeon, and Ryzen AI when one card or this laptop cannot hold the weights. See [`compatibility-matrix.md`](compatibility-matrix.md). |
| **Ryzen AI** | The platform (CPU + Radeon iGPU + XDNA NPU). Not a single accelerator. |
| **iGPU** | Integrated Radeon GPU (on this laptop: gfx1150 / Radeon 890M). |
| **NPU / XDNA** | The Ryzen AI NPU (`amdxdna`, `/dev/accel`, rocminfo `aie2`). Separate from the iGPU. |
| **Engineering characterization** | Informal latency/throughput collection. Not an official benchmark. |
