# Feature 291 - how many sides a homestead grove takes - the GM's request

The GM asked whether `homesteads/010`'s sentence "today wrapping the windward faces as a belt, where before 1868 it went
round the whole house" was meant as absolutely as written. The session reported that the full ring rests on one
region's report (Japanese Wikipedia's section on the Izumo plain's pine groves, tied to flood banks) and an ambiguous
1625 Takada order, while the record also holds the Sendai igune on the north and west "often lacking the south or the
east side" and planted that way under the first Sendai lord, the Tonami grove open on its east front, and the
Isawa, Iide, Hikawa and Okinawa groves on one or two sides; that no source counts farmsteads by grove shape; and that
the GM had ruled for the north-and-west hook on 2026-08-29 (`vegetation/030`). The GM, 2026-09-29:

> Yes, let's correct the record so that they cite the evidence correctly. And then because it does sound as if groves completely surrounding farmhouses was a thing, then that should indeed be a tunable knob. It seems like two sides is the minimum. Three sides would sometimes be the case, and all four sides would also sometimes be the case. So I don't know about the prevalence, and so I'm not really sure. how to set those numbers, but What do you think? Before we go forward, I guess whatever we do will be a guess, but if there's some random chance of it being a windbreak forest on two sides and some three sides and some four sides, then I don't know. Is that one third, one third, one third? Or something else? What do you think? Pitch me a suggestion before we make a decision.

The session pitched:

- Weights per settlement, rolled from the map's seed: two sides (the windward hook) 50%, three sides with the front
  open 30%, all four sides 20% - all three a GUESS, since no source counts farmsteads by grove shape.
- Rolled once per settlement, not per house (grove shape is regional custom).
- The windward side stays the heavy side: on three- and four-sided groves the deep stand is on the windward arms and
  a thinner band fills the rest (Tonami's pattern; for Izumo a GUESS).
- The open side of a three-sided grove is the front - the lee side, where the yard and entrance are.
- Optional: on a map whose farmsteads sit on flood-prone ground, the four-sided weight rises (say to 40%), from
  Izumo's flood-bank cause.
- The homestead grove only; the village-scale shelter belt stays on one or two sides.
- This reverses the GM's 2026-08-29 hook ruling; `vegetation/030` records the new ruling with the old one.

The GM, 2026-09-29:

> Your suggestions sound great, so yes, please go with all of that. Both the percentage split and the flood ground adjustment. Thanks.

The session then reported that no live pool hamlet draws a per-farmhouse grove at all - every scripted hamlet is
rolled nucleated, and the dispersed and linear forms (which carry the per-house grove) were switched off in feature
126 because the per-house grove path fails its checks (`hamletgen/consts.py`, `SETTLEMENT_FORMS`) - and asked how far
the feature should go. The GM chose "Knob + fix groves (Recommended)": correct the record, build the 2/3/4-sided knob
with the flood-ground adjustment, AND fix per-house grove placement so dispersed and linear hamlets (which carry
farmhouse groves) can be rolled again.

---

**2026-09-29, the GM, on the row village** (asked what a linear hamlet of grove farms should look like):

As is often the case with these things, the answer is always that what it should look like should be based on our research and not just something that you ask me. I mean, I don't know what these kinds of historical farming communities actually looked like. And the point of what we are doing in this project is to draw maps that reflect the historical norms for these types of settlements. So it would be inappropriate for me or for you to simply make an arbitrary decision. we should try to find out from our research what types of settlement layouts existed, and then have our settlements reflect the range of settlement layouts that we are able to find. And then, if our research is thin and we are straightforwardly unable to come up with an answer, then we make a tunable knob for the various possibilities which all seem reasonable by virtue of being in line with our other research and not contradicting anything that our research has already established.
