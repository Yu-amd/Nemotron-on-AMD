# Review: Nano Omni 30B BF16 (Tee.isatty FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json`  
Nested `llm_config` FA2 was forced to **eager** (progress). Load then crashed in Transformers `loading_report._style` because the family-smoke `Tee` lacked `isatty`. Harness bug after a real FA2 workaround. Retry adds `Tee.isatty() -> False`.
