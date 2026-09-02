# The pragma census (feature 174, FR-009) - what a ruling of "yes" would actually cost

Written because constitution XII says the research pass runs BEFORE the ruling is asked for, and the
question put to the GM in FR-009 - does *"there will no longer be any mechanism by which this can be
accomplished"* reach `# pragma: no cover`? - is much easier to answer with the shape of the thing in
front of you. **Nothing here presumes the answer.** Measured in this clone at HEAD, 2026-08-31.

## The size of it

| | |
|---|---|
| `pragma: no cover` sites under `l7r/` | **131** |
| ...inside the tree the hard `--fail-under=100` covers | **90**, across 32 files |
| excluded LINES engine-wide | **469** against 22,470 measured statements |
| excluded LINES inside the hard-floor tree | **281** against 9,118 - **3.08% of that tree is not measured** |
| added by feature 174 | **none** (its one `+` and one `-` are the same line moving with a lifted function) |

Sites are the wrong unit and were the first number taken; the lines come from coverage's own
`PythonFileReporter` under this project's `pyproject.toml` excludes, which is the same reckoning the
gate uses.

## The shape of it - and the finding that matters

Classified by what the pragma's own stated reason CLAIMS:

| class | sites | |
|---|---|---|
| **A** | **62 (47%)** | *"this cannot happen"* - "a hamlet always has its field", "build_comb always emits a drain collector", "filtered above", "fewer houses than this fails the gate first", "belt and braces" |
| F | 55 (42%) | other, with a reason stated |
| B | 6 (5%) | `if __name__ == "__main__":` - the standard idiom, harmless |
| E | 4 (3%) | **no reason stated at all** |
| C | 3 (2%) | needs a real external system (AWS transport) - the honest, irreducible use |
| D | 1 (1%) | an import/path shim |

**Nearly half of these are not "this cannot be tested" - they are "this cannot happen."** That is a
different claim with a different remedy, and this feature already worked one instance of it: the
`if not rows: continue` in `pipeline/pool_index.py` was pragma-shaped reasoning ("`_sections` only
yields pairs that have rows"), and the right answer was to DELETE it, which is what the GM's own
ruling on dead code says (2026-08-31: *"We should delete any dead code, which will also help with
this current effort"*).

So a class-A pragma is in one of two states, and both have an answer that is not exclusion:

- the claim is TRUE, and the line is dead code -> **delete it** (the GM's ruling already covers this);
- the claim is FALSE, and the line is a live branch nobody tests -> **test it** (the floor's whole point).

The 3 class-C sites are the genuinely irreducible ones. The 4 class-E sites cannot be defended in
their current form whatever the ruling, because they state no reason at all - the same objection
feature 170 made to a bare escape token, for the same reason: the missing thing is the reasoning,
which no tool can supply.

## What each ruling costs, so the trade is visible

- **"No, the pragma is out of scope"**: nothing to do; FR-009 stands as the record, and the count
  above is what a future reader inherits. The floor still means what it says about the measured set.
- **"Yes, close it"**: a pass over 131 sites, of which ~62 are delete-or-test decisions of the kind
  this feature already made once, ~6 are the harmless `__main__` idiom that any rule should exempt by
  name, 3 are irreducible and want an explicit carve-out, and 4 need a reason written before anything
  else can be decided about them. Plus the standing rule for NEW pragmas, which is the half that
  actually delivers *"for all time going forward"* - a count fixed today drifts back tomorrow, which
  is exactly what happened to Principle X clause 13 before feature 173 gated it.

The middle option nobody has costed: rule only on **new** pragmas (a gate check that the count may
not rise), leaving the 131 as a ledgered inheritance. That is cheap, it stops the drift, and it is
the same shape as the ratchets this feature just removed - which is why it is offered as a
possibility rather than a recommendation.

---

## THE GM RULED, 2026-08-31, and this is what carrying it out found

> *"If there is `# pragma: no cover` code that cannot happen then we should delete all of those
> cases, because dead code is bad, and it's better to remove it from the codebase."*

**The census above could not answer this by itself, and the method matters more than the count.**
Classifying by what each pragma's comment CLAIMS is not evidence - a comment is an assertion about
the code, written once and never re-checked. So all 131 were STRIPPED and the whole corpus run
against the new 100% floor, which then named every line nothing executes. That is the only reading
that is measured rather than asserted, and it inverted the picture:

| | |
|---|---|
| pragmas that were hiding lines the corpus ALREADY runs | **78** - stale, protecting nothing |
| genuinely unreached | **53** |

Reading the comments alone would have deleted live code and kept dead code.

### Counted in ONE unit, because the first draft of this section mixed two

Round 6 of `spec-fidelity` caught it: a "78 stale / 53 unreached" pair matched pragma COMMENT LINES to
uncovered STATEMENTS through a +/-2 line window, and did not reconcile with the tree - one pragma on a
`class` or a block hides many lines, and the well ring-probe rescue alone is 27 comment lines. In
coverage's own unit:

| | |
|---|---|
| excluded lines before | **469** |
| ...still uncovered when ALL exclusions were stripped | **113** |
| **exclusions hiding lines the corpus ALREADY runs** | **356** |
| dead sites found and DELETED | **13** (40 engine lines) |
| pragma comment lines | **130 -> 76** (131 grep hits less one prose mention in `tools/hamlet_floor.py`) |
| excluded lines after | **SUPERSEDED by the 2026-09-02 widening - see spec SC1 for the current 77 comment lines / 398 excluded of 22,520.** As measured for THIS pass: **385** counted over the filesystem tree, **327 of 20,682 (1.58%) inside the MEASURED set** - round 8 caught the census counting files coverage never reports, which is why two of its "largest" entries (`tools/cache_audit.py`, `pipeline/gencache.py`) are outside `[tool.coverage.run] source` altogether; inside the floored tree 281 of 9,118 (3.08%) -> 216 of 9,168 (2.36%) |

### What the genuinely-unreached turned out to be

| | disposition |
|---|---|
| a guard re-testing a filter one loop above it (`hamletgen/frame.py`), an enum check after the enum is exhausted, `return None` after a loop that always returns, `if not plots` before code that handles empty | **DELETED** - 13 sites |
| error handling and structural terminals: `if not pts: continue` stands before `len(pts)`, so removing it converts a graceful skip into a crash; several are a terminal return where the signature promises a value; three are a predicate's REJECTION, where removal changes the answer | **KEPT**, each carrying why it is not deletable |
| live rescues and external systems - the well ring-probe rescue, the least-bad brook route, the real AWS transport. *"no cohort map currently"* is "today's seeds miss it", not "cannot happen" | **KEPT** |

2,716 tests pass and no map manifest moved, which is the evidence the deletions were safe: every
deleted line was reached by nothing, on any seed the corpus rolls.

### A residue this pass did NOT fix, named so it is not rediscovered

The restored exclusions are **block-scoped and therefore over-broad**: 385 lines are excluded where
only ~73 are genuinely unreached (the 113 was measured BEFORE the 40 deleted engine lines went),
because a pragma on a rescue routine or a transport class covers
the executed lines inside it as well. That was true before this feature and is still true. Narrowing
each to the lines actually unreached is available work; it is not what the ruling asked for.

**The open half, which is the GM's**: whether the 24 error-handling guards are also meant. Deleting
those trades a silent skip for a crash on malformed input. That is a real trade rather than a
cleanup, so it was not assumed in either direction.
