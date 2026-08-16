# Review: llama-nemotron-rerank-vl-1b-v2 (retry, text path)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/llama-nemotron-rerank-vl-1b-v2`, revision `9c20c4aedf9ec87b6b7346c3bc4754ea030dab35`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, **text-pair** SequenceClassification.  
**Not claimed:** Vision ranking, image inputs, Validated retrieval.

First attempt (`2026-08-16_055234Z`) **FAIL**: missing `requests` and ROCm `torchvision`. This dir is the retry after those extras.

Architecture `LlamaNemotronVLForSequenceClassification`. Load ~3.21 GiB. Custom code required.

## What ran

Text query/doc scores: MI300X HBM sentence **-1.33** > banana ** -6.64**. Images were **not** passed. This is not a VL ranking proof.

Logs: `logs/family-smoke.log`.
