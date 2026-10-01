# 292 sweep - ways G01 handoff (write)

## Village lanes

- SECTION=ways/village-lanes
- RENDERING=rendering/ways/how-our-maps-draw-village-lanes
- OLD=research/ways/020-what-vehicle-used-a-village-lane-and-how-wide-was-it.html research/ways/100-what-was-a-village-lane-surfaced-with-and-does-it-show-bare-trodden-earth.html research/ways/025-where-could-a-village-lane-run.html research/homesteads/080-is-every-farmhouse-reached-by-a-lane-and-in-what-form.html research/homesteads/090-how-does-a-village-lane-bend.html research/homesteads/310-how-far-does-a-village-lane-run-past-its-last-farmhouse.html
- MODALS=VillageLane Farmhouse ApproachRoad CartYard
- BASE=efbd6eb95

No folded section was held by another feature. The rendering page `rendering/ways` is new (its `_front`, `_tail` and
`_citations-*` scaffolding copied from `rendering/water`); `tests/interactive/test_citations.py` now counts 36 pages, and
`test_page.py`'s farmhouse-entry expectation follows the lane entry to the ways page. Cut under STYLE.md 4 (REMOVED
comment in the fragment): homesteads 080's paraphrase of an unnamed, unread "nucleated-village morphology literature"
(the gridiron as the most efficient compact form, every house reached through it, "what compactness is FOR") and the
second absence note on that same passage; what readable pages show (the surveyed Manchu village's blind alleys, the
Shanghai lane housing) stands in its place, with the silence noted. `mlit-tokaido-michi-3` (020) and `mlit-tokaido-michi`
(100) quoted the same passage and are one note. Every absence note was converted to the new form and renamed
`village-lanes[-N]` / `how-our-maps-draw-village-lanes[-N]`; the Manchu note's two Chinese terms gained their
`(romaji, "meaning")` glosses. ApproachRoad and CartYard named a title that no longer existed ("What vehicle used a
village lane, and where could the lane run?"); both now name 'Village lanes'. The cart evidence stays in this section;
the later moving-goods topic (ways 060, T4) links to `#village-lanes` already. Code comments naming homesteads/310 now
name rendering/ways/020.
