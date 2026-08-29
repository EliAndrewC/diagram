# Tasks: five things about highlighting

**Feature**: 153-highlight-legibility | **Plan**: [plan.md](plan.md)

Every task here is `research: rendering` - all five are map/modal conventions about how a page
HIGHLIGHTS and what a modal says. None of them is a claim about how a place was built, farmed or
lived in: the sluice, the dike, the crowns and the windbreak are all already researched, placed and
drawn, and nothing about their form, size, position or existence changes.

- [x] **T01** `HIT_WIDEN["pond sluice"]` with the ditch's factors, and the GM's words at the point of
      change. `research: rendering`
- [x] **T02** `Planted(str)` in `tags.py`, in `ClsTag`, with the docstring saying why it is a `str`
      subclass. `research: rendering`
- [x] **T03** `_open(key, planted=False)` emits the `planted` token; `wrap()` passes
      `isinstance(tag, Planted)`. `research: rendering`
- [x] **T04** `--hl-planted` / `--hl-planted-stroke` and the two `g.f.on.planted` rules in `page.css`,
      after the global highlight rules. `research: rendering`
- [x] **T05** `landuse.py` tags the crowns `Planted(DIKE_CROP_CLASS[crop])`. `research: rendering`
- [x] **T06** the five `_PAIRS` rows: sluice <-> ditch, and each crop dike <-> perimeter dike.
      `research: rendering`
- [x] **T07** `windbreak`'s `name="windbreak forest"`; relax the name==key invariant in
      `tests/interactive/test_classes.py` to name-contains-key, with the reason at the assertion.
      `research: rendering`
- [x] **T08** tests: the sluice row is applied to real sluice ink; a `Planted` tag emits `planted` and a
      plain tag does not; the five pairs are installed both ways; the windbreak name.
      `research: rendering`
- [x] **T09** regenerate the dike-pond pool maps, re-run the feature-148 page-vs-SVG check, `make done`
      green, `settlement-review` on the changed map. `research: rendering`
- [x] **T10** (defect found in T09, constitution XIV) the merge pass was drawing outlined shapes in the
      wrong order - Kuwabata's woodland as glass rings, the page 0.255% of pixels from its own PNG.
      Fixed in `merge_primitives`, with the element cost measured at each step and the remaining
      antialiasing residual accepted and recorded (research R5, R6). `research: rendering`
