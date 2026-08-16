# Review: Lightning 30B BF16 vLLM

**Date:** 2026-08-16  
**Artifact:** `vllm/openai-api/summary.json` (`result=PASS`)  
**Claim allowed:** **Runs** / PASS WITH CAVEATS. Not Validated for vLLM. Not Optimized. Not Nano 30B.

AMD Docker vLLM, `max-model-len=8192`, served name `nemotron-lightning-bf16`. Health, thinking-off chat, and sequential integers succeeded. RAM/storage answer was reasonable. No FlashInfer. Transformers greedy remains the **Validated** claim (`062756Z`).
