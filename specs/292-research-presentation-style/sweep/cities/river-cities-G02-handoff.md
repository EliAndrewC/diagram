# 292 sweep cities/river-cities G02 - handoff

## Water gates and sluices (shuimen)

- SECTION=cities/river-cities/water-gates-and-sluices-shuimen
- RENDERING=rendering/cities/river-cities/how-our-maps-draw-water-gates-and-sluices-shuimen
- OLD=research/contents.json#river-cities research/contents.json#capitals research/contents.json#capitals
- MODALS=GranaryStilts RiverLanding Revetment

- BASE=875bb35d2

No section was held by another feature, so all three folded. 280's quay-side kura and boat-length jetty paragraphs were already told at 0142 (sweep capitals G07), so here they were dropped with 280. The three modals whose `Entry:` named "The sluice's lifting frame" (GranaryStilts in compound_kinds/office.py, RiverLanding and Revetment in compound_kinds/particulars.py) were written from those kura paragraphs, so their `Entry:` now names 'Rice storehouses and the rice brokers in a capital (kura, fudasashi)', not this topic. Their prose still says a raised floor and a stone revetment "answered flood" at Edo's rice stores, which capitals 090 now gives as on no page read, so `_entry_owed` may flag them for entry-drift (none is in the fixture). Cut, each named in the REMOVED comment: 110's "the one complete example" and "closed ... in war" (no quoted passage), the pointer paragraph, the GM framing of 280 and 310, and 280's stray `data-fn="134"` span. The OPEN question from the defenses check stays open and is carried as a comment beside the width rule: the defenses rendering opens 60 ft of wall for a 36 ft canal, while this rule draws the passage as wide as its canal. The glossary term "duty cycle" was deleted, since no page or modal used it after 310 was folded; "suimon" is now used in the research prose. Confusable pairs appended: this topic against the defenses city gates topic (T3), against city canals (re-titled), and against "What keeps the moat full?".
