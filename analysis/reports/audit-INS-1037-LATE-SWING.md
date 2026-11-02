# Audit — INS-1037-LATE-SWING

**Audit ID:** `AUD-1037-01`
**Insight version:** 1
**Verdict:** **partially supported**
**Date:** 2026-10-25

## Claim under audit

> AE’s 1037 game-1 win was a late defensive swing rather than wire-to-wire map control: commentary describes a 1v3 stand and a failed NAVI Lord conversion, the frame shows AE defending base at 21:08 with a ~1.9k gold deficit, and the final database line is a 2.0k gold win with less tower damage than NAVI. The specific “1v3 turning point” remains caster framing, not a fully verified causal event.

## Sources actually inspected

- Raw transcript copy: `analysis/sources/raw-transcripts/...Minggu 1 Hari 1...txt` (local, Git-ignored), lines 6451–6452 and 6524–6532.
- Timed alignment: `analysis/cache/timed/src-s18-w01d01.json`; 9,104 raw lines vs 9,104 timed caption snippets, 9,103 exact + 1 whitespace-normalized match.
- Broadcast video: `https://www.youtube.com/watch?v=40fehk2f4_E`, frames at requested 04:13:50, 04:14:05, 04:16:10; actual capture times 04:13:51.476, 04:14:06.335, 04:16:11.480.
- Database snapshot `mpl-s18-db-20c5ea2c51f3`, SHA-256 `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef` (current canonical snapshot; the 2026-10-31 winner-orientation migration changed only `matches.winner` values, so the score/gold/tower facts audited here are unchanged).
- Query catalog entries `Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-CLOSE-GOLD-WINNERS`.

## Quote and link validation

| Segment | Source span | Link | Result |
|---|---|---|---|
| `seg-src-s18-w01d01-L006451-L006452` | lines 6451–6452 | https://youtu.be/40fehk2f4_E?t=15240 | exact match after newline normalization |
| `seg-src-s18-w01d01-L006524-L006532` | lines 6524–6532 | https://youtu.be/40fehk2f4_E?t=15400 | exact match after newline normalization |

The quote checker found each quote at the asserted line span; the ledger records the SHA-256 of the exact text. Timestamps are **not native transcript metadata**; they come from the one-to-one YouTube auto-caption alignment (`youtube-auto-caption-alignment-v1`). They are cue times, not frame-accurate event times.

## Database checks

- `Q-MATCH-RESULT` (1037): schedule row is NAVI 0–2 AE on 2026-08-14; winner `team_b` in schedule orientation.
- `Q-GAMES` (1037): game 1 AE winner, duration 22:42; game 2 AE winner, 11:27.
- `Q-TEAM-GAMES` (1037): game 1 AE 72,200 gold / 20,158 tower damage; NAVI 70,169 / 33,132. AE won by 2,031 gold while dealing less tower damage.
- `Q-MATCH-DETAIL` (1037): after the guarded repair, the `matches` row has AE/NAVI order, score 2-0, and `winner='team_a'` (AE). The schedule row is NAVI/AE, 0-2, with `winner='team_b'` (also AE). No row-score mismatch remains; side tokens differ because team order differs. See `OBS-LINEAGE-WINNER`.

## Visual review (actually inspected)

| Frame | Actual time | Observed |
|---|---:|---|
| `VF-1037-replay` | 04:13:51.476 | Instant Replay banner; an AE play labelled “AE AFFAN … HAS SLAIN” near the base. |
| `VF-1037-base` | 04:14:06.335 | Game clock 21:08; AE 17–15 NAVI; AE gold 63.9K vs NAVI 65.8K; AE visible defending its base. |
| `VF-1037-post` | 04:16:11.480 | Post-game player-camera shot; confirms the game ended, not the fight sequence. |

The requested 04:15:45 frame failed the readiness/actual-time check and was **not** used. The broadcast overlay uses names that do not directly match the database’s Liquipedia handles, so no player join is asserted.

## Counterexamples searched

1. **Structured counterexample:** `Q-CLOSE-GOLD-WINNERS` returns other close-gold games where the winner had less tower damage, including 1074 game 2 and 1078 game 2. A close-gold win with lower tower damage is therefore not a unique AE signature.
2. **Corpus counterexample/related-use search:** regex `1v3|clutch|satu lawan tiga` found other uses, including W1D1 00:27:43 and W9D3 06:42:50. The phrase is descriptive commentary, not a standardized event measure.
3. **Alternative explanation:** NAVI may have lost through a later macro/Lord decision, not the 1v3 alone; the frame sequence does not show the full fight or communications.

## Verdict and reasoning

**Partially supported.**

Supported:
- The game was close (final +2,031 AE gold) and AE won with less tower damage.
- At 21:08 the reviewed frame shows AE defending its base while slightly behind on gold.
- The caster explicitly framed an AE 1v3 and a failed NAVI Lord attempt as important.

Not established:
- That the 1v3 *caused* the win.
- That this is a repeatable AE trait.
- That the broadcast frame shows the full sequence rather than a replay/camera selection.
- Any claim about communication, vision, reaction time or intent.

## Limitations

- Single game, single broadcast, selected frames; no full clip or replay sequence.
- Auto-captions have ASR errors and no speaker identity.
- Broadcast names and database handles differ; no player join is claimed.
- The database has no objective counts or communication/vision data.
- The close-gold/lower-tower pattern is not unique in the snapshot.
- Transcript verification establishes what the caster said; it does not establish why NAVI lost.

## Follow-up

Review a full clip from the first observable threat through the Lord attempt, record the AE and NAVI positions at each frame, and compare with another AE close game (1074 game 2 or 1078 game 2) before treating this as a coaching pattern. A coach should ask whether the defensive setup is repeatable or whether NAVI overcommitted.
