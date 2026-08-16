# Review: fused-MoE autotune sanity (FAIL)

**Date:** 2026-08-16  
**Artifact:** `moe-tune/summary.json`  
**Claim:** none. This is a kernel-tuner **data point**, not Optimized, not a serving result.

## What ran

- Image: `rocm/vllm:rocm7.14.0_cdna_ubuntu24.04_py3.14_pytorch_2.11.0_vllm_0.23.0`
- Script: `/app/vllm/benchmarks/kernels/benchmark_moe.py --tune`
- Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- Host: MI300X VF, started `2026-08-15T23:48:58Z`, finished `2026-08-16T02:06:25Z` (~2h 17m)
- Docker exit 1, `OOMKilled=false`

## Progress before death

vLLM announced a 40,000-configuration search. Observed passes:

| Pass | Outcome |
| --- | --- |
| 608 configs | completed |
| 1,220 configs | completed |
| 2,780 configs | completed |
| `batch_size=8` | completed 2026-08-16 00:52:00 |
| 4,480 configs | died at 4.42k / 4.48k (~99%) |

No `E=128,N=1856,device_name=AMD_Instinct_MI300X.json` was written.

## Failure

```text
ray.exceptions.ActorDiedError: The actor died unexpectedly before finishing this task.
  File ".../benchmark_moe.py", line 951, in _distribute
    return ray.get(outputs)
```

Layer: **KERNEL**. Logs immediately before the actor death contain Triton/LLVM spill dumps (`SI_SPILL_AV128_SAVE`, `fused_moe.py:489`), which is consistent with a compiler crash on one of the remaining configs. dmesg in this window does **not** show an amdgpu reset (earlier SVM workqueue hog lines are from the previous vLLM serve).

## What this does not change

- Nano Transformers **Runs** and vLLM serve **Runs** still stand.
- Missing stock MoE config for `E=128,N=1856` on MI300X is still unfixed.
- Do not copy NVIDIA H100/B200 MoE JSON onto this device.
- Do not call this Optimized.
