# Feature Specification: OPEN 2026-09-27: the village generator draws no shrine grove, sacred tree or basin

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-27, OWED AT CONVERSION: the village generator draws no shrine grove, sacred tree or basin", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: village

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

Feature 268 (the GM, 2026-09-27: "Add grove to map") put a grove, a roped sacred tree and a stone basin round
Hoshigaoka's shrine by hand, and the country-shrine program now says a village shrine's precinct holds its
grove, in the form its ground gives (research religion-and-death 124, 126, 129). No generator draws them: `rolling/roll.py`'s civic shrine lays the
hall, its arches at the 12 ft pitch and its well, nothing more. So converting Hoshigaoka (or any village) drops
them. Sketch: after `shrine_hall`, reserve a precinct outline from behind the shrine well to the outermost arch
(the register band of research 124 as its area), carve the clearing and the approach, then lay the WOOD in the
form of the program's knob 8, `grove form` (feature 279, research 129): read the hall's ground - at the foot of a
slope the candidates are `behind` / `behind and sides`, at the top with the approach climbing to it
`behind and sides` / `sides`, midway on an even slope all three slope forms, on a rise or flat paddy `all around` -
and roll between the candidates from the settlement's seed with equal weights; the wood's region is a smooth-noise outline about the form's base shape,
never a ruled box (the edge is its crowns' own where it meets scrub or slope; where a paddy-plain wood meets its
fields, its foot rolls the program's second grove knob - `field line` along the fields' straight edge, as a
photograph shows, or `ragged` - with equal weights). Fill the
region with the grove scatter the windbreak already uses (a `KeepoutGrid` of the clearing, the approach and the
well), carry the scrub into the precinct's open ground, then seat the sacred tree beside the approach and the
basin at the innermost arch, and the keeper's kitchen garden (a `gardens` entry) on the open ground nearest the
dwelling that gets its six hours (feature 283, `garden_sun`'s sun; Hoshigaoka's sheet draws it below the forecourt,
west of the approach). Measure: the region's area and canopy share, and feature 279's `STRAIGHT_RUN` on its
edge crowns (no four within 2 ft of one line), against the hand-drawn Hoshigaoka grove (form `behind and sides`, feature 279), and the `LONG_RUN` bar (no
stretch of edge 50 ft or longer within a crown's radius of one line).
