# Tasks: A Roll Cache a New Clone Can Use (feature 167)

Every task is `research: procedure`. The measurements that satisfied the GM's condition are in
[`request.md`](request.md); what the implementation turned up is in [`research.md`](research.md).

- [x] T01 answer the GM's two conditions BEFORE specifying anything
      research: procedure
      verify: a cold clone pays 30 s (reference) + 122 s (map-rolling gate tests) against 1 s + 21 s
      warm - ~2 min, six times the 21 s bar; and touching the most depended-on engine module costs
      `make quick` 10 s against 4 s warm, so the testmon cost is one-time construction and that
      database stays per-clone, as the GM concluded

- [x] T02 baseline: `make done` green on the unmodified clone
      research: procedure
      verify: /tmp/167-base.log, EXIT=0

- [x] T03 FR-001: dependency records are root-relative, absolute outside the skill root, and
      `FORMAT_VERSION` is bumped to 2 so old absolute entries are discarded rather than re-keyed.
      A data file is HASHED FROM THIS TREE while the key string carries the recorded path
      research: procedure
      verify: `tests/pipeline/test_gencache.py`, 20/20

- [x] T04 FR-002: the safe direction is proved, not assumed - the same sources under a DIFFERENT
      root key identically, a changed engine source does not, an old absolute-format entry cannot be
      re-keyed, and a data file follows this tree rather than the producing one
      research: procedure
      verify: the four new tests in that file, each of which fails if its guard is removed

- [x] T05 FR-003/FR-004: `sync-with-main.sh` seeds a new clone's `.gencache` from a sibling at the
      same commit; one directory test when a cache already exists; a cold start when none matches
      research: procedure
      verify: the cross-clone probe below

- [x] T06 the decisive cross-clone probe, run TWICE - the first run was invalid
      research: procedure
      verify: on a clone that has never rolled, seeded from a sibling: the reference settlement
      **HIT in 5 s** (30 s cold), a changed engine function **MISSES** (29 s), and the 63
      map-rolling gate tests take **28 s** against **122 s cold** and 21 s warm. A cold clone's
      ~152 s becomes ~33 s.
      THE FIRST RUN REPORTED 156 s AND WAS WORTHLESS: this clone's cache was still 119 format-1
      entries plus one rebuilt one, so the seed was junk the probe clone had to discard and re-roll
      through. The number was published before it was checked; `research.md` R6 carries it

- [x] T07 `make done`: **GREEN, 2790 passed / 2 skipped**, against the green T02 baseline. The
      `hooks-test` phase re-ran the three suites whose guards changed. `scripts/test-sync-with-main.sh`
      gains three seeding vectors (seeded from a sibling; an existing cache left alone; a sibling at
      a different commit refused) - 47 checks green. The third of those caught a real gap: `cp -a`
      fails when the destination parent does not exist, which the implementation now creates
      research: procedure
      verify: /tmp/167-done.log; the two suites above

**BYPASS AUDIT** (the constitution's closing step): this feature added one kind of entry to
`dev/bypass-log/` - the `PAIR_OK` on its gate runs, on the ground that it changes whether a roll is
SERVED or PRODUCED and never what a map contains, so there is no map for a settlement-review to look
at. Justified, and checked rather than asserted: no pool manifest is in the diff, and the gate's
map-rolling tests return the same verdicts as the baseline. No `REF_OK`, no FULL run, no `GATE_OK`,
no `MEASURE_OK`, no `DISCARD_OK`.
