# Review: nemotron-3.5-asr-streaming-0.6b (first BLOCKED)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=BLOCKED`)  
**Claim allowed:** none. This label over-called **BLOCKED**: the failure was missing `librosa`, and the harness substring `"nemo"` matched `NemotronAsrStreamingFeatureExtractor`. That is **not** a CUDA/NeMo-only proof.

Revision `1c8deaecc64b91f034d73e08dd8b64625eb3395d`. Successful retry: `2026-08-16_060037Z`.
