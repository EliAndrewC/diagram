# Feature 440 - the GM's request, verbatim

The GM, 2026-10-27, after trial 439's report (`specs/439-fewer-envelope-probes/report-trial.md`) listed five tooling
improvements its times pointed at - (1) `make land` checking for an owed claim with none in flight before the gate, (2) the
trial template asking for the verdict as "the branch taken, and the measurement that took it", (3) `make perf-profile`
writing the seat counters beside its profile, (4) `make perf-ab` printing each stage's time beside the total, (5) the small
ones: `make trial APPROVED=`, the stale-terms check skipping lines the same diff rewrote, quick's 15 s ceiling failing under
load:

> I think you should make all 5 of those tooling improvements and then run another search trial on one of the 5 untried searches. So please do that. Thank you.

The search trial is its own feature (a trial), after this one.
