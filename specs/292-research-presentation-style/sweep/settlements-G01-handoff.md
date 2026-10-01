# Handoff - 292 sweep, settlements G01 (write)

## The five sizes of settlement: hamlet, village, town, provincial city and capital

- SECTION=settlements/the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital
- RENDERING=rendering/settlements/how-our-maps-draw-and-state-each-size-of-settlement
- OLD=research/settlements/010-what-are-the-five-kinds-of-settlement-and-how-big-is-each.html research/settlements/090-who-lives-in-a-provincial-city.html research/settlements/040-what-does-the-page-beside-a-map-say-about-its-size.html research/settlements/050-which-district-and-county-does-this-settlement-belong-to.html research/settlements/060-how-far-is-it-across-this-map-the-scale-tier-by-tier.html research/settlements/070-what-must-a-map-be-told-that-its-own-ground-cannot-settle.html research/settlements/080-when-is-a-settlement-allowed-to-break-a-rule.html research/archetypes/190-what-a-settlement-is-and-what-the-place-card-may-say-about-it.html
- MODALS=
- BASE=0a655a7f7

Nothing was left out: no claim held any of the eight sections in progress. The rendering section is the first on a new
page, `research/rendering/settlements/` (its `_front`, `_tail` and `_citations-*` fragments copied from
rendering/religion-and-death; `tests/interactive/test_citations.py` now counts 23 pages). No class's `Entry:` named a
folded section, but the place card's `"entry"` in `l7r/diagram/interactive/assets/place.json` named archetypes 190 and
now names both new titles - the card is written from it, so an `entry-drift`-style look at the card's `basis` sentence
against the rendering section's card bullets is owed. Cut, with REMOVED comments: the GM's inciting question from 190,
190's "came back mostly NEGATIVE" framing, 190's note `l7r-median-domain-3` (its two passages are `l7r-median-domain-8`
and `-2`), and the five `Sources:` rosters. Keys renamed: 190's `l7r-median-domain`, `-2`, `-4` are `-23`, `-24`, `-25`
on the research page (`-20` was taken by settlements 035); the rendering page cites `l7r-median-domain-23` for the same
table rows. Two canon statements still carry no footnote, as in the old sections: the provincial city's caste shares
(40/20/25/10/5) and that it counts no farmers (both from the setting's budget tables, `budgets.md` - lines 87 and
252-284 hold them, readable through `make canon`), and the hamlet's "one to three small fields". The absence note on a
historical household size (the one study, sagepub, 403) was converted to the new form. Links re-aimed: cities/fabric 240
(to the research section) and archetypes 250 (to the rendering section); code comments in hamletgen/consts.py,
citybudget.py, settlement/core.py, settlement/houses.py and settlement/rolling/roll.py. `specs/229-.../research.md`
still names the old anchors; it is a finished spec and was left alone.
