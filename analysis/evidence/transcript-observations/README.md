# Transcript observation ledgers

One staging JSONL file per source: `<source_id>.jsonl`.

Schema: `analysis/evidence/transcript-observation-schema.json`.

Record types:

- `observation` — atomic claim with exact quote, line/cue provenance, entities,
  destination, confidence, and status.
- `proposal` — proposed new Markdown category.
- `unresolved` — ambiguous player/team/hero/map/term reference.
- `run` — model, prompt version, token usage, counts, errors.

Rules:

- Staging ledgers are not canonical.
- Only `accepted` observations may be consolidated into Markdown.
- Quotes must be exact and hashed.
- Statistic claims must include `database_refs` from `tools/stats_query.py`.
- Never invent timestamps, speaker labels, entities, or numbers.
- Keep short quotations only; do not commit full transcripts.

Validate:

```text
python tools/validate_transcript_ledger.py \
  --ledger analysis/evidence/transcript-observations/<source_id>.jsonl \
  --segments analysis/evidence/transcript-segments/<source_id>.jsonl
```
