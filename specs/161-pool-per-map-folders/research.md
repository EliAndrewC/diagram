# Phase 0 research - feature 161

Design decisions settled before implementation, each with what was rejected and why. This feature
asks no historical question (see R7); every decision here is about the repository's own structure.

---

## R1 - The discovery surface: ONE module answers "which maps exist, where, of what kind"

**Decision.** `l7r/diagram/pipeline/poolmaps.py` gains a discovery API beside its existing
`classify()`. Consumers stop constructing pool paths and start asking for map bundles, saying which
tree(s) they care about. `classify()` itself is unchanged.

**Why.** Ten consumers today each independently hardcode the two-level shape - as a
`glob("pool/*/*.gen.py")` (render_cache, cache_audit, test_villages, test_pool_index, timings), an
`os.listdir` plus a join (mapcheck), a `$(wildcard)` (Makefile), a subprocess grep (check_census), or
a literal default path (check_village's `__main__`). Every one of them is a restatement of a fact
that belongs in one place. `poolmaps.py`'s own docstring already states the principle it was created
for: *"three tools each had their own idea of what the pool contains - this module is so they cannot
drift apart."* The pool's SHAPE is the same kind of fact as its CLASSIFICATION, and it drifted for
the same reason.

This is `migration-plan.md` section 6's **"Derive, don't pin"** applied to the walk itself, and
constitution Principle X clause 14 (*a roster that merely restates what code elsewhere already
declares is DERIVED, not maintained*). Ten hardcoded globs are exactly such a roster.

**What was rejected: deepening the ten globs to `pool/*/*/*.gen.py`.** It is smaller, and it is the
obvious move. Three reasons against, in ascending order of weight:

1. It leaves the defect class in place. The next layout change breaks all ten again, discovered one
   gate failure at a time - the failure shape `migration-plan.md` section 6 names explicitly
   ("Enumerate what binds a feature BEFORE moving it. One reservoir got moved five times because its
   three constraints were discovered one gate failure at a time").
2. It cannot express FR-013. With two trees, "which maps" is no longer one question: the render
   cache and the index want both trees, the regeneration sweep and the cache audit want only the
   live one, and the ratchet (FR-013a) wants both for one assertion and neither for the other. Ten
   call sites each deciding that by hand is ten chances to get it wrong silently - and "silently" is
   the operative word, because a sweep that covers too few maps is green.
3. It would have missed the review's finding 1 entirely. `scripts/review-gate.sh` and
   `ci/delta.py` do not glob at all; they match a path PATTERN. A mechanical glob-deepening pass
   would not have looked at them, and both fail silently.

**Cost accepted.** One new module surface to keep tested at 100%, and one indirection between a
consumer and the filesystem. Both are cheap; the surface is a pure directory walk over a tree whose
shape this feature defines.

---

## R2 - Sequencing: the TOOLING learns the new shape first, then the files move

**Decision.** Five phases, in this order: (1) the discovery surface exists and is tested, tree
untouched; (2) every consumer is converted to call it, tree still untouched; (3) ONE map moves; (4)
the remaining 27 move; (5) docs and full verification. The surface describes whatever tree is on
disk, so phases 1 and 2 leave the suite green throughout.

**Why, on iteration cost rather than elegance** - which is the basis the plan is required to justify
this on. The alternative (move the files first, then chase the breakage) puts the repository into a
state where `make done` cannot complete at all, and the project's own measured lesson is that this
is the expensive failure mode: *"the failure mode is discovering the ordering one gate failure at a
time"* (CLAUDE.md). With ~120 files moved and ten consumers broken simultaneously, every gate run
returns a pile of failures whose causes are entangled, and each cycle costs a full gate. Converting
the consumers first means each one is verified against a green suite, and when the move happens the
only thing that can break is the move itself.

There is a second, sharper reason. Phase 3 moves exactly ONE map. If the shape is wrong - a link the
index cannot resolve, a gen whose `sys.path` arithmetic is off by one - it surfaces on one map that
takes ~15 s to re-verify, not on 28 maps and a 195 MB rename set that would have to be unwound.
That is the constitution VI "reference settlement, then the pool" discipline in the form this
feature can take it.

**What was rejected: dual-support (the tooling accepts BOTH shapes, move, then delete the old
support).** It is the standard safe migration and it is wrong here, because the two shapes are not
ambiguous-but-compatible: `pool/hamlets/inashiro.gen.py` and `pool/hamlets/inashiro/inashiro.gen.py`
can be told apart trivially, so dual-support buys no safety a single walk does not already have. It
costs a transitional code path that must itself be tested to 100% and then deleted - and a
transitional path that is deleted in the same feature is pure overhead.

---

## R3 - `ci/delta.py`: keep the merge-route classification IDENTICAL

**Decision.** Add `legacy-hand-authored-pool/` to `_ENGINE_DIRS` alongside `("pool/", (".gen.py",
".json"))`, so a change under the legacy tree classifies as engine content exactly as it does today.

**Why.** FR-007 makes this feature a pure relocation, and `_ENGINE_DIRS` is the list that decides
whether a push takes the free DIRECT route or the paid GATED one. Changing what it classifies is a
change to how the repository merges - a different kind of change from moving files, and not one this
feature was asked to make. One line keeps it identical.

**The alternative was considered and is arguably MORE correct, which is why it is recorded rather
than dismissed.** A frozen exhibit can never change again: it is never regenerated, never re-gated,
and its renders are committed write-once. A change to one therefore owes no build, so classifying
the legacy tree as NON-engine would be defensible and would save a paid build in the one scenario
where someone edits a frozen gen. It is not taken here because (a) the scenario is hypothetical -
the whole point of the freeze is that nobody edits these - so the saving is zero in practice, and
(b) a merge-route change made as a side effect of a directory move is exactly the kind of quiet
scope expansion Principle XVI exists to stop. If it is ever wanted, it is a one-line change with its
own reasoning, not a rider on this one.

---

## R4 - The engine-fingerprint prune lists: the highest-risk item in the feature

**Decision.** Add `legacy-hand-authored-pool` to the directory-prune tuples in BOTH
`pipeline/render_cache.py` `engine_fingerprint()` and `pipeline/gencache.py` `engine_files()`.

**Why this is the top risk.** Both functions walk the skill directory and prune by NAME:

```python
dirnames[:] = sorted(d for d in dirnames if d not in ("pool", "wip", "tests", "__pycache__") ...)
```

A new TOP-LEVEL directory is not in that tuple, so its `.py` files are collected as ENGINE MODULES.
The 18 legacy `.gen.py` would enter the engine fingerprint, which is the input to every map's cache
key. The observable consequences, in order of how long they would take to notice:

- immediately: every map's stamp goes stale at once, so the next render-sync regenerates the whole
  live pool for no reason;
- persistently: any future edit to a frozen exhibit's generator would invalidate every live map's
  cache, which is precisely backwards - the freeze exists so that these files cost nothing;
- and it would be *invisible*, because both outcomes look like a cache working normally.

Nothing in the test suite would go red. This is the reason the feature is not a `sed` pass, and it
was found by reading the two walks rather than by any failure.

**Verification.** T14 asserts the fingerprint is UNCHANGED across the move - the same hash before
and after, computed on the same engine sources - which is the direct statement of the property, not
a proxy for it.

**Related finding, stated rather than left silent:** `scripts/gate-stamp.py`'s `ENGINE_AREAS` hashes
`.claude/skills/diagram` for `*.py` with `EXCLUDE = ("tests/", "l7r/diagram/ci/")`. Legacy gens are
hashed today as `pool/**/*.py` and will still be hashed as `legacy-hand-authored-pool/**/*.py`. **No
change is needed there**, and that is a finding, not an omission.

---

## R5 - The `.gitignore` collapses because the two trees have OPPOSITE policies

**Decision.** Replace the 13 per-tier ignore lines and the 36 hand-written `!` un-ignore lines with
pattern rules over the new shape:

- ignore `pool/*/*/*.svg`, `*.png`, `*.html` - every live render is derived;
- re-track `pool/magistracies/*/*.svg` - a Mode A `.svg` IS the source, not a render;
- ignore nothing under `legacy-hand-authored-pool/` - every render there is a committed exhibit.

**Why it collapses rather than translating.** The 36 `!` lines exist only because committed exhibits
and derived renders were interleaved in the same directories, so each exhibit had to be exempted by
NAME. Separating the trees separates the policies, and a per-file exemption list becomes a
per-tree rule. This is a consequence of the GM's own request rather than an addition to it: the
lines all carry old paths and must be rewritten regardless, and rewriting 36 dead lines to keep a
distinction the new layout has already made would be the odd choice.

**Binding status.** FR-015's MUST (the rules keep working) binds. FR-015's SHOULD and SC-008 (a new
map needs no new line) do NOT bind - the round-1 review was right that promoting a design preference
into an acceptance criterion overreaches what the GM asked for. If the collapse turns out to need a
per-map line for some case not foreseen here, that is acceptable and not a failure.

**Verification.** `git check-ignore -v` on representative paths in both trees, before and after,
plus `git status` proving the 18 exhibits are still tracked and recorded as renames.

---

## R6 - `check_village/__main__.py`'s default must be RE-POINTED, not re-pathed

**Decision.** Its default manifest changes from `pool/villages/kikuta.json` to the live reference
hamlet's manifest.

**Why.** `pool/villages/` ceases to exist - every village in the pool is frozen, so the whole tier
folder moves to the legacy tree. A default that merely gained a directory level
(`pool/villages/kikuta/kikuta.json`) would point into the wrong tree entirely, at a frozen exhibit,
as the out-of-the-box behavior of the validator's CLI. Pointing it at the reference hamlet is what
the default is FOR: the map a session is most likely to want when they run the checker with no
argument.

**This is a class, not an instance.** Any default naming a now-legacy map has the same problem, and
the same fix. The Makefile's `M=`, `A=` and `B=` defaults already name live maps (`inashiro`,
`kuwabata`) and so need only the extra path level; they were checked rather than assumed.

---

## R7 - No SOURCE block moves, and no historical question arises

**Decision.** Constitution IV and V are N/A for this feature; Principle XII is a nil return.

**Method, because "N/A" on a NON-NEGOTIABLE principle should never be a bare assertion.** The moved
set was grepped for `SOURCE: GM NOTES` before the plan's Constitution Check was written. The
`.notes.md` files that move are session-written records of how each map was built, not the GM's
writing; the GM's own writing lives in `/host-l7r-repo/setting/l7r.md` and in SOURCE blocks that
this feature does not touch. `scripts/source-block-hooks.sh` checks containment against the file on
disk, so a slip would be refused at the edit rather than caught at review.

On Principle XII: the feature changes no glyph, size, placement rule, distance or density, and
FR-007 makes every render byte-identical. There is no claim about how a place was built, farmed,
planted or lived in anywhere in the work, so there is nothing to research, nothing to cite and
nothing for a `source-reader` to confirm. Every task is `research: rendering`. The spec's "Decisions
Recorded" table is kept and explicitly empty, so the nil return is legible as a nil return rather
than as a section someone forgot.

---

## R8 - The measured regression baseline

**Method.** `git worktree add --detach <scratch>/base161 HEAD`, then `make done` in that worktree's
skill directory. A detached worktree, never a stash - a stash mutates the tree under any review
agent currently reading it, and two `spec-fidelity` agents read this tree during Phase 0.

**The worktree gap was anticipated, then MEASURED, and the measurement changed the answer.** The
expectation was the documented one: a fresh worktree carries no gitignored artifacts, so live
renders would be present in the clone and absent in the worktree, and two code paths that skip on a
missing render would pass in the worktree by doing nothing.

The actual count (2026-08-30):

| tree | `.png` under `pool/hamlets/` |
|---|---|
| baseline worktree | 8 |
| clone | 8 |

They are **the same 8**, and they are the FROZEN exhibits - akagahara, enokida, honda, ikegami,
moritono, shimizu, tanada, yatsuda - because those renders are COMMITTED (write-once, un-ignored by
name). The five scripted hamlets have no renders in either tree: nothing has rolled them in this
clone, and their renders are gitignored, so there is no worktree-versus-clone gap here at all. The
baseline is directly comparable to the clone, which is the outcome the rule wants and is worth
recording as measured rather than assumed.

**But taking that measurement exposed a regression this feature would otherwise have shipped**, and
it is the most valuable thing Phase 0 produced. See R9.

**Result** (filled in from the run; commit `81641618`):

| phase | verdict |
|---|---|
| reference settlement (Inashiro, seed 4) | CLEAN |
| lint (`ruff check`), duplicate-def selftest | passed |
| format (`ruff format`) | 418 files unchanged |
| typecheck (`pyrefly`) | 0 errors |
| hooks-test | 19 guard suites green |
| tests | **2737 passed, 2 skipped, 0 failed** in 147.69 s |
| coverage floors | deferred to `make done FULL=1` (a deselected test takes its coverage with it) |
| **verdict** | **gate green** (reference settlement + non-map tests) |

Taken on commit `81641618`, scope unlocked, remote off. **Zero pre-existing failures**, so this
feature inherits no ledgered red and the bar after the change is exactly 2737 passed / 0 failed.
There is no rotation and no re-roll, so per-seed comparison survives intact and Principle XIII
applies in its strict form.

Zero NEW failures at merge is the bar. Per-seed comparison is fully preserved - no re-roll, no
rotation, no seed moves - so Principle XIII applies in its strict form: anything that passed before
and fails after is a regression and blocks the push.

---

## R9 - A regression the move WOULD have shipped: the stale-render sweep goes to zero

**Found by taking the baseline, not by reading the code.** This is the concrete return on Principle
XIII's "a regression is measured, not remembered".

`tests/test_villages.py`'s stale-render sweep compares each hamlet's PNG dimensions against its own
SVG's `viewBox` aspect. It exists because *"Sawada and kashikawa shipped PNGs from the roll BEFORE
their lane webs were fixed ... the picture the GM opens showed a farmhouse the lane no longer
crossed"* - the gate's regeneration child runs with `DIAGRAM_SKIP_RENDER=1`, so a gate-driven roll
writes a new `.json` and `.svg` and leaves the OLD raster on disk beside them, and nothing else
compares the two.

It walks `pool/hamlets/*.gen.py`, skips any map lacking both renders, and ends:

```python
assert checked, "no live hamlet render to check - expected in a clean checkout, suspicious after a sweep"
```

**The maps it actually checks are the FROZEN exhibits.** Measured: all 8 hamlet renders present in
the clone belong to akagahara, enokida, honda, ikegami, moritono, shimizu, tanada and yatsuda - the
committed, un-ignored exhibits. The five scripted hamlets have no renders on disk at all, because
theirs are gitignored and nothing has rolled them here.

So after the move, `pool/hamlets/` would hold only the five scripted maps, every one would hit the
`continue`, `checked` would be 0, and **the assertion would fail**. A test whose entire purpose is
catching a silent staleness would itself be the loudest casualty of the reorganization - and had the
assertion not been there, it would instead have passed while checking nothing, which is the worse
outcome and the exact failure `migration-plan.md` section 6 names ("a check that never runs looks
exactly like a check that passes").

**Decision.** The sweep walks BOTH trees. Recorded as **FR-013b**. The frozen exhibits are not
incidental to this check - in a clean checkout they are the ONLY maps it can check, because they are
the only maps whose renders are committed.

**Why this was invisible to inspection.** Reading the sweep, "live hamlet render" in its own
assertion message reads as though it covers the live maps. It does not, and has not since the 2026-08-16
freeze committed the exhibits' renders. The code and its message disagree, and only counting the
files on disk showed which one was true.

---

## R10 - Defect found in the baseline procedure itself: `gate-stamp.py` cannot stamp in a worktree

**The defect.** Running `make done` in a detached worktree - the baseline procedure Principle XIII
*mandates* - crashes `scripts/gate-stamp.py`:

```
NotADirectoryError: [Errno 20] Not a directory: '<worktree>/.git/gate-green-hooks'
```

**The mechanism.** `gate-stamp.py` writes its stamp to `<root>/.git/<name>`. In a normal checkout
`.git` is a directory and that works. **In a git worktree, `.git` is a FILE** containing
`gitdir: /path/to/real/.git/worktrees/<name>`, so writing a path *under* it raises
`NotADirectoryError`. Git's own answer is `git rev-parse --git-dir` (this worktree's git directory)
or `--git-common-dir` (the shared one).

**Why it matters, beyond the crash.** The stamp is a load-bearing guard: *"nothing is pushed that a
green gate did not see"*. In a worktree it cannot be written, so the phase that reports
`hooks-test: 19 guard suites green` cannot record that fact. The gate ran and passed; only the
recording failed. The failure is also noisy-but-non-fatal - it printed a traceback and `make`
continued to the next phase - which is the shape that gets scrolled past.

**Status: fixed under this feature** (Principle XIV - a defect found while doing something else is
fixed in that work). The fix resolves the git directory through `git rev-parse --git-common-dir`
instead of assuming `<root>/.git` is a directory, so the stamp lands in the one place both a
checkout and a worktree share. `scripts/test-gate-stamp.sh` gains a case that runs the stamp inside
a real worktree and proves it writes - the guard's test companion is what stops this regressing
(constitution XVIII).

**Scope note.** This is a fix to a guard script (`scripts/*.py`), which is the `hooks` area rather
than engine Python. It owes a green `make hooks-test`, not a `make done`, and it does not route the
push GATED on its own.
