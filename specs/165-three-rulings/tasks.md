# Tasks: The Three Rulings (feature 165)

Every task is `research: procedure`: three narrowings of what a guard forbids, ruled on by the GM.
The evidence is feature 164's `research.md` R3/R4/R5; what the implementation turned up is this
feature's own [`research.md`](research.md).

- [x] T01 baseline: `make hooks-test` on the unmodified clone - **19 suites green, exit 0**
      research: procedure
      verify: /tmp/165-base.log

- [x] T02 FR-001 `discard`: `--ours` / `--theirs` (and the `restore` spellings) pass while
      `MERGE_HEAD` exists; everything else refused as before. The `--ours .` whole-tree case is
      permitted and the reason written at the point of change, as `spec-fidelity` asked
      research: procedure
      verify: `scripts/test-discard-hooks.sh` builds a REAL conflict in a second throwaway repo -
      27/27, including the plain discard still refused mid-merge and the same flags refused outside
      one. The first fixture asked the hook about the wrong repository (`research.md` R3.1)

- [x] T03 FR-002 `no-poll`: a backgrounded loop whose condition READS A FILE is permitted, in the
      closed form `spec-fidelity` required - a `grep` on a path operand, a file-test `[`, or an input
      redirect, with no command substitution, no pipeline and no output redirection. The decision
      lives in `_hookmatch.py file-wait`, unit-testable; the wider option the GM declined is recorded
      at the point of change so it is not later "simplified" back
      research: procedure
      verify: `scripts/test-no-poll-hooks.sh` 42/42, carrying all three discriminating cases -
      a backgrounded `curl ... > /tmp/out` REFUSED, a piped process check REFUSED, a file test
      ALLOWED - plus the foreground form still refused

- [x] T04 FR-003 `review-gate`: a delta that is exactly one new `specs/NNN-slug/` directory, with
      `spec.md` itself among the additions, passes check 1. Two holes found while building it and
      closed: the first cut called an implementation push a claim (`research.md` R1), and the
      exemption opened a route one step removed from itself (R2)
      research: procedure
      verify: `scripts/test-review-gate.sh` 17/17 - the claim passes; plus one file elsewhere,
      two claims at once, a modified existing spec, and a LATER push into the same directory are all
      refused. Three of its existing vectors had to be rebuilt (R3.2, R3.3, R4)

- [x] T05 the full local verification and the close
      research: procedure
      verify: `make hooks-test` and `make done`, both green, compared against T01; the bypass audit
      below

**BYPASS AUDIT** (the constitution's closing step): this feature added one kind of entry to
`dev/bypass-log/` - the `PAIR_OK` on its gate run, because a delta of guard scripts and their suites
has no map for a settlement-review to look at. Justified: no `l7r/**` path and no manifest in the
diff. No `REF_OK`, no FULL run, no `GATE_OK`, no `MEASURE_OK`, no `DISCARD_OK`.
