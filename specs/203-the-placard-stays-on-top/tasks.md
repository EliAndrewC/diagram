# Tasks - 203 The placard stays on top

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 1: fixing the mechanism rather than the GM's z-index hypothesis graded faithful to the request's purpose; the scale bar's marker compelled by the opaque card and within the 2026-08-29 ruling
- [x] T02 `finish.py` marks the scale bar (FR-002); `page.css` exempts the placard and the bar from
      raster mode's hiding (FR-001); the why at both points of change
      research: rendering
      verify: DONE. finish.py: the scale bar's group is `<g class="scale" ...>` with the why beside the ruling; page.css: the leaf rule gains `:not(g.f-place *):not(g.scale *)` with the why
- [x] T03 the browser test (FR-004) and the marker's unit test; SC-002 shown once
      research: rendering
      verify: DONE. tests/settlement/test_label_placement.py: the marker present once, no data-k, still cls='-' (16 passed); tests/full/interactive/page_browser/test_speed.py: the card's pixel is parchment and the bar's line pixel is ink with the scrub lit, before and after the card was lit and left, the leaves displayed with nothing lit (30 passed); feature 201's leaf count now excludes the placard. SC-002: with the exemption reverted the test failed (the card and the bar not displayed). Measured on the shipped page first: with the scrub lit the card's pixel went from (247,240,220) to (230,212,164) and 14 lit scrub paths crossed the card
- [x] T04 `make done` green; the page opened, the card hovered and left, the scrub lit (SC-003); land GATED
      research: rendering
      verify: DONE. make done green (3,029 passed, coverage 100%) - the first green-test run was refused by the duration ratchet (772 s over a 713 s ceiling), which found feature 200's WebP encode at 9.6 s per page write; at method 0 (2.2 s, +8% bytes, still lossless) the test phase fell 578 -> 466 s and the gate passed; the card hovered, left, the scrub lit on the regenerated page by the browser test; landing GATED (LOCAL-GATED)
