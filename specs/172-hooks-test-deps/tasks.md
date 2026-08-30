# Tasks: `hooks-test` Costs What It Should (feature 172)

Every task is `research: procedure` - this is about what the tooling measures of itself. The GM's
words are in [`request.md`](request.md); the measurements, including the ones that contradict the
feature's own premise, are in [`research.md`](research.md).

- [x] T01 measure BEFORE specifying, and put the result to the GM even though it undercuts their
      stated reason for the feature
      research: procedure
      verify: R1/R2 - the skip already existed and cost 0 s; the refinement would have saved one and
      two suites on the helpers this session actually edits. Reported, with the smaller option left
      on the table; the GM chose the larger

- [x] T02 FR-001: `scripts/_hookdeps.py` derives each suite's dependency set, transitively, with the
      helper roster itself derived and the graph read from CODE rather than raw text
      research: procedure
      verify: `_gatecost.py` 21 -> 2 and `test_hooks_cases.py` 21 -> 3; and three separate ways the
      derivation was wrong first, each caught by measuring the blast radius rather than by reading it
      (R4)

- [x] T03 FR-001: whole-tree is an OUTPUT where it can be (`gate-stamp.py` reads the directory) and a
      STATED LIMIT where it cannot (`sync-with-main.sh`, `review-gate.sh` resolve paths at run time)
      research: procedure
      verify: round 1 caught the first version preserving three rows by hand; round 2 caught the glob
      test matching the docstring rather than the code

- [x] T04 FR-002: `hooks-test` runs its suites in parallel - decide, fan out, collect - reporting
      every failure together with the suite that produced it
      research: procedure
      verify: R6 - 194 s serial, 63 s parallel, 21 of 21 green both ways on the same content

- [x] T05 FR-002: every suite checked for shared state before being run concurrently
      research: procedure
      verify: no suite writes host-wide state beyond a guard log each isolates; the three that use
      `HOME` point it at their own temp; two build real git trees in their own `mktemp -d`. No suite
      needed serializing, and the empirical run agrees

- [x] T06 FR-003: `_hookmatch.py` split by cohesion into `_hm_shape.py`, `_hm_escape.py`,
      `_hm_make.py`, with each guard invoking the leaf it uses and the umbrella kept for anything that
      imports it by name
      research: procedure
      verify: 320 comparisons of every function against the pre-split version, zero differences; then
      `_hm_make.py` at 3 of 18 guards

- [x] T07 FR-004: the derivation is checked, not trusted - the transitive case, a helper on disk the
      deriver cannot see, a filename in prose, and the whole-tree derivation
      research: procedure
      verify: `tests/tooling/test_hook_deps.py`, 9 checks. The transitive assertion is what caught the
      Python-import under-run that the split itself created (R5)

- [x] T08 the whole guard suite and the gate, green together, then the push
      research: procedure
      verify: `make hooks-test` exit 0 in 60 s with every suite forced stale, and `make done` exit 0,
      re-run after each review round's changes; then `sync-with-main.sh done`

## What this feature did NOT achieve, stated plainly

The GM's reason for asking - *"it would have paid off a lot over the last couple of days"* - is still
not true of the dependency refinement alone, and the final numbers say so: the escape family and
`_guardlog.sh` remain at 17 of 18 guards, because every guard reaches its escape through them and the
escape stands on the shape primitives. What pays on those days is the parallelism (194 s -> 63 s), and
what the refinement buys is the `_gatecost.py`-shaped change: 21 suites down to 2.
