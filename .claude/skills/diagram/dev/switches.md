# The iteration switches - remote off, scope locked (feature 132)

**Load this when:** a target refused with "remote is OFF" or "scope is LOCKED", you are about to
throw or release a switch, or you are adding a target that rolls a map and need to know whether the
lock should cover it.

## What they are

Two committed, repository-wide switches in ONE tracked file, `dev/switches.json`:

| axis | states | what it governs | throw / release |
|---|---|---|---|
| **remote** | `on` (default) / `off` | whether anything is dispatched to AWS CodeBuild, and whether the merge gate may depend on it | `make ci-off REASON="..."` / `make ci-on REASON="..."` |
| **scope** | `unlocked` (default) / `reference` | whether any invocation may roll a map other than the tier's reference settlement, or more than one map | `make scope-lock REASON="..."` / `make scope-unlock REASON="..."` |

`make switches` prints both, with the reason, who threw it and when. The history of throws and
releases is the file's git log - each target commits its own change.

**They are two separate axes on purpose.** One could want local full sweeps with AWS off (a budget
month exhausted, offline), or AWS on with the scope locked (another session landing engine work
while this one iterates). Neither implies the other.

## Why they exist (the GM, 2026-08-25)

> *"I want to make sure that as we iterate, not only do we not run the full test suite, but we
> literally cannot because just telling you, please make sure not to run the full tests. In the
> past has frequently resulted in the full tests getting run, and that costs both time and actual
> money now that we are running on AWS."*

> *"can we perhaps have the first thing that we do to update the tooling to essentially disable
> AWS? That seems like something that would be good as a reusable setting anyway. such that if it
> is disabled, then we do not use it as a gate. and we do not dispatch to it while we are doing
> iteration."*

The project's own record says the same thing about instructions versus tooling: the reference-first
rule was written into the constitution and violated by its own author six hours later; feature 126
ran the full gate three times against a standing instruction; the 2026-08-24 bypass audit found 3
of 5 full sweeps unjustified. An instruction is a speed bump; a switch with no override is a wall.

## The rules, each with its reason

- **One tracked file, not an environment variable.** An environment variable is a forgery vector
  (feature 130 refused the FULL door through one for the same reason) and does not travel: a
  setting the GM throws once must reach every clone through the normal sync-in, which only a
  committed file does. A clone that has not synced since the throw still has the old state - the
  sync-in at the start of every piece of work is what delivers it.
- **A setting, not a log - so ONE file.** `perf-log/` and `bypass-log/` are per-entry directories
  because concurrent pushes conflict on an append-only file. A switch has a current VALUE; two
  sessions flipping the same one at once is a real conflict that SHOULD be seen.
- **No override exists.** Not an environment variable, not a make variable, not a flag. The
  release target is the only way back, and it commits. `cohort_audit`'s `--anyway`, `mapcheck`'s
  `--scope all` and its `SCOPE` environment default are read THROUGH the lock, not around it.
- **A malformed file fails closed** - remote off, scope locked, the parse error printed. The next
  throw or release rewrites it; that is the repair, and it is a diff someone reads.
- **Absent means defaults.** A checkout older than this feature, or a fixture, has remote on and
  scope unlocked. Absence is never "off".
- **A hand edit is flagged** - `scripts/guard-file-hooks.sh` treats the file as a guard, so a
  session editing it directly gets the same prompt as one editing the Makefile.

## Remote off: what the merge gate does instead

The gated route (engine code in the delta) becomes **LOCAL-GATED**. `make ci-merge` dispatches
nothing; it answers `SKIP-VERIFIED` when a green local `make done` vouches for exactly the engine
content the merge with the latest main would produce (the local-verified rule of 2026-08-25), and
the clone pushes directly. Otherwise it refuses and says what to do: `git pull --no-rebase origin
main` (if main moved on engine paths), `make done`, `scripts/sync-with-main.sh done` again. The
session is the driver of that merge, where the build would have been - the same sequence.

`make ci-check`, `make ci-image` and any `FULL=1` refuse outright; `make ci-status` still answers
(without the S3 lookup) and shows `remote-enabled` as the first condition. No AWS client is
constructed while the switch is off - the suite proves it by making the constructor raise.

## Scope locked: ONE map per invocation, reference only

The rule, not a list (the fidelity review of the spec turned an enumeration into a rule after
finding `cache-audit` and a globbed `make map GEN='pool/*/*.gen.py'` open): **no invocation may
roll a map other than the tier's reference settlement, and no invocation may roll more than one
map.** Enforced in the Makefile AND in every Python entry point that can roll more than one map,
because the Makefile's own record says a guard on one door is not a guard.

| refuses under the lock | still runs |
|---|---|
| `cohort`, `tripwire`, `maps SCOPE=all`, `test-full`, `done FULL=1`, `cache-audit` (any form), `regressions`, `perf`, `perf-gate`, `ci-check FULL=1`, `ci-check TARGET=<op>`, `ci-merge FULL=1`, `map` with more than one gen or a glob | `reference`, `quick`, `done` (reference scope), `test-file`, `map` with ONE gen, `hamlet` with one spec, `perf-profile` (one seed, one stage), `placement-stages`, `perf-report`, `maps` (reference map alone - it never widens while locked, whatever the last run said) |

