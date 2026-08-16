# Review: Nano Omni 30B BF16 (RADIO FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none for generate. Nested FA2 → eager **worked**. `Tee.isatty` **worked**. Then RADIO (`nvidia/C-RADIOv4-H`) raised `ValueError: The input resolution must be a multiple of self.min_resolution_step`. Input `torch.Size([1, 72])`, nearest `16×64`.

Text-only `task=causal` still constructs the vision tower. Not a vLLM result. Not FlashInfer. First FA2 FAIL `062426Z` kept.

Revision `24e67ea000b7c2837fc8f9488aa2008524fac8ba`.
