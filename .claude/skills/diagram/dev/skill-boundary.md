# One skill, two modes: why buildings and settlements are NOT separate skills

**Load this file when:** You are wondering whether Mode A (building plans) and Mode B (settlement
maps) should be split into two skills or two packages, you are adding a new Mode A building type,
or a Mode A generator is starting to appear.

**Decided 2026-08-27, by the GM, on the session's recommendation.** Docs-only decision, no code.

## The question

The magistracy diagrams are a success, and the GM asked whether building plans should stay in the
same skill as settlement maps - or become a `buildings` / `compound` skill beside a `maps` skill,
with `diagram` kept as the repository name because a map is a type of diagram. The question was
asked knowing that the `l7r` namespace package already allows submodules in different locations,
so a code split is cheap whenever it is wanted. The GM also asked whether the answer changes when
more hand-authored Mode A types are added - samurai city estates and country estates are planned
next, drawn the way magistracies are: hand-authored from a template, validated by automated checks
and the review agents, not scripted.

## The decision: keep one skill, one package

Three findings drove it, in order of weight:

1. **The shared code runs in ONE direction, from buildings INTO settlements.**
   `l7r/diagram/compound.py` (the Mode A compound placer, ~400 lines) is imported by
   `citybudget.py` and by eight `check_village` segments - because a magistracy, a temple compound
   or an estate STANDS ON a settlement map, and the settlement validator sizes and checks it from
   the same building-program data (`segments_10d_city_temples_and_estates.py` is that dependency
   by name). A skill split puts the program definition on one side of a fence and its largest
   consumer on the other. The moment `settlements` imports `buildings`, that is a package
   boundary, not a skill boundary - and it is the boundary we already have.
2. **The documentary split already exists.** `SKILL.md` is the shared index (palette, scale ladder,
   render pipeline, pool layout, the regression-fixture and review-agent doctrine, the `make`
   ladder); `buildings.md` and `settlements.md` are separate indexes over `buildings/` and
   `settlements/`, each topic file stating when to load it. The cost the GM actually feels - "I
   have to say which part of the skill I am working on" - is one word per request, and a second
   skill would cost the same word.
3. **The asymmetry argues AGAINST splitting.** Mode B is a 28-generator parametric engine with a
   ~1,371-segment validator, CodeBuild, perf bookends and scope switches. Mode A is ~29
   hand-authored SVGs, one placer, one geometry audit (`tools/pack_audit.py`) and three review
   agents. A `buildings` skill would be a small skill owning a large repository's process
   (spec-kit for every engine change, the gate, the switches). Today Mode A borrows that machinery
   without having to carry it.

## More hand-authored types do NOT change this

Adding estates (or temples, keeps, battlefields) the way magistracies are done means, per type: a
program entry in `buildings/programs.md`, a few checks in `pack_audit.py` and rows in
`size-audit`'s anchor table, a pool directory with the `.svg/.png/.notes.md` triplet, and the same
review agents before it ships. That grows `buildings/` the way `settlements/` grew from one file to
thirteen - which `SKILL.md` already anticipates ("add `temples/`, `keeps/`, etc. as they appear").
It does not touch the boundary. And every new Mode A type is ALSO a new Mode B glyph with a shared
program (a city estate stands on a provincial-city map; a country estate on a village or town), so
each addition strengthens finding 1 rather than weakening it. Building COUNT is not the trigger.

## The prediction: what WOULD change it, and what to do then

**The trigger is a Mode A GENERATOR, not a Mode A count.** The day drawing a building type feels
like "given knobs X, Y, Z, lay out the estate" rather than hand-authoring from
`pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg` - concretely, the day a `.gen.py` appears in a Mode A
pool directory the way `hamletgen` appeared for hamlets - Mode A acquires its own knobs, cohorts,
manifests and checks, and starts wanting its own scope lock, perf bookends and gate phases.

When that happens, split in THIS order:

1. **Split the CODE first**: `l7r.diagram.compound` (and the new generator) -> its own package
   under the `l7r` namespace, e.g. `l7r.buildings`, with `l7r.diagram.check_village` importing it.
   The namespace-package work was done for exactly this, so the move is cheap and it tells you
   whether the boundary is real: if the import graph stays one-directional it is; if settlements
   and buildings start importing each other, it was not, and the split is undone at the same
   price.
2. **Let the skill follow the package**, if it still seems worth it. `buildings.md` is already a
   self-contained index, so promoting it to a skill is near-zero cost once the code is separate.
   Splitting the skill BEFORE the code is the wrong order - it moves the documentation away from the
   code it documents while the code stays shared.

**Names, if it ever comes to that** (decided now so the question is not reopened): the repository
stays `diagram` - the genus, of which a map is one species. The building skill would be
`buildings`, not `compound` (a compound is one building type among temples, keeps and
battlefields). The map skill would be `settlements`, not `maps` - the project already says "Mode
B settlement map" and `settlement-review` everywhere. Nothing is renamed today.

## Alternatives declined

- **Two skills now, sharing the package.** Declined: the shared surface (style, scale, render,
  pool, review doctrine, `make`) would be duplicated or one skill would document the other's
  code.
- **Rename the skill to `buildings` and start a separate `maps` skill.** Declined for the
  ordering reason above and because the invocation `/diagram` and the mode-named agents already
  disambiguate.
- **Rename now in anticipation.** Declined: a rename before the trigger costs a session and buys
  nothing until a generator exists.
