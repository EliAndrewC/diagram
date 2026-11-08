# Feature 449 - quickstart (phase 1)

- Build and test the guard crate: `make rust-test` (prints cargo's summary per crate), `make static` (clippy on both crates, coverage).
- Run one guard against an input: `echo '<hook json>' | rust/guard/... l7r-guard --only pair-hooks PreToolUse` through
  `scripts/hooks/l7r-guard.sh` (the wrapper builds it first if its sources are newer).
- Replay a guard's suite against the Rust guard: `HOOK_RUST=pair-hooks make hooks-test` (each suite's `HOOK` pointed at
  `l7r-guard --only <guard>`), every case green before the guard switches.
- Time the guards for a Bash call: re-run `m:hooks-bash`'s command (measurements.json) - the phase closes on SC-001.
