# 191 - Refusals that tell the truth

**Status**: FAITHFUL at review round 3; implemented
**Request**: [request.md](request.md) (the GM's words, verbatim)
**Investigation**: [research.md](research.md) (FR-000)

## Why

Retiring `make reference` as a public rung (2026-09-06) left PRINTED messages in engine Python and
in the Makefile naming a target that no longer resolves. A refusal that sends a session to a failing
command is the defect class `test_operations_registry.py` caught the same day with `citybudget`, and
it is worse here: `_invocation.guard()` is the make-only guard, so its message is the first thing a
refused session reads.

Reading the sites found more rot than the original report. The `_invocation.py` ladder is stale in
**three** ways:

| what it says | why it is wrong |
|---|---|
| `make reference    ~26 s` | the target does not exist; `make reference` errors |
| `make quick        ~33 s` | feature 162: a guard message may not state how long a command takes |
| `make done ~75 s locked / ~4.5 min unlocked` | states durations AND cites the SCOPE LOCK, retired entirely by feature 185 |

**And the guard meant to prevent the duration half never looks at this file.**
`tests/tooling/test_guard_message_durations.py` scans `SCRIPTS = REPO / "scripts"`. The make-only
guard has two halves - `scripts/make-only-hooks.sh` and `l7r/diagram/_invocation.py` - and only the
shell half is covered, which is why the shell ladder is clean and the Python one rotted. Same shape
as the bug that opened the day: a rule censused over the surface where it was first written rather
than over every place the mechanism lives.

## Requirements

- **FR-000** The gate slowdown the GM named first is investigated and the finding recorded in
  [research.md](research.md). Any code change it implies is a SEPARATE feature; this one carries the
  investigation only. *(Delivered: heterogeneous cores, a 2.2x measured spread, a 285 s
  single-threaded tail, and no regression.)*
- **FR-001** The text of `_invocation.guard()`'s ladder lives in a DOCSTRING and is printed from it
  (`__doc__`), per D1. It names only targets that resolve; `make reference` is gone from it.
- **FR-002** That ladder states no durations (feature 162's rule, which already binds every shell
  guard).
- **FR-003** That ladder contains no scope-lock vocabulary ("locked", "unlocked").
- **FR-004** `hamlet_floor.check()`'s empty-path message likewise lives in a docstring, printed from
  it, and names a live target as the producer of the first roll record.
- **FR-005** `test_guard_message_durations.py` covers Python guard messages as well as `scripts/`.
  **The covered set is DERIVED BY AST from the tree** - every `.py` under `l7r/diagram/` containing a
  call to `print` or a write to `sys.stdout`/`sys.stderr` - **not** from `_invocation.OPERATIONS`,
  which is a hand-enumerated roster by its own docstring and which does not even contain
  `_invocation` (the guard module is not an operation). Stating the search space is the point:
  a derivation that misses the one file the requirement exists for is the failure this project has
  now made four times.
- **FR-006** The extractor must read Python string literals that reach an output call, and
  docstrings **only where that docstring's `__doc__` is itself referenced by an output call**
  (`X.__doc__` flowing into `print` / `sys.std*.write`). The existing `emitted()` parses shell only
  (`_HEREDOC`, and `echo|printf|block`); pointed at a `.py` it returns nothing and would pass green
  for ever. FR-001/FR-004 move the text INTO docstrings, so a scanner blind to docstrings would be
  blind to this feature's own output.
  **The narrowing is load-bearing, not fastidious.** A file-granular rule would sweep in
  `_invocation.py`'s MODULE docstring, line 3, which reads *"the fast path already existed -
  `make reference` answers in ~60 s"* - matching both the duration pattern and the command pattern.
  That line is historical record, protected by SC-001 and by the third out-of-scope bullet, so a
  file-granular FR-006 would turn the gate red on text this spec promises not to touch, and the
  natural "fix" would be to edit protected history. The `__doc__`-is-printed test distinguishes
  them: the ladder's docstring is printed, the module's is not.
- **FR-007** `Makefile:988` - the `_reference` failure path printing
  `(reference only under the lock)` - loses the retired-lock vocabulary. It is printed, on a path
  every gate runs, in the target the retirement created.
- **FR-008** Every target named in any message this feature touches resolves as a make target,
  asserted by a test.

## Out of scope, stated so it is not read in

- Acting on the slowdown. FR-000 records it; what to do about a variance-blind ratchet belongs to
  its own feature with the GM's ruling (research.md R5).
- `specs/189` - the GM reassigned it: *"I will have the other session handle that."* (Since
  confirmed done and merged.)
- Historical record. `_invocation.py:3` and `tools/hamlet_floor.py:54` mention `make reference` in a
  module docstring and a comment recording history. The duration guard's own docstring says *"A
  comment recording history ... is not a message and is not judged"*; these are untouched.
- Rewording beyond FR-001..FR-004, FR-007. The messages are well written; some facts in them are stale.

## Decisions Recorded

- **D1 - the GM's docstring suggestion is ADOPTED. My first-round objection was wrong.** I wrote
  that "a docstring is not printed"; the GM replied *"They are printed if you print them."* They are
  right, and this repository already does it - feature 189 the previous evening made `cls.__doc__`
  the displayed prose (`interactive/classes/_base.py:207`; `classes/CLAUDE.md`: *"The explanation IS
  the docstring"*). Two further things measured rather than assumed:
  - **It buys a permanent benefit.** `gate-stamp.semantic_bytes` strips docstrings, so once the text
    lives in one, every FUTURE correction to it is AST-identical: DIRECT route, no spec-kit feature.
    Verified on synthetic inputs - a docstring-only edit yields the same key, a string-literal edit
    does not. This is precisely the rot that made this feature necessary.
  - **The benefit is real HERE, and is not automatic in general.** Feature 189 had to add
    `classes/*.py` to `gate-stamp.RAW_AREAS` so page prose WOULD still key the gate. Measured:
    `RAW_AREAS == frozenset({"page"})`, and `_invocation.py` and `tools/` are not in it, so their
    docstrings are stripped and the exemption holds. `request.md`'s claim that a docstring edit
    avoids a feature is corrected to say so per file rather than in general.
  - **189's own D4 rule cuts toward the GM**: a docstring carries text visible in the interface, a
    string constant carries a record. A refusal ladder is visible output.
  - **Per site**: `_invocation`'s message is a template (three interpolations plus ANSI), so only the
    STATIC ladder moves to a docstring and the interpolated header stays an f-string.
    `hamlet_floor`'s is one static line, where the objection never applied at all.
- **D2 - the duration guard is WIDENED rather than the message exempted.** Fixing the text alone
  costs nothing today and re-rots on the next edit.
- **D3 - `make maps` is the replacement pointer, not `make _reference`.** `_reference` works, but it
  was made internal ON PURPOSE hours earlier; teaching sessions to type the internal name would undo
  that through the back door. `make maps` is public and does roll the reference alone after a
  failure. (`test_operations_registry.py`'s target regex `^([a-z][a-z0-9-]*):` cannot match a
  leading-underscore target either.)

## Success Criteria

- **SC-001** No message PRINTED by `l7r/diagram/` or the Makefile names `make reference`. Comments
  and docstrings recording the HISTORY of the retired rung are untouched and are not judged.
- **SC-002** Every command named in `_invocation.guard()`'s output resolves as a make target.
- **SC-003** `test_guard_message_durations.py` FAILS if a duration is planted in `_invocation.py`'s
  PRINTED ladder docstring - proven by planting one and watching it go red, per the add-a-guard
  rule - and does NOT fire on `_invocation.py:3`, the module docstring recording history, which
  already contains both a duration and `make reference`. Both halves are asserted: a guard that
  cannot tell a message from a record is one that gets switched off.
- **SC-004** `make done` green, 100% coverage held. Note `tests/tools/test_hamlet_floor.py:87`
  asserts `"make reference" in out.getvalue()` and MUST move with the message (reviewer's aside).

## Review history

- **Round 1 (`spec-fidelity`): CHANGES REQUIRED.** Five items, all accepted and all fixed above:
  (1) the gate slowdown was missing from the artifacts - now FR-000 with research.md; (2) SC-001 as
  drafted would have failed on two historical mentions the spec's own out-of-scope clause protects -
  rewritten to judge PRINTED messages only; (3) FR-005's derivation was drawn from
  `_invocation.OPERATIONS`, a hand roster that does not contain `_invocation` itself, so it would
  have missed the very file the requirement exists for - replaced with an AST derivation and an
  explicit search space; (4) D1's stated ground was measurably false, and feature 189 had established
  the opposite pattern the previous evening - the suggestion is now ADOPTED; (5) a third stale
  printed message at `Makefile:988` - now FR-007. The reviewer also flagged that
  `test_hamlet_floor.py:87` will break, carried into SC-004.
- **Round 2 (`spec-fidelity`): CHANGES REQUIRED**, two narrow items, both accepted:
  (1) `request.md` still carried the DECLINED decision while D1 claimed it had been corrected - the
  worst class of finding, a permanent record preserving the behavior the GM asked to change and
  reading as caution. Rewritten below the GM's verbatim quote, which is untouched (Principle V), and
  the routing claim is now stated per FILE - it holds for the two files here because area `diagram`
  is not in `RAW_AREAS`, and does not hold for `interactive/classes/*.py`, which 189 deliberately put
  there. (2) FR-006 at file granularity would have fired on `_invocation.py:3`, protected history
  containing both a duration and `make reference` - narrowed to docstrings whose `__doc__` is
  actually printed, with SC-003 asserting both halves.
  The reviewer also independently confirmed: the AST derivation does cover both target files (31 of
  212 files selected; the 181 excluded contain no console-output route), an untruncated sweep of the
  whole engine and both Makefiles finds exactly the three printed sites FR-001/004/007 name and no
  others, `RAW_AREAS == frozenset({"page"})`, and the reverted ratchet left `baseline=310` unweakened.
- **Round 3 (`spec-fidelity`): FAITHFUL.** *"Implement it."* The reviewer re-verified that the
  GM's quoted words are byte-identical and nothing from the declined position survives, that
  FR-006 as worded excludes `_invocation.py:3` while still covering the ladder (applied
  mechanically, not read), and that both SC-003 halves are assertable against the existing
  `_DURATION`/`_COMMAND` patterns. Two asides carried into implementation: the ladder is written by
  `assert_via_make()` rather than `guard()`, and FR-008 must check only the STATIC ladder because
  `ci/__main__.py` passes a free-form ROUTE as `{target}`.
