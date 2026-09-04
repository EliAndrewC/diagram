# The GM's request, verbatim

2026-09-04, after feature 178 reported the compute comparison and the perf-band explanation:

> Okay. Yes. Let's go ahead and lock in the eight CPUs going forward. And then, yes, let's make the
> band one threshold per environment. with a noise floor of about two percent proceed. Please
> implement both of those, which I think will resolve both of our open questions. if I am not
> mistaken. Thanks.

## What was put to them, that this answers

Two open questions left by feature 178, both stated as questions rather than decided:

1. **The compute default.** Feature 178 measured three instance types on ONE commit, sequentially,
   all green: `g1.medium` (4 vCPU) 913 s / $0.16, `g1.large` (8 vCPU) 553 s / $0.20, `g1.xlarge`
   (36 vCPU) 418 s / $0.56. The session recommended 8 vCPU and did NOT change the default, because
   FR-016 had set the advance criterion - green everywhere AND at least 50% cheaper at no worse wall
   clock - and 8 vCPU is 64% cheaper but 1.32x slower, so it misses the wall-clock half.

2. **The band-1 threshold.** The GM's own instruction on the perf transport was *"If so then please
   implement that; if not then let's talk more."* The transport was implemented; a remote FULL build
   still cannot go green, because `perf_bands.evaluate` sets band 1 on `total_pct > 0 or any(p > 0)`
   - ANY increase on ANY seed. The session put the residual to the GM with the measurement:
   feature 129's three noise runs, IDENTICAL code on CodeBuild's 36-vCPU box, fire band 1 on
   **5 of 6** pairwise comparisons. The recommendation was a per-environment floor of about 2%
   (double the measured ~1% noise), keeping `> 0` locally and leaving bands 2 and 3 untouched.

"about two percent" is the GM's number and it is the recommended one; "proceed" answers both.
