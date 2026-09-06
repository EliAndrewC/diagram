# The GM's request, verbatim

2026-09-06, during an audit of the make targets. First:

> In particular, I don't understand what most of the diagnostics are doing for us.  I think I made
> this point a while back, that `make why-placed` makes sense as an option, but that the other
> diagnostics mostly do not.  Please focus on answering that question in the audit.

Then, on being shown the evidence:

> Other than why-placed and "notes-census", are there any diagnostics targets you recommend keeping?
> why-placed at least seems useful when a human looks at a map and has a question about why
> something was rendered a certain way.  I'm not sure what wokrflow would use any of the others.
>
> In particular, I'm not clear what sun-audit is actually accomplishing even after your mention of
> it having a workflow role.

And, on being given the answer (no - only those two earn their place) with a costing:

> Yes please take them out, thanks, I want all of the ones we don't need, not just pack-audit and
> sun-audit.

## What the session had told the GM before that instruction, so the authorization is readable

That nine diagnostics have NO live consumer; that their apparent users are circular (a coverage test
exists because the 100% floor obliges one; a registry row exists because the module has a CLI); that
the guard and bypass logs record ZERO runs of any diagnostic; and that removing them reclaims ~8,496
lines of which 5,735 are tests that run in every gate.

**Two caveats were stated to the GM before they said "take them out", and the instruction is read as
covering both**: that `timings` produces `timings.md`, which `dev/loop.md` cites as the timing record
of authority - so that record loses its producer; and that "no recorded use" is the argument that
wrongly deleted `citybudget` earlier the same day, so each removal is verified individually rather
than as a batch.

## The GM's ruling on the corrected record (2026-09-06)

After being told that the first audit was wrong in three ways - `pack_audit` has live consumers and
a standing GM ruling preserving it, `sun_audit`'s rules ARE live in the placer, and the quoted cost
was roughly double the real figure:

> The six plus sun audit, please.  Because the placer should already do the job sun audit is
> auditing, so there's no need for that rule.  If pack_audit is used in the magistracy diagrams then
> that's fine to keep though.

**Read as**: remove SEVEN (the six plus `sun-audit`); keep `pack_audit`. The reason given for
`sun-audit` is that the PLACER already enforces what the tool measures - which is true and measured
(`hamletgen/homesteads/stages.py:46` calls `s.sun_corridor(SUN_CORRIDOR_FT)`, and `west_sun_lane`
gates the grove). **"no need for that rule" is read as "no need for that AUDIT"**: the GM is
justifying removal of the tool by the placer's enforcement, not asking for the placer's sun rules to
be deleted. Those stay. If that reading is wrong it is cheap to correct and expensive to guess at,
so it is stated here rather than assumed silently.

## The GM on scatter-audit (2026-09-06, fourth message)

> Also it seems like we can remove scatter-audit if it is used in settlement-review.md because I
> don't see why that review process needs it.  The purpose of that review is to do NON-automated
> checks, right?  So why do we actually need scatter-audit anymore?

**The premise is correct and the agent's own text supports it.** `settlement-review`'s description
is *"Judges the things the automated validator structurally CANNOT"*, and its line 135 says *"Any
count above a handful is needs-work, whatever `scatter_audit` says - the audit encodes the AUTHOR'S
allowances ... and the author's allowance is precisely what is under review."* The review does not
trust the verdict; it uses the tool to avoid hand-parsing SVG.

**So the module splits on a clean seam, and only half of it is the audit the GM is questioning:**
- `adjudicate` / `format_report` / `main` / the target / the registry row - the AUTOMATED JUDGMENT.
  Its only consumer is the review that disclaims it. **Removed.**
- `parse_bases` / `_translated_spans` / `Base` - the SVG PARSER, which resolves a grove clump's
  `<g transform>`. Imported by `tests/settlement/test_land.py:566` (the GM's own 2026-08-26
  scrub-in-the-reeds rule) and by the positional crown guard that caught ~78% of the crown family
  being adjudicated in the wrong place. **Kept, as test support.** Deleting it deletes a rule, which
  is the one thing this feature must not do.
