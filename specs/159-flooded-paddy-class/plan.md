# Implementation Plan: The blue paddy plot is its own kind

**Branch**: none - `SPECIFY_FEATURE=159-flooded-paddy-class` | **Date**: 2026-08-29 | **Spec**: [spec.md](spec.md)

## Summary

Give the FLOODED-tinted paddy plot its own interactive class so it highlights and opens apart from
the rice-green paddy, with an explanation written from the research pass (`research/fields.md`, "The
wettest plots are their own kind of ground - shitsuden, and why they read blue"). The whole change
is a class KEY chosen at one emit site plus one row of the vocabulary; nothing about the drawn map
moves.

## Technical Context

**Language/Version**: Python 3.14 (the container pin)

**Primary Dependencies**: none new

**Storage**: N/A - the class rides in the existing side list beside the record streams

**Testing**: pytest; `tests/interactive/test_classes.py` (registry invariants), `tests/interactive/test_page.py`
(the census and present-only data), `tests/full/interactive/test_page_browser.py` (Playwright, the
real page)

**Target Platform**: the generated `.html` beside every Mode B map

**Project Type**: the diagram engine

**Performance Goals**: unchanged - one string comparison per plot at draw time, in a loop that
already does that comparison for `flooded_plots`

**Constraints**: the `.svg` and `.png` must not move a byte (spec SC-004); the explanation is ONE
shared per-kind string and must be true on every map that can carry the class

**Scale/Scope**: one new registry row, one emit-site expression, one sibling pair, three test files

**Single-artifact target**: `pool/hamlets/inashiro.gen.py` - the reference hamlet, the GM's named
target, ~19 s to roll. It carries 2 blue plots and 24 low ones, so it exercises the comb rule and
the sibling pair together. The pool step is its own task (T8): `make maps`, which reaches the four
maps that tint every low plot (enokida, tanada, yatsuda, kuwabata) - the cases the shared string
must also be true on.

**Every step is two steps**: T5/T6 are the reference settlement; T8 is the pool.

## Performance bookends (REQUIRED)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `159-start` | 167.6s | 41.9s | 48.1s | taken on UNMODIFIED engine code (20:03:33Z, 32 s before the first engine edit) - but on a CONTENDED box |
| after | `159-end` | 68.3s | 17.1s | 19.1s | 21:14:15Z, idle box |

**BAND 0 - nothing owed** (`make perf-review`): no increase on the total or on any seed.

**DO NOT READ THE -59.2% AS A SPEEDUP.** This change adds one string comparison per plot at an emit
site that already compares the same two values one line below; it cannot make a roll faster, let
alone by half. The baseline was measured while another session's `cohort_audit --count 48` was
saturating the box (~20 forkserver workers) and a stale `dmypy` daemon held 422 MB; the closing
measurement ran on an idle one. The pair is therefore honest about the DIRECTION (no regression -
which is what the bookend is for) and worthless as a magnitude. Recorded here so a later session
mining the perf log does not attribute a 59% gain to a class tag.

`make perf-report AGAINST=159-start` before the push; any seed over 5% slower is diagnosed here in
writing. The expected delta is nil - the emit site already compares `p["fill"]` to `FLOODED` one
line below the one being changed, so the added work is a second comparison of two interned strings
per plot, and the tinted plots number 2 on the reference map.

## Constitution Check

- **I. Accessibility-First Viewports**: N/A - governs gm-assistant's webapp. (The `.html` this
  feature touches is a generated artifact, not that webapp; its behavior is verified by the
  Playwright suite under VI.)
- **II. Bold, Intentional Design**: N/A - same reason.
- **III. Pool Data Conventions**: N/A - no new pool content of a recurring kind; no map is added.
- **IV. One Canonical Home for GM Source**: N/A - no SOURCE blocks added or moved.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: PASS - no task touches SOURCE markers.
- **VI. Verify Before Reporting Done**: PASS - `make done` for the Python; the reference hamlet
  regenerated and opened (T6); `make maps` for the pool (T8); the browser test drives the real page
  rather than asserting on the registry alone. `settlement-review` is not owed: the drawn map does
  not change (SC-004), which is the standing ruling of 2026-08-29 - it will be recorded with the
  GM's words at the push, not assumed.
- **VII. De-Localized Generation by Default**: PASS - the explanation is per KIND and names no
  settlement, exactly as every other row.
