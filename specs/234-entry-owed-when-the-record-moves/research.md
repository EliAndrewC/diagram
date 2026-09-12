# Feature 234 - research and measurement

## R1 - the seam, measured (2026-09-12)

| quantity | value |
|---|---|
| feature classes carrying an `Entry:` tag | 51 |
| entries resolving to at least one research question | 50 |
| deliberately silent entries (`fallow`) | 1 |
| **BROKEN entries today** | **0** |
| research pages named by an entry | `archetypes`, `fields`, `homesteads`, `urban-features`, `vegetation`, `water` |

A broken heading is invisible: `research_questions()` matches by prefix and returns `[]`, and
`test_an_entry_is_complete` asserts only `"research/" in fc.entry`. `research/CLAUDE.md` already
requires a rename to fix "the class entries ... that quote the heading" - in prose, with no mechanism.

## R2 - THE MEASUREMENT THAT KILLED THE FIRST DESIGN (spec-fidelity round 1, 2026-09-12)

The first draft of this spec proposed a PUSH-TIME REFUSAL keyed on "a research section a class was
written from changed in this delta, and that class's docstring did not". The review replayed that exact
rule over the repository's own history instead of taking FR-009's "it will not fire on correct work" on
trust:

| quantity | value |
|---|---|
| commits since 2026-08-20 touching a research page named by an entry | 38 |
| of those, commits changing NO class docstring | 32 |
| of those 32, commits the proposed rule would FLAG | **30** |
| worst single commits | `1e77e82f` 41 classes, `c8b86cd3` 38, `290659f5` 37, `536dbf56` 34 |

And those 30 are the record's own maintenance sweeps - footnotes moved onto citations pages (211),
session notes turned into HTML comments (209), the absence-note pass, the translation pass (202). Every
one is CORRECT work that changes no obligation on any modal's prose, and by construction touches no
docstring, so the "docstring changed in the same delta" exemption never fires on them.

**Why this is disqualifying rather than a tuning problem.** The root `CLAUDE.md` keeps a list of rules
DELIBERATELY not enforced, on the stated grounds that "a guard that fires on correct work teaches a
session to bypass every guard". Feature 173's precedent (the file-size bar) runs the other way: a line
count "fires on exactly the thing it names". *The body of a section your class quotes changed* is NOT
the thing this rule names. The thing it names is *what the modal says is now out of step with the
record*, and no delta-derived script can decide that - it is a judgment about prose.

The first draft also contradicted itself and the contradiction was the tell: FR-009 asserted the guard
would not fire on correct work, while FR-005 named that very work ("a footnote added, a typo fixed, a
citation re-pointed") as the legitimate case for its escape.

## R3 - what the short-circuit does to a "report it at the gate" requirement

`make done` exits at its short-circuit (skill `Makefile:122`) before any phase runs when engine content
is unchanged. A research-page edit plus a class docstring is NOT engine content (features 188, 189,
207); the target such a delta owes is `make page-check`. So a requirement to "report at the gate" is
VACUOUS for the exact delta this feature exists for: the gate would never run, and the report would
never print. Any reporting channel has to be a target the delta actually runs.

## R4 - the design this leaves

Three things are true together, and the design follows from all three:

1. Something must SURFACE the pair (a moved section, a modal whose explanation did not move), because
   the GM's whole point is that nobody currently knows.
2. Nothing may REFUSE on it, because R2 shows the key fires overwhelmingly on correct work.
3. Deciding whether a modal is now out of step is a judgment about prose, and this project already
   routes that kind of judgment to a subagent on Opus rather than to a script (`record-format`,
   `quote-check`, `source-applicability` - each "verification, not judgment", each reporting rather
   than deciding).

So: a script that REPORTS candidate pairs, on a target the delta actually runs; a guideline that says
what is owed when one is named; and the judgment left where this project already puts it. The one thing
that IS mechanically decidable - a heading that no longer resolves - stays a gate failure, because that
fires on exactly the thing it names and is never correct work.

## R5 - can the key be narrowed enough to enforce it? NO (2026-09-12, after the GM's ruling)

The GM: *"I don't believe that we should have any such thing as an unenforced doctrine. If it is
unenforced, then it is not a doctrine. something should either not be considered doctrinal or it should
be enforced."* That strikes D6's shape, so the question became whether the key could be made quiet
enough that a refusal would not land on correct work.

The obvious narrowing: fire only when what a READER SEES changed - strip HTML comments, footnote
markers (`<sup class="fn">`) and link attributes, then compare. That is aimed squarely at R2's 30
sweeps, which moved footnotes onto citations pages, turned session notes into comments, and re-pointed
citations.

Measured over every research-only commit since 2026-08-20:

| key | commits that fire |
|---|---|
| the section's BODY changed | **39 of 39** |
| what a READER SEES changed | **38 of 39** |

**It does not help.** One commit in thirty-nine is the entire saving, because those sweeps do touch
reader-visible text - a session note turned into an HTML comment REMOVES a visible sentence, and the
translation pass rewrites visible quotations. There is no mechanical key that separates "this section
now says something different about the thing on the map" from "this section was maintained", because
that separation is a judgment about meaning.

**So the choice is the GM's binary, with narrowing eliminated: enforce it.** And the shape enforcement
takes here is the one this repository already uses for every rule whose compliant action only a session
can supply - `guard-write`'s 41 refusals, `guard-file`'s 77, `FILE_SIZE_OK`, `PAIR_OK`, `GATE_OK`: the
guard REFUSES, the session supplies the thing no tool can (its judgment, in writing), and the reason is
auditable afterward. That is enforcement, not doctrine: nothing lands until the pair is resolved or a
reason is recorded, and `make audit` can list every reason anyone ever gave.

The cost is bounded by the same FINDING rule that was already in FR-013: a maintenance sweep naming 41
classes is discharged by ONE recorded line, not 41 dispatches.
