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
