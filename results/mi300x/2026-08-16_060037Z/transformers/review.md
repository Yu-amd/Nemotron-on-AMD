# Review: nemotron-3.5-asr-streaming-0.6b (retry)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/nemotron-3.5-asr-streaming-0.6b`, revision `1c8deaecc64b91f034d73e08dd8b64625eb3395d`, Transformers ASR pipeline, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, `Nemotron3_5AsrForRNNT`.  
**Not claimed:** Validated speech recognition, streaming latency, NeMo CUDA stack as a requirement.

First attempt (`2026-08-16_055308Z`) **BLOCKED** (mis-labeled): missing `librosa`. That was a venv extra, not a CUDA/NeMo proof. Preserve that dir. This retry added librosa.

Load ~1.26 GiB peak. Synthetic 440 Hz 0.5 s tone transcribed as empty `{"text": ""}`. Expected for a tone, **not** WER evidence.

## Caveats

- Transformers pipeline path, not NVIDIA NeMo runtime.
- Empty transcript is not a quality PASS.

Logs: `logs/family-smoke.log`.
