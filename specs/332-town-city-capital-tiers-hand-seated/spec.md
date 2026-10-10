# Feature Specification: The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8)

**Status**: Filed - from future-work/cities.md, "The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

Feature 266 built ONE caption placer (`l7r/diagram/labels/`, the cartographic standard: ranked positions, a
consistent gap, free space first, leaders) and routed every caption a live map draws through it. The unscripted tiers
still carry 47 hand-seated `self.label(x, y, ...)` calls in 33 functions - a ministry's name written across its roof,
a hall caption a fixed drop below it - which no live generator runs; the maps that used them are frozen exhibits.
`tests/labels/test_caption_paths.py` lists them by file and function (`D8_HAND_SEATS`) and fails on any NEW hand
seat. **When a tier is scripted**, each of its captions names its SUBJECT instead: `self._captions.append(...)` via
`place_caption(text, box, rot=...)` for a feature beside which it stands, an area subject for a name that lies on its
building or district (`Subject("area", ...)` through `_draw_seated_caption`), and a civic building's own caption with
`Subject(civic=True)` so it keeps off the other named civic buildings (spec FR-014). Delete the row from
`D8_HAND_SEATS` as each goes. The town and city cover rule (research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html) is already in the weights.