- **VIII. Direct Voice Over Framing Distance**: PASS - the modal states what the plot is; the one
  place it must hedge (the drain-foot inference) is a disclosure the constitution requires, not
  narrational distance.
- **IX. Setting Integration**: PASS - nothing setting-specific; the research is real-world.
- **X. Python Discipline (NON-NEGOTIABLE)**: PASS - ruff, pyrefly, pytest, the coverage floors.
  Red-green on the new behavior: T3 writes the failing tests before T4 makes them pass. No file
  approaches 1,000 lines from this change (`classes.py` grows by one row, `comb.py` by one
  expression and its comment).
- **XI. Japanese Authenticity**: PASS and load-bearing - 湿田 shitsuden, 乾田 kanden, 谷津田 yatsuda,
  深田 fukada each pass the kanji / romaji / meaning triangle, and each is quoted from a published
  dictionary with the reading and the gloss in `research/fields.md`.
- **XII. Historical Grounding Bookends (NON-NEGOTIABLE)**: PASS. **Opening**: done before this plan
  was written - the `source-reader` pass of 2026-08-29, recorded as a full entry in
  `research/fields.md` with five new keys in `research/SOURCES.md`, and with its three failures
  (the maintained water depth, the canopy-closure visibility, the "Kishu-school" name) written into
  the re-sourcing queue rather than asserted. **Closing**: the class's `label_note` / `caveat` carry
  the liberty to the modal, and the Decisions Recorded table in `spec.md` lists every one.
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: PASS - baseline is a green `make done` on the
  merged tree; the drawn output is asserted unmoved on the reference map.
- **XIV. Fix Defects Where You Find Them (NON-NEGOTIABLE)**: two found and handled during the
  research pass, both recorded rather than silently patched, because both are research-record
  questions rather than code defects: the unsourced "four to six inches" in the shipped `paddy`
  modal, and the "Kishu-school" name. Both are in the re-sourcing queue and both are being reported
  to the GM. Neither is fixed under this feature - changing a shipped number on one failed fetch
  would be worse than queueing it.
- **XV. Keep Going**: PASS.
- **XVI. Build What Was Asked (NON-NEGOTIABLE)**: three `spec-fidelity` rounds; round 1 caught the
  universal-sampling error, round 2 struck an addition (the `field pond` sibling) and the two
  acceptance scenarios that still carried the round-1 falsehood.
- **XVII. The README is the GM's**: N/A.
- **XVIII. A Guard Owes a Test**: N/A - no guard script changes.

## Phase 0 - research

Complete before this plan. `research/fields.md`, "The wettest plots are their own kind of ground -
shitsuden, and why they read blue"; `research/SOURCES.md` keys `kotobank-shitsuden`,
`kotobank-kanden`, `kotobank-yatsuda`, `kotobank-fukada`, `fao-rice-water`.

## Phase 1 - design

**The class key and name.** Key `wet paddy`; name `wet paddy (shitsuden)`. The registry test asserts
the key is a substring of the name, and `slug()` must yield a CSS token. `flooded paddy` was
DECLINED as the key: every paddy on the map is flooded, so it names the wrong difference - the
distinction is that this one is wet ground rather than wet crop.

**The label.** `accurate`, with a caveat. The category and its penalties are READ from published
dictionaries; the liberties are that which plots wear the tint is a drawing convention (a share on a
comb field, all of them on a terrace or polder field) and that siting the wettest ground at the
drain foot is an inference from the attested cascade rather than a stated finding. Both go in the
liberty half of `label_note`, and `caveat` is that half verbatim - the machinery feature 156 built,
so the modal leads with what the plot IS and discloses the liberties under the why.

**The emit site.** `settlement/fields/comb.py` `_comb_draw_paddies` already imports `FLOODED` and
already compares `p["fill"]` to it, one line below, to write `flooded_plots`. The class becomes
`Split("wet paddy" if p["fill"] == _WF_FLOODED else "paddy", "bund")`. Deciding it from the fill
about to be drawn is what makes the class and the color unable to disagree (spec FR-002), and the
bund half is untouched (FR-003).

**What does NOT change**: the tint rules, `wet_plots`, `flooded_plots`, the land-use overlays, the
gate checks that read them, and every byte of the `.svg` and `.png`.
