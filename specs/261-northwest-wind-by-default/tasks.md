# Tasks - feature 261, the wind is northwest unless a map declares otherwise

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6). Research: [`research.md`](research.md) (R0-R4).
American spellings, hyphens only.

**No task here is `research: physical`.** The northwest default and the katabatic reading are already cited in
`research/vegetation/030` from sources read and quote-checked before this feature; no new source is used and no
historical question is reopened. What changes is which of the two recorded forms the map takes by default - the
GM's ruling - and the record is rewritten to say so. `quote-check` and `record-format` still run on the changed
entry (T10).

## Phase 1 - the engine (D1-D3)

- [x] T01 The default: `DEFAULT_WINDWARD`, `plan_site` takes it unless the spec declares a wind; `windward_for`
      and `WIND_TURNS` deleted with the retirement reasoned at the constant; `meta.wind_source`
      research: rendering
      verify: DONE. plan_site takes DEFAULT_WINDWARD unless the spec declares one; windward_for and WIND_TURNS deleted, the retirement reasoned at the constant; meta.wind_source written in water/skeleton.py. test_plan: NW for every fall and seed, a declared quarter used as declared.
- [x] T02 The seat bends to the wind: `WIND_BACK_MIN_DOT`, the off-wind fallback, `seat["offwind"]`, and
      `meta.seat_offwind` where `stage_ways` used to rename the wind
      research: rendering
      verify: DONE. WIND_BACK_MIN_DOT (cos 45); a margin off the wind is only the last fallback, seat[offwind] and meta.seat_offwind where stage_ways used to rename the wind. test_cluster: the seat faces the wind for all 8 quarters x 4 falls; the hemmed case falls back and says so.
- [x] T03 The fallback order (D3): wind-facing clean, off-wind clean, divided with a wind-facing one first
      research: rendering
      verify: DONE. Order: clean wind-facing, clean off-wind, divided (wind-facing first) - feature 230 unchanged after two MODE 1 exception checks refused the wind-first order (research R4). brook_banks() fixed the divided test (D7). test_cluster covers both fallbacks and brook_banks.

## Phase 2 - measurement (R1-R3)

- [x] T04 R1 trial and R2 seed search, recorded
      research: rendering
      verify: DONE. research R1 (the trial: Kashikawa 0 clumps with the seat unchanged) and R2 (Sawada 1-30, Mizuguchi 1-30 plus five candidates through the real generator).
- [x] T05 R3 cohort both ways, baseline in a detached worktree; every new failure checked against it
      research: rendering
      verify: DONE. Baseline 37/48 in a detached worktree at HEAD; final engine 38/48, every failure also failing on the baseline (scatter_frame_breach), seed 37 fixed, no households_seated failure (research R3, R5).

## Phase 3 - the pool (D4)

- [x] T06 Sawada 6 -> 24, Mizuguchi 23 -> 27 and Kashikawa 3 -> 8, the reason in each generator; all five re-rolled
      research: rendering
      verify: DONE. Sawada 6->24, Mizuguchi 23->27, Kashikawa 3->8 (seed 14 refused for a 333-degree wrap), Inashiro kept at 4; reasons in each gen docstring; all five re-rolled on engine key 1ffef5ec (research R5).
- [x] T07 The pool test: no spec declares a wind; every manifest NW / regional / not off-wind / every household
      seated / belt center within 45 degrees of northwest
      research: rendering
      verify: DONE. tests/hamletgen/test_pool_wind.py: no pool spec declares a wind; every manifest NW / regional / not off-wind / every household / belt center within 45 deg of NW / arc at most 200 deg. Green in make quick.

## Phase 4 - the page (D5)

- [x] T08 `windbreak_default` and its wiring; the class `What`, `Entry`, the snapshot; `siblings.json`
      research: rendering
      verify: DONE. place.windbreak_default wired in page.py (the notes win); Windbreak What hooked not embracing, Entry names vegetation/030, Note names what the side rests on; siblings.json and the snapshot. test_place + test_page cover the three cases.

## Phase 5 - the record and the docs (D6)

- [x] T09 `research/vegetation/030` rewritten to the rule as built, arcs re-measured, the footnote gloss;
      `hamletgen.md`, the two package indexes, the five notes files
      research: rendering
      verify: DONE. vegetation/030 rewritten to the rule as built, arcs re-measured (113/134/87/168/157), gloss corrected; hamletgen.md, hamletgen and sitegen indexes, five notes files. make record also fixed to write the citations page (a notes-only edit was unwritable).
- [x] T10 `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class
      research: rendering
      verify: DONE. quote-check: 2/2 READABLE and VERBATIM, the katabatic clause trimmed to what the quote supports; record-format: Siberian high glossed, maps named, a history clause dropped; entry-drift: IN-STEP (embracing -> hooked applied).

## Phase 6 - acceptance

- [x] T11 `make done` green
      research: rendering
      verify: DONE. make done green on 0d44e65c (merged with main at 19837bc2): every test passed, coverage 100% (27454 statements), roll census green; the batching-test race and the stale roll roster were fixed on the way.
- [x] T12 `settlement-review`, one agent per re-rolled map, findings through `escalation-check`; ledger rows
      research: rendering
      verify: DONE. make verify ruled NO SETTLEMENT-REVIEW OWED (rendering-only feature, feature 248); the one earlier dispatch round came back NOT-REVIEWABLE on a red gate and held no map findings. The five maps are handed to the GM to look at, per their standing rule.
