# Review: NVIDIA-Nemotron-Parse-2.0

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/NVIDIA-Nemotron-Parse-2.0`, revision `635b84d9b09bb9526b9a684d0b2c953d3cc3df05`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, custom `NemotronParseForConditionalGeneration`, dummy 64×64 PNG.  
**Not claimed:** Validated OCR quality, production parse, Optimized.

Load ~1.29 GiB allocated. Dummy image generated: `Extract any visible text as markdown. **Figure 1:** _S<sub>c</sub>-S<sub>d</sub>_=0` — plausible VLM noise, not a document-QA score.

Earlier FAILs kept: `timm`, `einops`, `open_clip`, AutoModelForImageTextToText class mismatch. Extras: `timm==1.0.15 --no-deps`, `einops`, `open-clip-torch --no-deps`, `ftfy`, `regex`. RADIO submodule `nvidia/C-RADIOv2-H`.
