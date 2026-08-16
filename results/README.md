# Results

Every experiment writes a **new** timestamped directory. Never overwrite.

```text
results/<platform>/<YYYY-MM-DD_HHMMSS>Z/
  environment/          collect-env.sh snapshot
  transformers/         result.json from smoke tests
  vllm/                 serve logs, OpenAI API traces
  benchmark/            engineering characterization only
  logs/
  run-metadata.json
```

Large artifacts (weights, core dumps, multi-gigabyte logs) stay out of Git. JSON metrics, short logs, and `run-metadata.json` may be committed.

## `run-metadata.json` schema

```json
{
  "date": "",
  "platform": "mi300x | ryzen-ai | radeon",
  "gpu": "",
  "model": "",
  "model_revision": "",
  "precision": "",
  "runtime": "transformers | vllm | llamacpp | other",
  "runtime_version": "",
  "rocm_version": "",
  "pytorch_version": "",
  "result": "NOT TESTED | PASS | PASS WITH CAVEATS | FAIL | BLOCKED",
  "notes": ""
}
```

`result` here records a **test artifact**. It is not the maturity labels Runs / Validated / Optimized / Production-ready. See `docs/terminology.md`.

## Local evidence already collected

| Path | What it is | Nemotron execution? |
| --- | --- | --- |
| `results/ryzen-ai/2026-08-15_162031Z/` | First Strix Point env snapshot | No |
| `results/ryzen-ai/2026-08-15_171202Z/` | Repeat Strix Point env snapshot | No |
| `results/mi300x/` | Empty until the operator runs collect-env on MI300X | No |
| `results/mi300x/2026-08-15_172057Z/` | MI300X environment snapshot | No |
| `results/mi300x/2026-08-15_172557Z/` | Transformers FAIL (tokenizer harness) | No (load only) |
| `results/mi300x/2026-08-15_172810Z/` | Transformers greedy smoke PASS | Yes |
| `results/mi300x/2026-08-15_223840Z/` | vLLM OpenAI serve PASS | Yes |
| `results/mi300x/2026-08-16_020625Z/` | MoE autotune FAIL | No JSON |
| `results/mi300x/2026-08-16_022238Z/` | Engineering characterization (memory + conc 1/2/4) | Yes — not a benchmark |
| `results/mi300x/2026-08-16_024048Z/` | Transformers thinking on/off | Yes |
| `results/mi300x/2026-08-16_024220Z/` | vLLM context ladder 4K→128K | Yes — not 1M |
| `results/mi300x/2026-08-16_031205Z/` | Pinned Transformers smoke | Yes — **Validated** greedy thinking-off |
| `results/mi300x/2026-08-16_054423Z/` | Nano 4B BF16 Transformers smoke | Yes — **Validated** greedy thinking-off |
| `results/mi300x/2026-08-16_054857Z/` | Embed 1B cosine | Yes — **Runs** |
| `results/mi300x/2026-08-16_055129Z/` | Embed 8B cosine | Yes — **Runs** |
| `results/mi300x/2026-08-16_055206Z/` | text rerank 1B | Yes — **Runs** |
| `results/mi300x/2026-08-16_055737Z/` | VL rerank 1B text path | Yes — **Runs** (no images) |
| `results/mi300x/2026-08-16_055802Z/` | ColEmbed VL 3B dummy image | Yes — **Runs** |
| `results/mi300x/2026-08-16_061905Z/` | ColEmbed VL 4B | Yes — **Runs** |
| `results/mi300x/2026-08-16_061921Z/` | ColEmbed VL 8B | Yes — **Runs** |
| `results/mi300x/2026-08-16_061940Z/` | omni-embed 3B | Yes — **Runs** |
| `results/mi300x/2026-08-16_060037Z/` | ASR 3.5 pipeline | Yes — **Runs** (empty tone) |
| `results/mi300x/2026-08-16_055324Z/` | Content Safety 3.5 | Yes — **Runs** |
| `results/mi300x/2026-08-16_055356Z/` | Safety Guard 8B v3 | Yes — **Runs** |
