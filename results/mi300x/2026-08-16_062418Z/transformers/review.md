# Review: NVIDIA-Nemotron-Parse-2.0 (retry3 FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Error:** `open_clip` still reported missing. `open-clip-torch` was installed `--no-deps`; `import open_clip` needed `ftfy`. Next retry installs `ftfy` + `regex`.
