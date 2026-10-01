# T34 - the seeded tier experiment (plan section I, decision D12)

Run 2026-10-01, 16:44-16:51 UTC. One seeded case per check: one Opus leg (the pinned tier) and three Sonnet legs, all at the
check's pinned effort (`high`). Each leg ran as a headless `claude -p --agent <check>` session, hooks off, in its own scratch
clone of this clone at `b996746bf` (the 251 harness, `specs/251-*/measure/run_seeded.sh`; 2400 s timeout, five at a time).
The Sonnet clones differed from the Opus clone only in `model: sonnet` in the five agent files. Each leg got its own
clone so that a run's verdict record could not read as the "previous verdict" of the next run. In every clone,
`_review_prereq._fresh` was stubbed to green, because a scratch clone has no gate stamp and every contract stops at
NOT-REVIEWABLE without one. Each leg's prompt is the tooling's own `DISPATCH` text (`_review_snapshot.py`), written by
`mkprompts.py`, with the snapshot under the clone's `.git/review-snapshot/<unit>/{clone,main}`. Every leg's reply is in
`replies/`.

**The rule** (FR-012): a check moves to Sonnet only if Opus found the seeded finding AND all three Sonnet runs found it. If
Opus missed it, that is recorded and the check stays on Opus.

## The cases

