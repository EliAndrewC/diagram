# `future-work/` - deferred engineering, split by what kind of map it is about

**Load ONE file: the one for the map type you are working on.** That is the whole point of the
split. This directory replaced a single 3,453-line `future-work.md` on 2026-08-24 at the GM's
direction, because a session planning hamlet work was loading the capital-era backlog to find it,
and a human auditing the list had to sift a changelog to see what was actually outstanding.

| file | load it when | size |
|---|---|---|
| [`farming-communities.md`](farming-communities.md) | working on hamlets or villages - paddy fabric, lanes, homesteads, wells, woodland, the notice board, and the village tier's conversion | the live work |
| [`towns.md`](towns.md) | working on a town - storefronts, inns, caravans, the theater | thin; the tier is unconverted |
| [`cities.md`](cities.md) | working on a provincial city or a capital - walls, gates, wards, streets, the castle | small |
| [`compounds.md`](compounds.md) | working on a Mode A compound plan - magistracies, and the estate/mansion types still to be built | small |
| [`cross-cutting.md`](cross-cutting.md) | the thing you are fixing would change more than one kind of map, or no map at all (the gate, the caches, module structure) | small |
| [`closed.md`](closed.md) | you want to know whether something was SETTLED or merely forgotten | a one-line ledger |

## Why these groupings and not others

**Hamlets and villages share a file** (GM 2026-08-24). A village is a hamlet with a headman, a shrine
and tax-free plots - not a different kind of place - and its defects are the same defects.

**Provincial cities and capitals share a file** for the same reason: they are largely scaled versions
of one another.

**Towns have their own file.** They were folded in with cities in the first cut of this split and
pulled out the same day (GM 2026-08-24): a town has storefronts, inns, caravans and a theater that a
farming community does not, and a farmers plurality and no wall-and-ward apparatus that a provincial
city does. It is thin today because the town tier is unconverted, not because towns are in good
shape.

**Compounds are Mode A** - a walled compound drawn as an interior plan rather than a settlement in
its fields. Only magistracies exist today; samurai city estates, governor's mansions, samurai country
estates and keeps are coming.

## The rules that keep this from rotting back into what it was

1. **An entry is OPEN WORK.** Not history, not a lesson, not a decision record. Closed items go to
   `closed.md`; method lessons - dead ends, wrong claims, the shapes failures take - go to
   [`../dev/lessons.md`](../dev/lessons.md).
2. **Close it in the same commit that closes the work.** The audit found two settled questions still
   reading as OPEN, one for five days and one for seven, both about to be put to the GM a second
   time. That is the specific failure this rule prevents, and it costs the GM a decision they had
   already made.
3. **Each entry names the pain, the evidence, and a sketch of the fix.** An entry without a
   measurement is a feeling, and this project's own history says a feeling is usually wrong about
   which fix will work.
4. **Not a second copy of what a tool already lists.** A drift between the engine (or a Mode A procedure) and the
   research is `make claims-report`'s; a guess or silence the record labels is `make open-questions`'. An entry
   here is work neither carries - a defect the claims do not state, a sheet check, an unlabeled research question,
   a tooling gap, or what a tier's conversion owes. The 2026-10-07 audit removed ~3,000 lines that were done,
   about code or checks since deleted, or already tracked by one of those two.
5. **Check the era before you act on an old entry.** Much of the city material predates scripted
   generation and assumes a next hand-authored map. There will not be one: the 18 hand-authored maps
   are FROZEN and conversion is the answer for every tier above hamlet
   ([`../docs/migration-plan.md`](../docs/migration-plan.md)). Those entries are annotated - the task is dead,
   the insight is an input to that tier's conversion.


## THIS DIVISION IS LARGELY GUESSWORK - expect to reorganize it

**GM 2026-08-24: *"right now, we have divided based on largely guesswork."*** That is an accurate
description and it is written here so no later session mistakes these boundaries for a designed
taxonomy.

What the split actually rests on:

- The categories were chosen from the map types we generate TODAY plus the ones we know are coming.
  Four of the six tiers are unconverted, so most of them have no live work to organize.
- Sections were assigned by scanning each one's body for keywords and then hand-correcting the ones
  that followed a provenance rather than a subject. That is a decent first pass, not a classification
  anyone would defend line by line.
- Towns moved between files within a day, which is the honest illustration: the first answer was
  wrong and the cost of fixing it was five minutes.

**So reorganize freely.** Moving a section between these files is cheap and requires no migration. Code comments,
notes and tests do cite entries by TITLE (`git grep -n "future-work"`), so a moved or closed entry keeps its title in
its new file or in `closed.md`, and a pointer that names a FILE is re-aimed in the same commit. The signals
worth acting on:

- **A file nobody loads for its own tier.** If hamlet work never opens `cross-cutting.md`, the split
  is wrong or that file's contents are misfiled.
- **A section that keeps getting read from the wrong file** - the town material was found by grepping
  `cities.md`, which is the symptom that preceded the split.
- **`farming-communities.md` grows fastest** because it is where the live work is. When it becomes the thing you
  scroll rather than read, first close what is done (rule 2), then split it by subject - the water/paddy fabric, the
  way network, homesteads and their appurtenances - rather than by tier, because the tier is already the filename.

The one thing NOT to do is leave a section in the wrong file because moving it feels like churn. This
directory exists to be read under time pressure; a misfiled entry costs more every time it is missed
than the move costs once.
