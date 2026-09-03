# Feature 178 - the GM's request, verbatim (2026-09-03)

Given in answer to feature 177's four recorded findings, plus a fifth question of their own.

> 1) I think a short-circuit for "measured but engine" is best, and would handle this case nicely, so
> please do that.
>
> 2) Yes I agree this sounds like a quick small fix, so please make that fix too.
>
> 3) Couldn't we pass along timing information about past runs to the container?  I mean we could have
> it pull that information from Github or we pass it along in the same manner we pass along our latest
> code, etc.  Wouldn't that work?  If so then please implement that; if not then let's talk more.
>
> 4) Yes, I don't see why we should be tracking those renders.  Not only should we stop tracking them
> in git, we should remove the ones we have been tracking from the git history to clean up the size of
> our git repo.  We should also indeed stop tracking wip/*.html and in general, the generated html
> pages should not be tracked just like the generated svg and png files should not be tracked.
>
> Also, while I'm somewhat shocked to learn that these beefy AWS servers don't save time, does that
> mean we can investigate smaller servers?  Like if we're only using 4 cores then what does a 4-core
> server cost?  Could we get the same performance out of something that costs a tenth what we're
> paying now?  I'm certainly interested in exploring that - can you run some tests against the latest
> code on small inexpensive servers and see what kinds of performance we get with some drastically
> cheaper servers with significantly fewer cores?

## What items 1 to 4 refer to

The four findings feature 177 recorded and left for the GM (`specs/177-.../spec.md` D5, D7 and
`research.md` R12, R15). Reproduced because the instruction names them by number:

1. **R12** - `make done`'s short-circuit key EXCLUDES `l7r/diagram/ci/` (the GM's own feature-132
   FR-025 ruling), but since 2026-09-02 the coverage floor MEASURES it (`source = ["l7r"]`). So a
   change confined to `ci/` cannot re-open the gate that enforces its own floor; feature 177 hit this
   and had to reach the floor with `make test-full`. The GM's answer: a short-circuit key for the
   "measured but not engine" surface.
2. **R15** - `make test-full` records no verification state, so it cannot satisfy the paid route's
   `green-local-since-edit` condition, while a `make quick` that selected nothing and reported
   *"no tests ran in 0.97s"* can.
3. **D5** - a FULL measurement can never go GREEN: `done FULL=1` ends in `perf-gate`, which takes
   BOTH bookends inside the fresh container and compares them to each other, so ordinary noise reads
   as "any increase" and reports band 1, owing records only a `perf-audit` subagent can write.
4. **D7** - 441.1 MB of tracked generated renders, of which the gate reads 97.9 MB (the eight frozen
   hamlet exhibits' `.svg`/`.png`, which `tests/test_villages.py` asserts a raster against a viewBox
   for) and 0.1 MB is Mode A tracked source. Roughly 343 MB is browsable and read by nothing
   automated: `wip/*.html` (190.8 MB), `dev/placement-stages/` (78.4 MB), and the legacy NON-hamlet
   `.svg`/`.png` (73.6 MB).

## The fifth item, and what it is asking

The measurement behind the GM's surprise (feature 177 R16), both sides `make done`, same commit:

| | local | remote |
|---|---|---|
| xdist workers | 8 (the Makefile caps a laptop at 8) | 36 (`auto` in a build) |
| passed / skipped | 2,923 / 2 | 2,903 / 21 |
| test phase | 316.8 s | 365.5 s |

Remote runs 4.5x the workers, 20 fewer tests, and is 15% slower. The GM's question follows directly:
if the parallelism is not being used, what does a far smaller and cheaper instance cost, and does it
perform the same? `config.RATES` today: `BUILD_GENERAL1_MEDIUM` $0.01/min, `LARGE` $0.02,
`XLARGE` $0.08 (the current default), `2XLARGE` $0.20.
