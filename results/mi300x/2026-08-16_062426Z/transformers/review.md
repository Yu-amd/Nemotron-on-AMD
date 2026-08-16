# Review: Nano Omni 30B BF16 (first FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Error:** `FlashAttention2 has been toggled on` and the CUDA FA2 package is absent. Config requested FA2; a later harness retry had **dropped** `attn_implementation=sdpa`. Recorded as TRANSFORMERS/software, not a HIP OOM.

Retry forces SDPA and does not pop that flag.
