# `future-work/` - deferred engineering, split by what kind of map it is about

**Load ONE file: the one for the map type you are working on.**

| file | load it when | size |
|---|---|---|
| [`farming-communities.md`](farming-communities.md) | working on hamlets or villages - paddy fabric, lanes, homesteads, wells, woodland, the notice board, and the village tier's conversion | the live work |
| [`towns.md`](towns.md) | working on a town - storefronts, inns, caravans, the theater, and what the town tier's conversion owes | thin; the tier is unconverted |
| [`cities.md`](cities.md) | working on a provincial city or a capital - walls, gates, wards, streets, the castle | small |
| [`compounds.md`](compounds.md) | working on a Mode A compound plan - magistracies, and the estate/mansion types still to be built | small |
| [`cross-cutting.md`](cross-cutting.md) | the thing you are fixing would change more than one kind of map, or no map at all (the gate, the caches, module structure) | small |
| [`closed.md`](closed.md) | you want to know whether something was SETTLED or merely forgotten | a one-line ledger |

## The rules that keep this from rotting

1. **An entry is OPEN WORK.** Not history, not a lesson, not a decision record. Closed items go to
   `closed.md`; method lessons - dead ends, wrong claims, the shapes failures take - go to
   [`../dev/lessons.md`](../dev/lessons.md).
2. **Close it in the same commit that closes the work.** A settled question still reading as OPEN gets put to the GM
   a second time, which costs them a decision they had already made.
3. **Each entry names the pain, the evidence, and a sketch of the fix.** An entry without a
   measurement is a feeling, and this project's own history says a feeling is usually wrong about
   which fix will work.
4. **Not a second copy of what a tool already lists.** A drift between the engine (or a Mode A procedure) and the
   research is `make claims-report`'s; a guess or silence the record labels is `make open-questions`'. An entry
   here is work neither carries - a defect the claims do not state, a sheet check, an unlabeled research question,
   a tooling gap, or what a tier's conversion owes.
5. **Check the era before you act on an old entry.** Much of the city material predates scripted
   generation and assumes a next hand-authored map. There will not be one: the 18 hand-authored maps
   are FROZEN and conversion is the answer for every tier above hamlet
   ([`../docs/migration-plan.md`](../docs/migration-plan.md)). Those entries are annotated - the task is dead,
   the insight is an input to that tier's conversion.

**The division is guesswork - reorganize freely** (GM 2026-08-24: *"right now, we have divided based on largely
guesswork."*). Code comments, notes and tests cite entries by TITLE (`git grep -n "future-work"`), so a moved or closed
entry keeps its title in its new file or in `closed.md`, and a pointer that names a FILE is re-aimed in the same commit.
