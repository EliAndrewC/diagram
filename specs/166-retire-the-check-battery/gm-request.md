# The GM's request, verbatim

**Renumbered 164 -> 166 within minutes of the claim.** Two peer sessions had taken 164 and 165 while this
one was working, and the sync-in that should have surfaced them reported "Already up to date" because they
landed between it and the commit. The claim protocol (CLAUDE.md, "spec numbers are CLAIMED IN MAIN") says
to renumber rather than negotiate, which is what happened - the duplicate 164 existed on main for one push
and was corrected in the next.

Captured BEFORE `spec.md` is written (constitution XVI). Nothing here is edited. This feature is the
CONCLUSION of feature 163: 163 asked which checks still fire and retired the dead ones; this one acts on
the answer 163's own ledger forced, which is that the post-placement battery should not exist at all.

## 2026-08-30, after reading feature 163's ledger

The session had reported 11 checks as "placer bug", 116 as "fold into a trial-and-error placer", and had
flagged that 75% of the fold group's evidence rested on the single `finish` stage.

> Yeah. I was going to say, I'd be really, really surprised if our win is actually only eleven checks. I mean, most of what you're describing and what I'm seeing does sound like it could just be deleted. Even moving canopies doesn't sound like something that an automated check should be doing. Because if a canopy is in the wrong place, that definitionally means that a placer put it in the wrong place. And that means that the placer algorithm needs to be fixed. Right? Like, based on what you're saying, it sounds like the actual outcome is that all automated checks can be deleted. What am I missing? I mean, now that you have looked at the automated checks, can you describe to me a single category of automated check? which should still exist?

The session measured the question rather than arguing it: **116 of the 116 "fold" checks have a NAMED
last-touching stage; zero are ownerless.** So the bucket's justification - *"no unit test of the placer can
carry the guarantee"* - was false: the placer the session had NAMED could not, but the stage that last
writes the feature can, and that stage is a placer. The session could name no category of post-placement
per-map check that should survive, and said so.

## 2026-08-30, the instruction

> Okay. Sounds good. Go ahead and implement that. Get rid of check village, and I guess the same thing will later apply to other similar automated checks for towns and provincial cities and capital cities when we eventually begin to script those as well. As things stand now, I believe that check village is performed for both hamlets and villages, and, therefore, this is the one that we will get rid of now. Right?

**One premise in that last sentence is factually wrong, and the session corrected it before starting** (the
correction is what makes this feature bigger than the GM was picturing, so it is recorded here rather than
buried): `check_village` is not the hamlet/village checker - it is the ONLY Mode B checker, for every tier.
Measured: **307 of its 353 segments carry no scale guard at all** and run at every scale; 9 are
city/capital-only; 2 are town-and-up. There is no separate town or provincial-city battery to retire later.
The live pool is 5 hamlets and ZERO villages. So "later" does not mean "delete the town checker too" - it
means that when towns and cities are scripted, their rules are written directly as placer unit tests and a
battery is never built again.

The session also stated one assumption for the GM to override: where a check body is the sole operative
statement of a research finding, the finding is preserved in `research/` before the code goes - the rule
survives, the runtime check does not.

## 2026-08-30, the GM on the town and city checks (after the spec was FAITHFUL at round 3)

> Oh, actually, I am okay with these automated checks for towns and cities being deleted now. Now that I think about it, that is probably better. Because we basically just proven that the automated checks aren't needed. And, essentially, what will be required of us when the time comes to create a scripted process for towns and cities is to have placement algorithms which will straightforwardly be correct and not require these sorts of automated checks. Right? or is there logic in the automated checks which will need to be converted into placement algorithms, and therefore, we should not delete the code just yet? What do you think?

**The session MEASURED the question rather than answering it from impression**, and the measurement is what
FR-005's urban clause rests on:

- The urban rules are not in the 11 tier-guarded segments. They are spread across **39 segments** whose
  bodies carry an `if URBAN:` branch - **544 lines of code and 163 of prose** - and **none of the 39 cites
  where its finding is recorded.**
- But the knowledge is not trapped in them. Spot-checking the prose-heaviest (`kosatsuba`, 66 lines of
  comment in the check body), `settlements/urban-features.md` carries the whole doctrine MORE FULLY than
  the check does, including the exact rule the check enforces - *"the presence floor is gates + 1"* - with
  a link onward to the research entry. `ministries` and `flophouse` are likewise documented across
  `settlements/` and `research/`.
- **So the check bodies RESTATE the rule; they do not hold it.** The logic in them is trivial - an overlap
  test, a distance, a count. The value was the number and the reasoning, and those are in the docs.

**One spot-check came back empty** (`wall thickness` found nothing in `research/` or `settlements/`), which
is why the confirmation is per-rule and recorded rather than assumed for the class.

**And the honest gap, stated to the GM rather than discovered later:** for hamlets a deleted check's rule
lands in a placer unit test immediately; for towns and cities there is no placer yet, so those rules are
**advisory documentation until someone writes one**. That is the GM's architecture working as intended -
the doc is what a future placer author reads, and their placer gets a test - but it is a real gap in the
interval.

## 2026-08-30, the GM on the documentation sweep and the Mode A carve-out

> Okay. That sounds great. Keep on going then. I look forward to seeing you rip out the remainder of the automated checks and retire that from our architecture completely. Make sure to check our documentation also for any places that refer to automated checks such as this for the scripted process and then rip them out. However, please keep in mind that for nonscripted diagrams such as the magistracy diagrams, There still are automated checks and those survey valuable purpose because those maps are generated by hand rather than by a scripted process. Therefore, we should not rip out every mention of this type of automated check. from our documentation.

**The carve-out is the SAME argument running the other way, which is why it holds.** The Mode B battery is
retired because a correct placer makes a post-hoc audit redundant. Mode A compounds are hand-authored SVG -
placed by a person - so a check on them is catching exactly what a check is for. The GM's own framing of
feature 163 said so from the start: *"This was not true at an earlier stage of this project when the maps
were essentially hand generated and then our automated checks told us whether we had placed things by hand
correctly."* Mode A is still at that stage.

**Measured, so the boundary is drawn on evidence rather than by name:**

- Mode A's apparatus is `tools/pack_audit.py` (1,225 lines), `tools/scatter_audit.py` (261) and **8 frozen
  red SVG negative fixtures** in `tests/fixtures/`. It references `check_village` **zero times**, so
  deleting the Mode B battery cannot touch it and no code change is implied by the carve-out.
- The risk is entirely in PROSE. The doc split is uneven and a blanket sweep would strip live doctrine:
  `dev/gate.md` is pure Mode B (10 battery references, 0 Mode A), `buildings.md` is overwhelmingly Mode A
  (35 to 1), `SKILL.md` is mixed (5 to 15), `settlements.md` mostly Mode B.
