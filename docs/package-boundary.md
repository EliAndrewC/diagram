# One package, two modes: why buildings and settlements are NOT split

**Load this file when:** You are wondering whether Mode A (building plans) and Mode B (settlement
maps) should be split into two packages, you are adding a new Mode A building type, or a Mode A
generator is starting to appear.

**Decided 2026-08-27, by the GM, on the session's recommendation.** Docs-only decision, no code. (It
was asked as "two skills or one" while the project was a Claude Code skill; since feature 329 the
project is a repository with one package, `l7r.diagram`, and the same question is asked of packages.)

## The question

The magistracy diagrams are a success, and the GM asked whether building plans should stay with
settlement maps - or become a `buildings` / `compound` project beside a `maps` one, with `diagram`
kept as the repository name because a map is a type of diagram. The question was asked knowing that
the `l7r` namespace package already allows submodules in different locations, so a code split is
cheap whenever it is wanted. The GM also asked whether the answer changes when more hand-authored
Mode A types are added - samurai city estates and country estates are planned next, drawn the way
magistracies are: hand-authored from a template, validated by automated checks and the review
agents, not scripted.

## The decision: keep one package

Three findings drove it, in order of weight:

1. **The two modes share machinery.** As decided, the shared code ran from buildings INTO
   settlements: `l7r/diagram/compound.py` was imported by `citybudget.py` and by eight
   `check_village` segments. **Re-checked 2026-10-07 (feature 329): that dependency is gone.**
   `check_village` was retired by feature 166, `citybudget.py` no longer imports `compound`, and the
   settlement engine imports none of `compound.py`, `compound_model.py` or `compound_parts.py` (their
   importers are each other, the two magistracy gens whose svg the placer writes -
   `county-magistracy-example` and `ochiba-roundtrip-test` - the tests, and `pipeline/gencache.py`,
   which names `compound` among the engine imports it keys the cache on). What the modes share now
   is common infrastructure both import: the one caption placer (`l7r/diagram/labels/`, feature 266,
   used by the settlement engine, `compound.py` and the hand-drawn sheets), the interactive page
   (`l7r/diagram/interactive/`, with a Mode A kind registry beside the Mode B classes), the render
   cache and pool index (`l7r/diagram/pipeline/`), and the sheet-follows-its-map rule (a Mode A
   sheet of a place a settlement map draws is checked against that map's manifest -
   `tools/pack_audit/mapmatch.py`, feature 257). A split would put that infrastructure in a third
   package both depend on; it would not separate the two.
2. **The documentary split already exists.** `docs/usage.md` is the shared usage document (scale
   ladder, labeling, rendering, pool layout, the `make` ladder); `docs/buildings.md` holds the
   Mode A conventions and indexes `buildings/`, each topic file stating when to load it; the Mode B
   record is the research pages. The cost the GM actually feels - "I have to say which part I am
   working on" - is one word per request, and a second package would cost the same word.
3. **The asymmetry argues AGAINST splitting.** Mode B is a parametric engine with a scripted hamlet
   generator, a frozen legacy pool, CodeBuild, perf bookends and the gate. Mode A is a handful of
   hand-drawn sheets, one draft placer, one geometry audit (`tools/pack_audit/`) and its review
   agents (`building-review`, `size-audit`). A separate buildings project would be a small one owning
   a large repository's process (spec-kit for every engine change, the gate, the switches). Today
   Mode A borrows that machinery without having to carry it.

## More hand-authored types do NOT change this

Adding estates (or temples, keeps, battlefields) the way magistracies are done means, per type: a
declaration in `l7r/diagram/buildings/types.json` and its program in `docs/buildings/programs.md`,
a few checks in `tools/pack_audit/` and rows in `size-audit`'s anchor table, a pool directory with
its `.svg` and `.notes.md`, and the same review agents before it ships ([`docs/buildings.md`](buildings.md),
"Adding a building type"). That grows `buildings/` without touching the boundary. And every new
Mode A type is ALSO a feature a settlement map may draw (a city estate stands on a provincial-city
map; a country estate on a village or town), and its sheet then follows that map. Building COUNT is
not the trigger.

## The prediction: what WOULD change it, and what to do then

**The trigger is a Mode A GENERATOR, not a Mode A count.** A Mode A sheet's `.gen.py` today renders
the hand-drawn svg, and `compound.py` writes a DRAFT that is then refined by hand (its two exemplars
excepted). The trigger is the day drawing a building type feels like "given knobs X, Y, Z, lay out
the estate" every run, the way `hamletgen` lays out a hamlet - Mode A then acquires its own knobs,
cohorts, manifests and checks, and starts wanting its own perf bookends and gate phases.

When that happens, split the CODE first: `l7r.diagram.compound` (and the new generator) -> its own
package under the `l7r` namespace, e.g. `l7r.buildings`, with the shared infrastructure (finding 1)
staying where both import it. The namespace-package work was done for exactly this, so the move is
cheap and it tells you whether the boundary is real: if the import graph stays one-directional it
is; if settlements and buildings start importing each other, it was not, and the split is undone at
the same price. Move the documentation with the code, never before it.

**Names, if it ever comes to that** (decided now so the question is not reopened): the repository
stays `diagram` - the genus, of which a map is one species. The building package would be
`buildings`, not `compound` (a compound is one building type among temples, keeps and
battlefields). The map package would be `settlements`, not `maps` - the project already says "Mode
B settlement map" and `settlement-review` everywhere. Nothing is renamed today.
