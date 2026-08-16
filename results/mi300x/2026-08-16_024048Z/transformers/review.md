# Review: Transformers reasoning-on vs thinking-off

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`, 5/5)  
**Claim allowed after this review:** **Runs** for Transformers greedy thinking-off **and** sampled thinking-on on this stack, pinned snapshot.  
**Not claimed:** Validated (this used `prompts/reasoning-tests.json`, not the original smoke set), Optimized, vLLM long context, Production-ready.

## Stack

- Device: AMD Instinct MI300X VF
- Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, HIP 7.14.60850
- Checkpoint: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`
- `trust_remote_code` not required to load
- `enable_thinking` accepted by `apply_chat_template`
- Load ~58.9 GiB allocated (matches prior smoke)

Per-prompt JSON flags were honored (`enable_thinking`, `temperature`, `top_p`). `run-metadata.json` still records the CLI default `enable_thinking: false`; inspect each generation.

## Prompts

| ID | thinking | Sampling | Verdict | Note |
| --- | --- | --- | --- | --- |
| reasoning-on-math | on | temp 1.0 / top_p 1.0 | Reasonable | Thought then `8×192=1536`; `</think>` then user answer. Opening `<think>` is in the template, not in generated tokens. |
| reasoning-off-math | off | greedy | Reasonable | 1536 GB; no `</think>`. |
| system-and-user | off | greedy | Reasonable | Names MI300X / 192 GB HBM3 in one sentence. |
| system-think-token | on | temp 1.0 | Reasonable | `/think` in system is duplicative; `</think>` then `4`. |
| assistant-prefill-not-used | off | greedy | Reasonable | `READY` |

## Material caveats

- Thinking-on traces leak into `generated_text` as `</think>` plus the thought. Transformers does not apply `nano_v3`. vLLM serve (`223840Z`) split reasoning vs content.
- Opening `<think>` is a chat-template prefill, so raw decoded generations start mid-thought.
- This is **not** a pinned re-run of `prompts/smoke-tests.json`, so it does not by itself earn **Validated** for the earlier greedy smoke.

Logs: `logs/transformers-smoke-test.log`.
