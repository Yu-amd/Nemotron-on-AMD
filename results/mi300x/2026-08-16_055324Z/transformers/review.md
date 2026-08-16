# Review: Nemotron 3.5 Content Safety

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/Nemotron-3.5-Content-Safety`, revision `35645ed3543b7e7ffaed2e788699e57a5051497c`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, greedy generate. Architecture `Gemma3ForConditionalGeneration`.  
**Not claimed:** Validated safety policy, production guardrail, Optimized, Nano 30B.

Load ~8.09 GiB. Two informal prompts both produced `User Safety: safe`. That is a shape check, not a red-team.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| safe-hello | Reasonable shape | `User Safety: safe` for “capital of France”. |
| policy-shape | Reasonable shape | Banana-bread classify also `User Safety: safe`. |

## Caveats

- Not a catalog of harmful prompts (out of scope for this repo’s smoke).
- Do not copy onto Safety Guard 8B v3 or Nano LM.

Logs: `logs/family-smoke.log`.
