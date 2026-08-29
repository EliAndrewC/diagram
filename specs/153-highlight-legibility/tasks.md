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
- [x] **T11** (settlement-review error 2) the sluice's widened box lost to the field ditch's on 49 of 52
      sluices. `HIT_ON_TOP` lifts it into one layer above the ink; two wider designs measured and
      rejected (research R7). 42.4% -> 88.6% of its own box, worst 10.3% -> 75.8%. `research: rendering`
- [x] **T12** (settlement-review error 1) the perimeter dike's willow and mulberry rows now carry
      `Planted`, so the GM's own complaint is fixed on both dikes rather than one (research R8).
      `research: rendering`
- [x] **T13** (settlement-review, questionable 1) `pond sluice` <-> `sluice gate` - the near-homonym the
      GM's list did not name and the likeliest confusion on this map - is a sibling pair now.
      `research: rendering`
- [x] **T14** (settlement-review nitpicks 1-3) the four crop-dike sibling paragraphs share one constant;
      the walk figure is measured (815 ft median, 3.1 min) rather than "a minute"; `landuse.py` uses the
      absolute import its neighbors use. `research: rendering`
- [x] **T15** (settlement-review round 2, error 1) the lifted sluice layer swallowed a pig sty (88.4% of
      its footprint) and a duck pen (42.8%) - it broke the rule its own docstring states. `HIT_KEEP_CLEAR`
      clips the layer against every recorded structure; each is back to its main-branch share and the
      sluice keeps 88.3% (research R7). `research: rendering`
- [x] **T16** (settlement-review round 2, error 2 + questionables) the perimeter-dike walk figure was a
      double count - the manifest's `outline` is the band polygon, 1.99x the `crest` it should be keyed
      on - so "half an hour" is "the better part of twenty" (4,591 ft at 260 ft/min); the raster record
      corrected to 45,564 px / max 3 with the browser-identical finding; both sluice measurement
      definitions recorded; `HIT_PRIORITY`'s fallback no longer ranks a forgotten lifted class weakest.
      `research: rendering`
