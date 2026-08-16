# Radeon compatibility (research only)

**Hands-on status: NOT TESTED.** This project currently has no discrete Radeon GPU attached.

ROCm support claims below come from AMD’s Linux system-requirements page, checked **2026-08-15**:

https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html

If a GPU is **not** on that table, this repo will not call it “ROCm-supported.” Community/TheRock nightlies are a separate, explicitly weaker category.

Radeon / Ryzen consumer enablement also has a dedicated doc tree: [Use ROCm on Radeon and Ryzen](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/index.html). Instinct-only recipes must not be copy-pasted.

## Representative hardware

Official ROCm support column is **software support**, not Nemotron validation.

| GPU (examples) | Arch | LLVM | Memory (vendor) | ROCm list (2026-08-15) | PyTorch | vLLM (docs list) | llama.cpp | Largest realistic Nemotron class (hypothesis) | Nemotron status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Radeon PRO W7900 | RDNA3 | gfx1100 | 48 GB GDDR6 | Officially supported (Ubuntu 24.04.4 / 22.04.5, RHEL 10.1 / 9.7) | Expected where ROCm PyTorch ships gfx1100 | vLLM ROCm hardware list includes RX 7900 series (gfx1100/1101) — **not a Nemotron test** | Applicable in principle (HIP/Vulkan) | Nano 4B BF16; Embed; **quantized** Nano 30B. **Not** Nano 30B BF16 (~60 GB) | NOT TESTED |
| Radeon PRO W7800 48GB | RDNA3 | gfx1100 | 48 GB | Officially supported | Expected | Same as above | Applicable | Same as W7900 | NOT TESTED |
| Radeon PRO W7800 | RDNA3 | gfx1100 | 32 GB (confirm SKU) | Officially supported | Expected | Same | Applicable | 4B / Embed / aggressive quant only | NOT TESTED |
| Radeon AI PRO R9700 | RDNA4 | gfx1201 | 32 GB class (confirm SKU before quoting) | Officially supported | Expected | vLLM lists RX 9000 series gfx1200/1201 | Applicable | 4B / Embed / quantized Nano | NOT TESTED |
| Radeon AI PRO R9600D | RDNA4 | gfx1201 | Confirm SKU | Officially supported | Expected | Same | Applicable | Smaller local models | NOT TESTED |
| RX 7900 XTX | RDNA3 | gfx1100 | 24 GB | Officially supported | Expected | Listed | Applicable | 4B / Embed / Q4 Nano **maybe**; 30B BF16 **NOT PRACTICAL** | NOT TESTED |
| RX 9070 XT | RDNA4 | gfx1201 | 16 GB | Officially supported | Expected | Listed | Applicable | 4B / Embed; 30B BF16 **NOT PRACTICAL** | NOT TESTED |

OS footnote from AMD: those Radeon/PRO rows “only support Ubuntu 24.04.4, Ubuntu 22.04.5, RHEL 10.1, and RHEL 9.7” on the page we fetched. Verify against the live matrix before telling a customer to install.

## Practical Nemotron guidance (still NOT TESTED)

Prioritize:

1. Nemotron 3 Embed 1B
2. Safety Guard 8B (generic Llama) if ROCm Transformers is healthy
3. Nano 4B BF16 or FP8
4. Community Nano 30B GGUF via llama.cpp; official Nano 4B GGUF `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF`

Avoid as a first Radeon experiment:

- Nano 30B BF16
- Super / Ultra any precision
- NVFP4 official checkpoints

vLLM on Radeon is listed at the **framework** level (gfx1100/1200). Hybrid Mamba-MoE Nemotron on those targets is a **separate** question.
