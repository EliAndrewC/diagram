# Feature Specification: the season a hamlet's fields show, rolled per map

**Status**: Filed - from feature 325's ruling R1, 2026-10-08

**Affects**: all settlements

**Input**: the GM's ruling on feature 325 R1 (2026-10-08, verbatim): *"For feature 325 the answer is "spring / summer /
autumn" i.e. when there is planting."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this
directory); until then `make speckit-todo` lists it as filed.

## The ruling, and what it changes

Today each dry-field crop - millet, buckwheat, barley, soy - is drawn in its own ripest color, so barley shows the gold
of its May harvest beside crops of high summer on one sheet (the question as filed: `specs/325-gm-rulings-from-319/rulings.md`
R1). The GM chose option (c): a season knob rolled per map from the map's seed, over the three seasons when fields are
planted - spring, summer, autumn - and every crop drawn as it stands in the rolled season (a crop not yet sown, growing,
ripe, or stubble after its harvest), the paddy included.

- The field-crop research pages give each crop's season and color; a crop the record does not date is a research
  question first (constitution XII), never a guess written straight into the knob.
- The knob is told on the map's title card and in the field-crop modals' Depiction tabs, which today say the colors
  and the real seasons without calling the ripest-color drawing deliberate (feature 319).
- Related: feature 354 (`specs/354-seasonal-maps-straw-rick-hasa-frames/`), the harvest-season features (the straw rick,
  the hasa frames, the drained paddies) - with a season rolled, those become drawable in the season they belong to.

## Carried: the harvest-season features

Carried word for word on 2026-10-10 (the GM, 2026-10-10: "Yes, please.", on the session's proposal to merge them); each old feature reads `Superseded by 369`.

### 354 - DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames, the drained paddies

**Status**: Filed - from future-work/farming-communities.md, "DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames, the drained paddies", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: all settlements

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

