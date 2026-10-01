# 292 sweep vegetation G04 - handoff (session 1: write)

## Village fuel woods and their coppice (satoyama)

- SECTION=vegetation/village-fuel-woods-and-their-coppice-satoyama
- RENDERING=rendering/vegetation/how-our-maps-bound-and-draw-the-coppice-woods
- OLD=research/vegetation/220-where-did-a-village-keep-its-fuel-wood-beyond-its-fields-on-the-hill-ground-around-it---not-below-the-houses.html research/vegetation/140-how-is-a-coppice-lot-bounded-by-ridge-stream-and-path---never-by-a-page-axis.html research/vegetation/130-does-scrub-stand-under-a-village-wood-no---the-floor-was-worked-clear-grass-fringes-the-edge.html
- MODALS=WoodlandCommons
- BASE=fcea787ec

No other feature held these sections, so all three are folded. The brief listed no modals, but `WoodlandCommons`
(greenery.py) named all three old headings in its `Entry:`, so the Entry and the fixture now name the new research and
rendering titles (the 230 heading is unchanged). Cut under STYLE.md 4 (REMOVED comment): the three Sources rosters;
130's claim about the EUNIS factsheet's wording, from a page nobody could read (so the now-unused glossary term
`0100-EUNIS.json` is deleted); the GM's quoted questions and the answers to them, which now sit as comments beside the
rendering rules. Merged notes: 140's satoyama-enwiki-5 into -3 and -6 into -9. The absence note ijc-yamaguni-5 is now
in the new form, keyed by the section id on each page. Its visible text also says no page read describes a
rectangular coppice lot, which was 140's own claim. The rendering section has a bullet on a lot's line following a
brook, lane or field (woods W26, the 45 ft reach). The code already did this, but no folded section described it.
Links re-aimed in vegetation 060, towns 420 and 340 (whose "link it once 269 lands" comment is now a link). Code
comments in parcels.py and stages.py name vegetation/220 and the new title.
