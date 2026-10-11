# Feature Specification: What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)

**Status**: Superseded by 358 (2026-10-10): carried word for word into the one re-roll wave of map-moving review fixes (the GM, 2026-10-10: "Yes, please."). Was: Filed - from future-work/farming-communities.md, "What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

**Measured** (Sawada): the head race leaves the brook at `#6C9CBE` (128,167,191) - darker and more saturated than the
brook's own `#9CB4C8` (168,187,199) - and at 6.0 px against the brook's 7, so it is 86% of the trunk's width. At 9x the
dug ditch can read as the principal watercourse. The mouth half is done (269 B22: the race now opens out of the brook's
bank, research/contents.json#water 310, `hamletgen/water/brook.py` `open_race_mouth`); the width and the hue are what remain.
**Mechanism**: both widths are the water-width ladder's own figures, drawn by RANK rather than discharge, and the hues
are the supply/brook pair every map uses; changing either for this junction trades a junction-scale misread for a
map-scale one. **Sketch**: judge the new mouth at 9x in a settlement-review first; only if the race still reads as the
river, taper its first ~30 ft from the brook's hue to its own.

## The sketch's first step, measured (2026-10-11)

Judged on Sawada's mouth at (4575, 3455) as main draws it today (observed 2026-10-11; method: the pool SVG rendered at about
5 px per map unit around the tap, read by eye): the head race leaves the brook 6.0 px wide in the supply hue `#6C9CBE` against
the brook's 7 px in `#9CB4C8`, and at that zoom the dug race reads as the principal watercourse - the saturated band - while
the brook reads pale. So the sketch's condition ("only if the race still reads as the river") holds and its taper is owed.
It stays in 358's one re-roll wave, as the GM bundled it on 2026-10-10; the session asked the GM whether to build it alone.
