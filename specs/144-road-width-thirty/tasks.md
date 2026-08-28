# Tasks: The Mode B Highway Default Is ~30 ft (144)

**Input**: [spec.md](spec.md), [plan.md](plan.md); authority [gm-request.md](gm-request.md)

- [ ] T01 [US1] **Perf bookend before** - `make perf LABEL=144-start` on the unmodified tree.
      research: procedure
- [ ] T02 [US1] **The default** - `ground.py`: `self.lw(30)`; the docstring cites `tokaido-jawiki` (5 ken ≈ 29.5 ft, drawn 30) and drops "~18-24 ft"; the ~30 check fallbacks `M.get("road_width", 26)` -> 30; a test pins the default.
      research: physical
      - [x] research pass (feature 143: `tokaido-jawiki` READ - "街道の幅員を5間とし")  - [x] source-reader confirmed (the 143 capitals reader)  - [ ] recorded and cited
      scaffold: `l7r/diagram/settlement/structures/ground.py`, the check fallbacks; `tests/` width pin
      verify: one quick run after the whole diff is re-read
- [ ] T03 [US1] **The record** - `research/cities/capitals.md` "Street widths" (the GM's ruling; class accurate; the 26 ft gloss struck; the audit row), `settlements/cities/defenses.md` gate-throat gloss, `wip/shiro-daika.gen.py`/`.notes.md` comments; the feature 143 ledger G row 4 closed.
      research: procedure
- [ ] T04 [US1] **Reference settlement** - the map target (Inashiro alone first); the PNG re-examined (closing bookend).
      research: procedure
- [ ] T05 [US2] **The pool** - the map target widens to the tier once Inashiro is clean; every failure fixed forward; every pool manifest with a road carries `road_width`.
      research: procedure
- [ ] T06 [US2] **Gate + review** - the unlocked gate green; `make perf LABEL=144-end`, `make perf-report AGAINST=144-start`; `settlement-review` on Inashiro (background); commit; push (GATED route: engine delta, remote off -> LOCAL-GATED).
      research: procedure
