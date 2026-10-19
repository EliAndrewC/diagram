# settlement/civic_grounds/ - the civic-grounds subsystem as a package

Split from one `settlement/civic_grounds.py` by feature 115 (constitution Principle X clause 13 - the cost being
managed is context-window tokens). **Load only the file the task calls for**; this index is the map.
`from .civic_grounds import CivicGroundsMixin` still resolves.

**This package was never ONE subsystem.** The file was a RESIDUE BUCKET - unrelated subsystems feature 025 left in one
file - so its modules are grouped by **what a session comes here to change**, not by theme, and are deliberately uneven
in size.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition itself; never add logic here |
| `civic.py` | institutional works - what a domain builds because it administers, as opposed to what its inhabitants build to live: `district`, the declarative named-region overlay (records only, draws nothing) |

Feature 392 retired the code only the frozen legacy maps called (the funerary and justice grounds, lodging, the stable
yard and its context, and the rest of the civic works); the commit before it holds it.

## Composition, and why it is in `__init__.py`

`CivicGroundsMixin` is `class CivicGroundsMixin(CivicWorksMixin)` with no members of its own. It exists ONLY so
`core.py` keeps its single import and `CivicGroundsMixin` keeps its position in the `class Settlement(...)` base list -
which means the partition here can be re-cut later without touching `core.py`.

Monkeypatching: patch the DEFINING module - the rule is [`../CLAUDE.md`](../CLAUDE.md)'s.

## The guard, and what it is for

`tests/settlement/test_civic_grounds.py` holds the composed-surface guard (feature 115): the pre-split members still
live as a SUBSET of what the composed class exposes, a second test that no two sub-mixins define the same name, and a
third that they all resolve on `Settlement` itself. Both breakage classes were proven to fire before the guard was
trusted (feature 115 T007/T017).

- **Subset, not equality** - an addition needs no bookkeeping. The direction that HIDES is a member going missing: an
  addition is visible in review, while a subtraction surfaces only when whichever generator happens to call it runs.
- **The census admits attributes, not just callables**, even though this class has none today. A
  constant is as easy to lose in a split as a method and much easier to overlook.
- **A dead-member pass here MUST count intra-file callers**: a cross-file census that excludes the defining file
  reports a member called only inside its own file as deletable (feature 115's pre-spec census did exactly that).
