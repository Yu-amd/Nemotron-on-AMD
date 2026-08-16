# Review: Nano 4B FP8

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS` from harness)  
**Claim allowed:** **Runs** only, with a material caveat. **Not Validated.**

Loaded and generated on 1× MI300X VF, rev `3fe6dab7…`. All five greedy prompts returned a looping `a A A A…` string. That is not reasonable output. Treat as **R-FNUZ** (NVIDIA OCP FP8 vs MI300 FNUZ). Do not install CUDA mamba-ssm. Not a Nano 4B BF16 result. Not vLLM.
