# Ryzen AI platforms

Ryzen AI is a **platform**, not one accelerator. Always name the compute target:

1. **CPU** (Zen cores)
2. **Radeon iGPU** (RDNA, ROCm/HIP or Vulkan)
3. **XDNA NPU** (`amdxdna`, `/dev/accel`, rocminfo `aie2`)

This project’s laptop is documented in [`strix-point.md`](strix-point.md).

NPU claims require a Nemotron execution path **on the NPU**. None is identified as of 2026-08-15. Running ROCm on the iGPU is **not** NPU evidence.
