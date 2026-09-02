# Feature 174 - the GM's request, verbatim

Asked at the end of feature 173, while a coverage question from a peer session was still being
measured. The GM's instruction, in full:

> Sounds great. Thanks. When you are done with that, I think the time has come to begin once again
> enforcing one hundred percent code coverage. I think that right now, we have some ratchets
> somewhere that enforce less than one hundred percent, but I think we want to enforce one hundred
> percent coverage in whatever the relevant place is. I guess our quick tests probably would not be
> able to enforce one hundred percent code coverage because the entire point of them is that they
> are testing most things, and in particular, are testing the things most commonly needed to be
> tested while doing iterative development. But that this is less than one hundred percent of our
> code However, I believe that make done is close to one hundred percent coverage, and at this
> point, should probably be moved back up to one hundred percent with the standard `fail_under =
> 100` configuration option set so that in the future, we literally cannot complete our make done in
> order to merge back into main, and there will no longer be any mechanism by which this can be
> accomplished. We turned this off because we were doing a large refactor, and we didn't even know
> which of our code would remain, and thus it seemed pointless to run lengthy unit tests on code
> that was perhaps about to be deleted. However, at this point, I think that we have stabilized our
> foundation for hamlet generation enough that we can go back to one hundred percent coverage and
> maintain one hundred percent code coverage for the remainder of this project for all time going
> forward. Go ahead and finish what you're working on now and then get the code coverage back up to
> one hundred percent when that is done.

## What the GM stated, separated into instruction and premise

**The instruction** (not in question):
- enforce 100% coverage again, in whatever the right place is;
- `fail_under = 100`, so a run below it CANNOT complete and there is no mechanism to land anyway;
- `make quick` is explicitly EXEMPT - they named that themselves and gave the reason;
- maintain it from here on.

**The premises, which this feature must check rather than inherit** (the feature-172 precedent: a
GM's stated reason that the measurement does not support is recorded, not quietly adopted):
- *"I believe that make done is close to one hundred percent coverage"*;
- *"We turned this off because we were doing a large refactor, and we didn't even know which of our
  code would remain"*;
- *"we have stabilized our foundation for hamlet generation enough"*.

The first two are checkable against the Makefile's own recorded reasons and against a measured run,
and `research.md` does that before any floor is moved.

---

## The GM's later rulings, verbatim

Recorded here because `request.md` is this feature's AUTHORITY and these two rulings changed its
scope - and because round 12 of `spec-fidelity` found the constitution and `CLAUDE.md` quoting the
second one with nothing in the repository to support it. A quotation nobody can check is
indistinguishable from an invented one, whatever its provenance.

### 2026-08-31, on `# pragma: no cover`

> If there is `# pragma: no cover` code tbat cannot happen then we should delete all of those cases,
> because dead code is bad, and it's better to remove it from the codebase. So please do that, and
> the merge into main because I am okay with all of these changes as soon as the dead code is
> deleted, thanks.

Carried out as FR-009.

### 2026-09-02, on the measured surface

> To be clear, a new tool absolutely should silently owe one hundred percent coverage the day it
> lands. Going forward, we want one hundred percent code coverage, period. That was not previously
> the case. We now want that to be the case always. For tools, for our settlement generation, for
> the automated checks on our hand drawn diagrams, for everything. This should be enforced in the
> standard manner. For example, setting "fail_under = 100" in the appropriate places, and such.
>
> So yes. These nineteen modules should Join the measured surface. Though before you do that, can
> you please explain to me what they are? I just want to make sure that there are things that
> actually do belong in the codebase rather than something which should be deleted instead of unit
> tested. Thus, what I would like you to do now is immediately update our project guidelines to
> indicate that a new tool should silently owe one hundred percent code coverage the day it lands
> and that indeed all new code should. And then tell me more about these nineteen uncovered modules.
> so I can decide what to do with them.

...and, after the audit of the nineteen was put to them:

> I agree that none of that is abandoned code. Therefore, it should all have tests, and we should
> require one hundred percent code coverage for it. So please proceed. with implementing that.

Carried out as FR-010. **"For example ... and such" is the GM's own hedge on the MECHANISM** - it is
what licenses `coverage report --fail-under=100` in the Makefile rather than a `fail_under` key in
`[tool.coverage.report]`, which would fire on every partial run. That reading is argued on its merits
in FR-003; this is where the words it rests on are recorded.
