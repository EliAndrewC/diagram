# The GM's request, verbatim

Captured BEFORE `spec.md` (constitution XVI). Nothing here is edited.

## 2026-08-28, accepting feature 145 and opening this one

> Sounds great. I accept. So please merge your work back into the main checkout. Then open a separate feature for the residue in three named classes. Instead of having the biggest one as its own feature, go ahead and make a single feature for all three of them. After your existing work is merged into the main checkout, then please begin that feature and take it to completion and then merge it in as well without needing any acceptance from me. I think I'm still a little bit unclear on whether the floor being red on that three hundred and seventy four line residue. is captured by this new feature. or not. If it is not, then please include that as separate tasks within the same feature so that by the time your next round of work makes its way back into main, then the floor will no longer be red. Please proceed with that. Thank you.

**The session's answer to the GM's question, for the record**: the floor's red state IS the residue -
the 373 lines the hamlet floor reports are exactly the three classes, with nothing else in them. So
closing the three classes is what turns the floor green, and this feature's closing task is a GREEN
floor rather than a separate errand. Every number in the classes is measured; see feature 145's
`research.md` R3b/R3c/R3e and the table in this feature's `research.md` R1.

**The three named classes** (145's words, quoted so this feature is judged against them):

1. *"56 lines are the dike-pond check waiting on a scripted mulberry map"* - `dikepond_is_ponds_in_a_block`,
   guarded on `meta.field_archetype == "mulberry_dike_fishpond"`, which no scripted map rolls yet.
2. *"~200 are check FAILURE branches no map trips - the scripted-negative-fixture half of feature 141"* -
   the body of a check that runs only when a map is wrong.
3. *"~120 are placer refusal branches and never-needed fallbacks"* - one `return True` per reason a seat
   is refused, plus fallbacks like `_thread_the_fabric`'s shortened track and `_smooth_web`'s rollback.

**No acceptance is required for this feature** (the GM, above): it lands on main when it is done and green.
