# 197 - Claim feature numbers under a lock

**Status**: FAITHFUL at review round 1 (spec-fidelity, 2026-09-07: "Nothing MISSING ... No requirement
contradicts the request. Scope is not inflated"; D1 judged faithful to the GM's words, D3 a legitimate
boundary; its one aside - whether the commit-and-push-the-claim step is still load-bearing - is answered
in `docs/session-clones.md` point 2: the push publishes the claim to the laptop and GitHub, which the
scan cannot see); implemented
**Request**: [request.md](request.md) (the GM's words, verbatim)
**Classification**: tooling; every task `research: rendering` (nothing here is about how a place was built)

## Why

Two sessions each read "the highest number under `specs/` plus one", each got the same answer, and each
built a feature under it. Main carried the result when this was written: `specs/195-cite-only-what-can-be-read` and
`specs/195-target-descriptions-and-two-removals` both landed under 195 on 2026-09-06 (the second is 198
since 2026-09-07 - D3), and on 2026-09-05
two sessions both claimed 184 (one renumbered to 186 before landing). The existing protocol
(CLAUDE.md "Concurrent sessions", `docs/session-clones.md`) allocates from main's `specs/` after
`sync-in` and relies on the PUSH to surface a collision - but the push comes hours or days after the
specify step, and the GM's observation is exactly that cost: *"two different features might go for a
long time"*, and the loser *"needs to go back and update their feature to use a different number"*.

The GM's proposed shape - *"a makefile target that selects the next feature number ... using some file
locking or other kind of multiprocess locking"* - fits the container: every session's clone is
`<mirror>/.clones/<name>`, and the mirror root is a host volume mount, so one lock file under it is
seen by every session on the host, and it survives a container rebuild.

## What "the next available number" means here

A number is TAKEN when any of these holds it (all read under the lock, so two claims cannot read the
same state):

1. the mirror's working tree `specs/` (main as this container last saw it);
2. the mirror's `origin/main` tree (`git ls-tree`), in case the mirror has fetched and not yet
   fast-forwarded - a read of the packfile, no network;
3. every clone's `specs/` under `<mirror>/.clones/*/` - the UNPUSHED claims of the other sessions,
   which is the source the old protocol could not see;
4. the ledger of every claim this tool has made (FR-002).

Next = 1 + the maximum over all four. **The claim is the directory**: `specs/NNN-slug/` is created in
the caller's clone before the lock is released, so the next caller's scan (source 3) sees it. The
ledger is a record and a safety net, never the only source - which is what lets it be lost without
consequence (D2).

## Requirements

- **FR-001 The target.** `make claim SLUG=<slug>` runs from a session clone (the root Makefile forwards
  it; the skill Makefile carries it). Under a host-wide lock it derives the next number as defined above,
  creates `specs/NNN-<slug>/` in the clone, appends one row to the ledger, writes the clone's
  `.specify/feature.json` (`feature_directory: specs/NNN-<slug>` - spec-kit's own per-workspace pointer,
  gitignored since 2026-08-16), and prints the directory name on stdout with the two exports the chain
  needs (`SPECIFY_FEATURE`, `SPECIFY_FEATURE_DIRECTORY`) on stderr. `NNN` is zero-padded to three digits
  as every existing directory is.
- **FR-002 Where the state lives, and that it is derivable.** The lock is
  `<mirror>/.specify/feature-numbers.lock` and the ledger `<mirror>/.specify/feature-numbers.jsonl`
  (one JSON object per line: number, slug, clone, UTC time). Both are under the mirror root, which is
  the host volume, so they persist across a container rebuild, and both are gitignored (`*.lock`
  already is; the ledger gets its own line with the reason). **If the ledger is missing, the next
  claim recreates it** - sources 1-3 alone give the right next number in every case but one, stated in
  D2. Nothing needs regenerating on a fresh container.
- **FR-003 Refusals (exit 2, nothing created, nothing appended).** Run from the mirror itself (main is
  never a workspace - the same rule as the Makefile's `guard`); a slug that is not lower-case kebab
  (`[a-z0-9]+(-[a-z0-9]+)*`; hyphens are the house style); a slug already in use by any directory in
  sources 1-3 (a number is the identity, but a second `NNN-same-slug` is a mistake nobody wants); the
  lock not acquired within 30 seconds (a held lock is a hung process, not a queue - name the lock file
  in the refusal so the session can look).
- **FR-004 Existing collisions are REPORTED, not fixed.** When the scan finds one number under two
  directories in main (195 today), the tool prints a one-line warning naming both and continues. It
  never renumbers - see D3.
- **FR-005 A look without a claim.** `make claim SLUG=<slug> PEEK=1` prints what the claim would be and
  creates and appends nothing.
- **FR-006 One chokepoint.** `.specify/scripts/bash/create-new-feature.sh`'s automatic numbering
  (`check_existing_branches`) is replaced by a call to the tool, so there is exactly one place a number
  comes from. An explicit `--number N` is still honored (a deliberate re-use of an existing claim).
- **FR-007 The documents that told a session to scan by hand now tell it to claim.** The constitution's
  Development Workflow gains the step; CLAUDE.md's "Concurrent sessions" bullet, `docs/session-clones.md`
  "Coordinating spec-kit feature numbers", and the `speckit-specify` skill's directory-resolution step are
  rewritten around `make claim`; `docs/make-targets.html` is regenerated (`make docs`); the root
  Makefile's forward list gains `claim`. The "on collision the unpushed spec renumbers" rule is KEPT as
  the fallback for the one case the lock cannot see (D4) and is no longer the normal path. Every
  surface is found by an unfiltered grep for the old instruction, not from memory (feedback: enumerate
  from the waist).
- **FR-008 The claims are auditable.** `make audit` prints the ledger's recent rows, because a ledger
  nobody reads is a file nobody notices is broken.
- **FR-009 Tests.** `tests/tooling/test_claim_feature.py`, on fixtures built in `tmp_path` (a mirror
  with `.git` and an `origin/main` ref, two clones): each of the four sources moves the answer; twelve
  concurrent claims from one clone (and from two clones) receive twelve distinct numbers; each FR-003
  refusal fires and leaves nothing behind; the FR-004 warning fires on a fixture duplicate; PEEK creates
  nothing; a missing ledger is recreated; the exports and `feature.json` are written. The tool is
  a Python script under `scripts/` like `tick-task.py`, so `hooks-test`'s stamp covers it at push and
  pytest covers its behavior; it is NOT a guard (it refuses a session nothing and rewrites no command)
  and does not join the `*-hooks.sh` roster.

## Success Criteria

- **SC-001** Twelve claims started concurrently receive twelve distinct consecutive numbers, every run
  (the test in FR-009 is the proof; it fails if the lock is removed).
- **SC-002** On the tree as it stands at landing, `make claim SLUG=x PEEK=1` answers `198-x` (197 is
  this feature), and it answers the same from either live clone.
- **SC-003** After landing, no commit on main renumbers a spec directory (`git mv specs/NNN-... specs/MMM-...`)
  for a claim made through the tool. Measured by reading the log, not promised.
- **SC-004** The whole target runs in well under a second - a scan of a few hundred directory names and
  one packfile read - so it costs the chain nothing.

## Decisions Recorded

- **D1 A derived maximum plus a directory, not a counter file.** The GM's words were *"increment the
  spec kit feature number"*; a counter file alone was priced and declined because it would be the one
  source of truth, and the GM's own constraint - *"make sure that it gets regenerated if the container
  is destroyed"* - is met most simply by having nothing that needs regenerating. Every place a claim
  can exist is on the volume already (the mirror, its packfile, the clones), so the tool reads them.
  The lock is what the GM asked for and what makes the read-then-create atomic. The ledger keeps the
  "increment" property across the one gap the scan has (D2).
- **D2 What a lost ledger costs.** A number claimed and then ABANDONED (the session deletes the
  directory before pushing) is held only by the ledger. With the ledger gone, that number is reused
  by the next claim. That is harmless: a number that never reached main identifies nothing. Stated
  here so the next reader does not "fix" it with a counter.
- **D3 The 195 duplicate is the GM's to resolve.** Both features landed, both have commit histories
  reading `195:`, and one may still carry open tasks in another session's clone. Renumbering a landed
  feature rewrites the meaning of its history without rewriting the history, which this repository
  never does. The tool reports the duplicate on every claim until it is resolved; a CLAIM never
  touches either directory.
  **Amended 2026-09-07, after landing - the GM resolved it**: *"Yes please fix 195 by deduplicating
  it."* The ruling is carried out by the tool rather than by hand: `make claim RENUMBER=specs/NNN-slug`
  (`--renumber`) moves an existing directory to the next number under the same lock and the same four
  sources, `git mv` staged, a `renumbered_from` ledger row, `.specify/feature.json` untouched.
  `195-target-descriptions-and-two-removals` became **198**: it was claimed FIRST (21:13 against 22:28
  UTC), but the choice was made on the cost of the move, not on priority - it had six references to
  its number (two engine comments, a tool docstring, the Makefile, a future-work note, a sizing rule)
  against the other's constitution clause (v2.19.0), CLAUDE.md, two agents, three test files and the
  research index. Every reference was rewritten to "198 (claimed as 195, renumbered 2026-09-07)"; the
  `195:` commit messages stand, and the moved spec's header says which feature they were.
- **D4 No network under the lock.** `sync-in` runs at every prompt and fetches GitHub main, so source 2
  is at most one turn old. A spec authored on the GM's laptop and pushed to GitHub between that fetch
  and the claim is the residual window; the old renumber rule covers exactly that and nothing else
  now. A fetch inside the lock would make the claim depend on the network and make the concurrency
  test depend on it too.
- **D5 The tool creates the directory but not `spec.md`.** The spec is the `speckit-specify` skill's
  to write from its template; the tool's job is the number, and a directory is enough for every other
  scan to see the claim.
- **D6 Constitution version.** The Development Workflow section gains a mandatory step ("a feature
  number comes from `make claim`; nothing else allocates one"), which is a new obligation on every
  session, so MINOR: 2.19.0 -> 2.20.0, with the sync-impact note in the header as every amendment has.

## Out of scope

- Renumbering the two 195 features (D3).
- Coordinating anything other than the number - file-level integration is already the locked
  pull+push (`docs/session-clones.md` point 5).
- A remote or cross-host lock: the GM's premise is one host, one container, and the mirror root is
  the shared volume.