| check | unit | how it was seeded | the known finding |
|---|---|---|---|
| glyph-check | `glyph-check--drying-rack` (Sawada, `glyph-redrawn: drying rack`) | Sawada was regenerated at HEAD with the rack drawn in its pre-2732ea565 form: an outlined box, a center pole, and cross-bar posts. Main's side has the current gold line with dots. The sentence in the Sawada notes that recorded the old catch was stripped from the snapshot and the pool copy. | the rack reads as the woodpile or wood shed beside the same houses (settlement-review, Sawada, 2026-09-28) |
| settlement-review | `settlement-review--ashigawa` (a map new to the pool) | `pool/hamlets/ashigawa/ashigawa.gen.py` is Sawada's `HamletSpec` with only the name changed (houses byte-identical), plus fresh notes that declare reed cutting. There is no main side. | RE-SKIN of Sawada (the twin detector) |
| fix-check | `fix-check--kashikawa` (`gm-fix: kashikawa - "two ditches run side by side down the paddies, like a doubled line"`) | Kashikawa was regenerated at HEAD with `drop_twin_deliveries` disabled in `waterfields/comb.py`, so the 340 ft twin (drawn_channels 7/10, 26 ft apart) stays. Main's side is the mirror's render, which also has the twin. The offered record is a count over the PLANNED channel list. | yes, still there; the fix did not fire; the record is a proxy |
| building-review | `building-review--hoshigaoka-shrine` (`layout-revised`) | the RECORDED case: the sheet and notes at d2f025dbc (the kitchen garden moved to the forecourt's foot beside arches 4-5), with main = 42bf5f8a5. Rendered with resvg, because the current `sheet-render` refuses pre-286 captions. | the service and night-soil route to the bed crosses the forecourt past the basin (building-review 93dc74cb, 2026-09-28, error 1) |
| size-audit | `size-audit--latrine` (a sized kind new to the sheet, no band) | the current Hoshigaoka sheet with the privy rect enlarged from 15 x 15 px to 42 x 42 px: 14 x 14 ft against a recorded 5 x 5 ft. | the latrine is OVERSIZED or WRONG (about 2.3x linear) |

## Runs

Tokens are total input (fresh plus cached) and output, from each run's own `run.json`; they agree with
`seeded.py usage '*t34*/*.jsonl'`.

| check | leg | found? | verdict | wall | tokens |
|---|---|---|---|---|---|
| glyph-check | Opus | **missed** - weighed the wood shed as a confusable and dismissed it; F1 "ladder or rail" questionable | PASS | 127 s | 713k in / 10.6k out |
| glyph-check | Sonnet 1 | missed - wood shed confusion called "unlikely" (nitpick) | PASS | 58 s | 298k / 5.4k |
| glyph-check | Sonnet 2 | missed - "dark slats resemble the wood shed's marks" as a nitpick only | PASS | 41 s | 195k / 4.7k |
| glyph-check | Sonnet 3 | missed - wood shed and byre resemblance as a nitpick | PASS | 29 s | 137k / 3.0k |
| settlement-review | Opus | **found** - RE-SKIN of sawada (error) | NEEDS-WORK | 62 s | 242k / 5.5k |
| settlement-review | Sonnet 1 | found | NEEDS-WORK | 37 s | 150k / 3.3k |
| settlement-review | Sonnet 2 | found (also: declared reed cutting ABSENT) | NEEDS-WORK | 36 s | 197k / 3.7k |
| settlement-review | Sonnet 3 | found (also: declared reed cutting ABSENT) | NEEDS-WORK | 39 s | 250k / 4.0k |
| fix-check | Opus | **found** - yes still; did not fire; record a proxy | NEEDS-WORK | 63 s | 295k / 5.7k |
| fix-check | Sonnet 1 | found (all three) | NEEDS-WORK | 36 s | 193k / 3.5k |
| fix-check | Sonnet 2 | found (all three) | NEEDS-WORK | 35 s | 163k / 2.9k |
| fix-check | Sonnet 3 | found (all three) | NEEDS-WORK | 34 s | 136k / 2.5k |
| building-review | Opus | **found** - E1: the bed's carry, night soil included, crosses the forecourt past the basin | NEEDS-WORK | 110 s | 246k / 9.1k |
| building-review | Sonnet 1 | missed - "crosses the forecourt's lower west side, which is open ground and not a ceremonial route -> ok" | PASS | 16 s | 71k / 1.9k |
| building-review | Sonnet 2 | missed - "crosses open ground... does not cross the sanctuary. ok" | PASS | 22 s | 89k / 2.6k |
| building-review | Sonnet 3 | missed - "follows the clearing's west edge, so it stays off the villagers' gathering ground. ok" | PASS | 28 s | 91k / 2.9k |
| size-audit | Opus | **found** - WRONG, 2.3x per side, against a cited 5-shaku-square privy | NEEDS-WORK | 268 s | 471k / 9.2k |
| size-audit | Sonnet 1 | missed - anchored on a multi-seat temple privy and rated 14 ft ok | PASS | 32 s | 99k / 2.3k |
| size-audit | Sonnet 2 | found - OVERSIZED 1.6x (an estimated anchor; no page quoted) | NEEDS-WORK | 39 s | 120k / 2.6k |
| size-audit | Sonnet 3 | found - OVERSIZED, 2.3x | NEEDS-WORK | 37 s | 142k / 2.7k |

## Decisions

- **glyph-check: stays on Opus.** Opus MISSED the seeded finding, so the rule keeps the check where it is, and none of the
  Sonnet runs scored it as an error either. The seed may be weaker than the recorded case. At the current render the rack
  is about 3 x 7-16 px at fit zoom, and the woodpile is retired (feature 280), so the confusable is now the wood shed, which
  every leg weighed. The original catch was made against a page that still drew the eaves woodpile. A stronger glyph seed
  (a mark that reuses another class's exact glyph) is the next measurement if the tier is revisited.
- **settlement-review: moves to Sonnet** (effort stays `high`). Opus and all three Sonnet runs named the re-skin; two Sonnet
  runs also caught that the declared reed economy was not drawn.
- **fix-check: moves to Sonnet** (effort stays `high`). All four legs answered the GM's question first ("yes, still"),
  found that the fix did not fire, and named the proxy record.
- **building-review: stays on Opus.** Opus found the circulation error; 0 of 3 Sonnet runs did. Each Sonnet run read the
  forecourt as open ground rather than ceremonial space.
- **size-audit: stays on Opus.** Opus found it and cited a quoted period dimension; 2 of 3 Sonnet runs found it, from
  estimated anchors. Sonnet 1 passed it on a multi-seat temple anchor.

What this costs and saves, measured on these legs: Sonnet ran at 0.55-0.65 of Opus's wall time on the two checks that move
(settlement-review 37 s against 62 s; fix-check 35 s against 63 s), with 0.6-0.9 of its input tokens.

Limits, stated:
- One seeded case per check, as plan I sets (the GM 2026-09-19: small slices with known findings).
- A Sonnet check that later misses a finding Opus would have caught goes back to Opus by the same experiment run on that
  case.
- The glyph contract itself lists "the drying rack as a woodpile" among its recorded catches, which every leg read.
