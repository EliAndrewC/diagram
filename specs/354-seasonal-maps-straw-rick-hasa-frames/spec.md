# Feature Specification: DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames, the drained paddies

**Status**: Filed - from future-work/farming-communities.md, "DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames, the drained paddies", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: now

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

The straw rick (waraguro, built round a pole after the harvest and kept to spring - Sugiura counts
a straw SHED on 0.68 of households) and the hasa drying frames in the fields are HARVEST-SEASON
features, so the GM ruled them out of the current phase: *"the straw shed, I think we should omit if
it is something that would only appear during the harvest time. That is something that we can put
under future work where, in general, we want the ability to have seasonal maps ... Seasonal maps will
require a number of changes as well because things like rice paddies being drained and then used for
other crops in the off season are also the kind of thing that we would need to do on some maps, but
not others."* Sketch when it comes: a `season` knob on the spec (spring / summer / harvest / winter)
read by the field renderer (flooded vs drained vs winter crop), by a `farmstead_fixtures` row for the
rick (harvest and winter only, at the yard's edge) and by a hasa pass in the fields; the checks that
read `meta.farm_fixtures` already carry the declaration shape. The research is now recorded (269 B05): the
winter barley on a drained paddy and the rick on the reaped paddy or its bund (research/contents.json#fields); the GM's deferral
stands, so nothing is drawn.