### THE DECISION: one-map invocations stay runnable (recorded, with the alternatives priced)

**Accepted**: under the lock a session can still regenerate ONE map (`make map GEN=...`,
`make hamlet`) - including a map other than the reference settlement.

**What it costs**: a session can, one invocation at a time, roll any pool map; the lock does not
stop a slow hand-rolled sweep. Observable: `git log dev/run-log/` would show it.

**Alternatives priced**:

1. *Refuse every non-reference map, one at a time or not.* Declined: the GM's definition of the
   suite is *"forty eight different maps ... some number of different maps with some number of
   different seeds per map"* - a sweep; one map is iteration, and the lock exists to protect
   iteration on the reference map, which needs `make map` and `make hamlet`. Distinguishing "the
   reference gen" from "another gen" at the Makefile would also have to know every tier's
   reference, which `mapcheck.TIERS` knows and the Makefile does not.
2. *Cap invocations per hour.* Declined: a rate limit is a policy nobody asked for, and it fires
   on correct work (a fix that needs five regenerations of Inashiro in ten minutes).
3. *Refuse `perf` too* - this one was ADOPTED at the fidelity review's round 2: four seeds is a
   sweep by the GM's definition. A feature that lands while the lock is on records "bookends not
   taken - scope locked" in its plan; they are owed at unlock, and `make scope-unlock` says so.

**Who chose**: the session, under the spec's FR-012/FR-018; the spec was graded FAITHFUL against
the GM's words at round 3 (2026-08-25).

## `make done` short-circuits on the same rule as the remote gate (the amendment)

GM, 2026-08-25, seeing a five-minute gate follow documentation-only commits: *"this also seems like
the kind of thing which shouldn't even run the normal 5 minute tests, right?! Like it's only
documentation. Can we apply the same rules that decide whether to short circuit and skip AWS tests
to these 5 minute tests as well for the make done procedure?"*

So `make done` (reference scope) first asks `python3 -m l7r.diagram.ci verified-done`: is the last
recorded verification a green `make done` whose **gate key** equals the working tree's now? If so
it prints `already verified` with that run's time and commit, re-stamps, records `green-local done`
and exits green in seconds - no map rolled, no test run. The run-log gets an `already-verified`
entry so the audit can see how often it happens.

**The key is EXACTLY the dispatcher's** (`state.already_verified`): the content hash of every
`*.py` under the skill outside `tests/` (`gate-stamp`'s `diagram` hash - the dispatcher's
`green-local-since-edit` condition; `.explain.py` and `wip/*.gen.py` count) and the engine key over
`pool/*.gen.py`, `pool/*.json` (its `tree-not-already-verified` condition). **The Makefile,
`pyproject.toml`, the lockfiles and `scripts/` are NOT in it**, exactly as they are not in the
remote key - GM 2026-08-25, second amendment, after seeing a Makefile change re-run the gate: *"I
thought we were omitting `make done` results for changes to the hooks or scripts or makefile
changes, etc."* The first draft widened the key to those paths on the fidelity reviewer's
containment argument; the GM overruled it. What covers them instead is unchanged: the guard
scripts owe `make hooks-test` (gate-stamp's `hooks` area), and a Makefile edit is exercised by the
next real gate. A docs-only change matches nothing.

**Why re-stamping is safe**: the short-circuit re-writes `gate-stamp`'s `diagram` stamp, which
asserts "a green gate ran on exactly this Python" - and the check compares that SAME hash, loaded
from `gate-stamp.py` itself (`tests/ci/test_state.py` proves the two are one computation).

**Tests-only changes skip BOTH gates** (the GM's ruling, FR-024). The GM remembered an AWS rule
"if the only thing that changed were tests AND the previous test run was green then we skipped"
that feature 130 had not implemented (`tests/` was in the engine set); the session asked rather
than resolving it, and the GM chose *"Yes, locally AND on AWS"*. So `tests/` is outside the route
decision, the engine key and `gate-stamp`'s `diagram` area. The recorded cost: a test edited after
the last green run lands on main unexecuted and runs on the next real gate.

**`l7r/diagram/ci/` is exempt the same way** (FR-025, the GM: *"isn't it actually test code? Like
the engine itself isn't using it, right?"*). It is tooling that decides whether the tests run;
nothing in it reaches a map; its tests are fast and inside `make quick`. A ci-only change is DIRECT
and needs no stamp. `switches.py`, `_invocation.py` and `tools/` are the same kind of code and were
left in the engine set because the GM named `ci/` - add them if wanted.

**What never short-circuits**: `FULL=1` (a different scope); a last record that is a green `quick`,
`reference` or `test-file` (they vouch for less than the gate); a red last run. And there is no
flag in either direction - a `FORCE=` re-run flag was drafted and removed at the fidelity review as
unrequested; the remote rule this copies has none.

## When the lock is released

`make scope-unlock` prints the reminder: nothing swept the pool and no perf bookend was taken while
it was locked, so run `make maps` and the owed `make perf` bookends then - what accumulated is
measured, not remembered (constitution XIII). Pool regressions that built up under the lock are
found at unlock; that is the accepted cost of the period, and the closing task of the feature that
used it.
