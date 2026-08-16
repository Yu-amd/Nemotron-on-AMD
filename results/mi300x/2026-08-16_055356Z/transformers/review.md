# Review: Llama-3.1-Nemotron-Safety-Guard-8B-v3

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3`, revision `8fdc246ba3d56db9c469d534233b9f582d3afafa`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF. `LlamaForCausalLM`.  
**Not claimed:** Validated Guard policy, LoRA-specific serving, Optimized.

Load ~15.0 GiB. `trust_remote_code` not required.

## Prompt-by-prompt

| id | Verdict | Note |
| --- | --- | --- |
| safe-hello | Load only | Answered as a chat LM: “The capital of France is Paris.” Did **not** emit a Guard label. |
| policy-shape | Reasonable shape | One word `Safe` for banana bread. |

## Caveats

- This smoke did not apply a published Guard chat template / tool schema. First prompt behaves like a generic Llama.
- Informal. Not Content Safety 3.5. Not Nano 30B.

Logs: `logs/family-smoke.log`.
