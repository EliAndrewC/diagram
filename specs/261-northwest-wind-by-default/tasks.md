# Tasks - feature 261, the wind is northwest unless a map declares otherwise

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6). Research: [`research.md`](research.md) (R0-R4).
American spellings, hyphens only.

**No task here is `research: physical`.** The northwest default and the katabatic reading are already cited in
`research/vegetation/030` from sources read and quote-checked before this feature; no new source is used and no
historical question is reopened. What changes is which of the two recorded forms the map takes by default - the
GM's ruling - and the record is rewritten to say so. `quote-check` and `record-format` still run on the changed
entry (T10).

## Phase 1 - the engine (D1-D3)

- [ ] T01 The default: `DEFAULT_WINDWARD`, `plan_site` takes it unless the spec declares a wind; `windward_for`
      and `WIND_TURNS` deleted with the retirement reasoned at the constant; `meta.wind_source`
      research: rendering
      verify:
- [ ] T02 The seat bends to the wind: `WIND_BACK_MIN_DOT`, the off-wind fallback, `seat["offwind"]`, and
      `meta.seat_offwind` where `stage_ways` used to rename the wind
      research: rendering
      verify:
- [ ] T03 The fallback order (D3): wind-facing clean, off-wind clean, divided with a wind-facing one first
      research: rendering
      verify:

## Phase 2 - measurement (R1-R3)

- [ ] T04 R1 trial and R2 seed search, recorded
      research: rendering
      verify:
- [ ] T05 R3 cohort both ways, baseline in a detached worktree; every new failure checked against it
      research: rendering
      verify:

## Phase 3 - the pool (D4)

- [ ] T06 Sawada 6 -> 24 and Mizuguchi 23 -> 27, the reason in each generator; all five re-rolled
      research: rendering
      verify:
- [ ] T07 The pool test: no spec declares a wind; every manifest NW / regional / not off-wind / every household
      seated / belt center within 45 degrees of northwest
      research: rendering
      verify:

## Phase 4 - the page (D5)

- [ ] T08 `windbreak_default` and its wiring; the class `What`, `Entry`, the snapshot; `siblings.json`
      research: rendering
      verify:

## Phase 5 - the record and the docs (D6)

- [ ] T09 `research/vegetation/030` rewritten to the rule as built, arcs re-measured, the footnote gloss;
      `hamletgen.md`, the two package indexes, the five notes files
      research: rendering
      verify:
- [ ] T10 `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class
      research: rendering
      verify:

## Phase 6 - acceptance

- [ ] T11 `make done` green
      research: rendering
      verify:
- [ ] T12 `settlement-review`, one agent per re-rolled map, findings through `escalation-check`; ledger rows
      research: rendering
      verify:
