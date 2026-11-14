# Visual reviewer comparison — free models

**Date:** 2026-11-14
**Question:** Can LongCat 2.5 Free replace DeepSeek V4.1 Flash Free for the MPL visual-proof task?

**Models (both free):**

- DeepSeek V4.1 Flash Free — `opencode/deepseek-v4.1-flash-free#max`
- LongCat 2.5 Free — `opencode-go/longcat-2.5-free`

**Method:** 12 frames, identical prompt, four read-only subagents (two batches of six per model). No paid model calls in the final comparison; earlier paid baseline probes were stopped. No boundary promotion. Raw key results: `analysis/evidence/free-visual-model-comparison.json`.

## Ground truth

Clocks were checked against the pixels, not just the existing ledger:

| Frame | Expected clock | Expected teams | Note |
|---|---|---|---|
| `DF-1062-2464` | `00:19` | ONIC / DEWA | clean HUD |
| `VF-1037-base` | `21:08` | AE / NAVI | pixel-verified |
| `VF-1107-early` | `05:08` | TLID / ONIC | pixel-verified |
| `DF3-w01d02-12301` | blurred (~`04:24`) | RRQ / EVOS | **excluded from clock scoring** |

`DF3-w01d02-12301` is a replay of match 1, not the 1039 series. The paid DeepSeek ledger labels it DEWA/RRQ/`04:38`; the pixels show RRQ/EVOS and a blurred clock. That is a ledger pairing error, not a model result. It does not affect the 0 verified boundaries, but it is a warning against treating any single review as ground truth.

## Head-to-head

| Frame | Expected | DeepSeek Free | LongCat Free | Edge |
|---|---|---|---|---|
| `DF-1062-2464` | `00:19`; ONIC/DEWA | `00:19`; teams `[]` | `00:19`; DEWA/ONIC | LongCat |
| `VF-1037-base` | `21:08`; AE/NAVI | `21:06`; AE/NAVI | `21:08`; RE/NAVI | split |
| `VF-1107-early` | `05:08`; TLID/ONIC | `05:08`; TLID/ONIC | `05:08`; TLID/ONIC | tie |
| `VF-1037-replay` | no clock; no tags | no clock; `[]` | no clock; NAVI | DeepSeek |
| `DF-W07D1-2038` | countdown `15:56`; GEEK/VITALITY | `15:56`; BTR/VITALITY | `15:56`; GEEK/VITALITY | LongCat |
| `DF-ALBERTTT-DRAFT` | no clock; no tags | no clock; `[]` | no clock; `[]` | tie |
| `DF3-w09d03-24946` | no game clock; video `6:55:46`; TLID/ONIC | correct | correct | tie |
| `DF2-w01d03-10609` | countdown `10:26`; VITALITY/GEEK | correct | correct + extra ONIC ticker | DeepSeek |
| `DF-1084-CROP` | countdown `15:51`; GEEK/VITALITY | correct | correct | tie |
| `DF2-w02d02-23262` | countdown `03:52`; no teams | correct | correct | tie |
| `DF-1094-1585` | countdown `17:00`; no current pairing | `[]` | DEWA/NAVI from next-match ticker | DeepSeek |
| `DF3-w01d02-12301` | blurred; RRQ/EVOS | `04:31`; EVOS | `06:26`; RRQ/EVOS | neither |

## Scoreboard

| Check | DeepSeek Free | LongCat Free |
|---|---:|---:|
| Valid JSON | 12/12 | 12/12 |
| Clean game clock exact | 2/3 | **3/3** |
| Countdown/overlay timer exact | 6/6 | 6/6 |
| False `literal_00_00` | **0/12** | **0/12** |
| False same-frame pairing | **0/12** | **0/12** |
| Team reads (exact/partial/wrong) | 9/2/1 | 8/3/1 |
| Observed direct-API stall | 1 empty response | 1 × 300s timeout, retry OK |

## What LongCat did well

- Read all three clean game clocks exactly: `00:19`, `21:08`, `05:08`. DeepSeek Free missed `21:08` as `21:06`.
- Never claimed a false `00:00` and never claimed same-frame pairing.
- Read every countdown correctly, including separating `DRAFT PICK IN 15:56` from a game clock.
- Read GEEK/VITALITY correctly where DeepSeek Free said BTR/VITALITY.
- Returned valid JSON in all 12 frames.

## Where LongCat failed

- On the blurred replay frame it reported `06:26` with **high confidence**. The actual clock is near `04:24`. A high-confidence wrong clock is the most dangerous failure for a `00:00` gate.
- Read AE as `RE` on the `21:08` frame. The player tags said `AE`; the top-bar code was small.
- Pulled DEWA/NAVI from a **next-match ticker** on the interview frame and presented them as visible teams.
- Labeled the paused VOD player-cam as `draft`.
- Had one 300-second stall in the direct API path; a retry succeeded. The subagent batches completed.

## DeepSeek Free’s failures

- Read `21:08` as `21:06` (2-second OCR miss).
- Read GEEK as BTR on the M49 frame.
- Under-reported teams on the `00:19` frame and the replay frame.
- Returned one empty response in the direct API pilot.

## Verdict

**LongCat 2.5 Free is capable as a free second opinion, not as the sole visual-proof reviewer.**

It is at least as good as DeepSeek Free on clean clock reading in this sample, and both are safe on the specificity check: no false `00:00`, no false pairing. But the task is a strict gate: one wrong team code or one `00:00` false positive invalidates a boundary. LongCat produced a high-confidence `06:26` on a blurred clock and misread AE as RE; that is enough to disqualify it as the authority.

Neither model can be certified for the actual gate yet, because **there is no real `00:00` frame in the corpus to test recall**. The existing broadcasts cut in after the clock started. This experiment only tests specificity and OCR on other clocks.

**Recommendation:**

1. Keep DeepSeek V4.1 Flash Free as the baseline reviewer.
2. Use LongCat 2.5 Free as a cheap cross-check/triage pass; require DeepSeek agreement before any promotion.
3. Do not switch the canonical gate to LongCat.
4. If a real same-frame `00:00` source appears, test both models on it before changing the contract.

## Limits

- 12 frames, one run per model per frame; not a statistical benchmark.
- No positive `00:00` control.
- `DF3-w01d02-12301` is blurred and excluded from clock scoring.
- Subagent read-tool image handling may differ from the canonical API attachment path.
- The existing visual ledger contains at least one pairing error (`12301`); verify pixels before treating ledger answers as ground truth.
