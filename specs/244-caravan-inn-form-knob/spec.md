# Feature 244 - the caravan inn's FORM is a knob

**Status:** specified; awaiting a FAITHFUL verdict (see Review history).

## Summary

The GM ruled on 2026-09-12 that a two-story caravan inn was a mistake, *"if our attested analog reads it
as a single story"*, and on 2026-09-13, told there are now two attested analogues pointing opposite
ways, that *"if there are opposing sources then it's a toggle."* So the inn's FORM becomes a knob with
two values, each drawn from its own attested analogue: **`wagon`**, the north-Chinese wagon inn,
single-story; **`hatago`**, the Japanese post-station inn, two-story. Constitution XII's rule applies
exactly - two forms the record supports, not a degree along a continuum, so a knob rather than a
choice - and its reason is the project's: two towns that may honestly differ should.

**The knob is ROLLED, in the glyph, from the map's own seed.** The engine already does this for a
form knob three files away: `byre_form` is registered with two values and a default, resolved inside
the drawing method by `Settlement.resolve()` - pinned, else rolled from the seed, else the default -
and declared to the manifest's `meta` so the gate can hold the drawing to it. `caravan_inn_form`
takes that shape exactly. A first draft of this spec deferred the roll to a future town generator on
the ground that a glyph has no seed; the review found the precedent and the deferral was withdrawn
(D2).

**Who calls the glyph, stated because it shapes the default.** No scripted generator draws an inn.
Seven files call it: six hand-authored legacy generators under `legacy-hand-authored-pool/` (three
towns, three provincial cities), which are frozen - never regenerated and never re-gated - and one
DRAFT capital under `wip/`, parked out of the pool until it is green and re-run by whoever picks it up.
None of them passes a form, so on any of them that is ever re-run the knob rolls.

## Functional requirements

**FR-001 - the knob.** `caravan_inn_form` is registered in `settlement/_knobs.py` with the values
`wagon` and `hatago` and the default `wagon`, beside `byre_form` and in its shape. The registration
carries the why: two attested analogues, opposite on the one question, the GM's two rulings with
their dates, and the record's silence on how common either was.

**FR-002 - the glyph draws both, and resolves the knob when the caller pins nothing.** `inn()` in
`settlement/civic_grounds/lodging.py` takes `form: str | None = None`. A caller that passes a form
pins it (any value outside the knob's is refused); a caller that passes none gets
`self.resolve("caravan_inn_form")` - the map's pin if it has one, else the roll, else the default.
`wagon` is the single-story building the glyph draws today; `hatago` carries a second story that reads
as one at map scale. The resolved form is written to `M["meta"]["caravan_inn_form"]` once, as
`byre_form` is, and to each inn's record in `M["buildings"]`, so a page or a check can tell the forms
apart without re-reading the SVG.

**FR-003 - the roll is stated on the research page as the rule the map follows.** The caravan-inn
section of `research/towns.html` carries a `<p class="spec">` opening *The rule the map follows:*
saying a town's inn takes one of the two forms, rolled from the map's own seed with no bias between
them, and that a map may pin one. It names no engine identifier in visible text; the knob's name is in
a comment beside it.

**FR-004 - the research page states both forms as ACCURATE to their analogues, labels what is not
attested, and stops calling the question open.** The section says the wagon inn is single-story on
fn-25 and the hatago two-story on fn-26. On what stands beside a `hatago`-form inn it says exactly what
the record bears (`research.md` R1): that a Japanese inn keeping travelers' horses was a named kind of
place - the dictionary's definition of 馬宿, to be footnoted from kotobank's Seisenban Nihon Kokugo
Daijiten entry, public - and that the front-inn, back-stable picture rests on that dictionary's
earliest cited example, a sentence from a 1913 novel; and that nothing read describes a cart yard or a
feeding trough at a hatago. So under the `hatago` form the stable is thinly attested and the cart yard
a GUESS, and the page says so. The sentence *"whether it is the better analogue for a wagon inn is an
open question and not a settled one"* and the `<!-- Evidence: -->` line calling it a cross-class
question still open are REPLACED by the ruling: both are analogues, one per knob value.

**FR-005 - the docstring is the record at the point of change.** `inn()`'s docstring names both
analogues, both rulings with dates, the knob and its default's reason, and no longer says the question
is open.

**FR-006 - the checks the changed material owes.** `quote-check` and `record-format` over the changed
section of `towns.html`; `source-applicability` over the one new registry key (the kotobank 馬宿 entry;
`okabe-hatago-jawiki` was judged in 238); `scripts/_entry_owed.py` consulted, though no modal class is
written from this section today.

**FR-007 - verification.** The knob rule owes one map per knob value. No live pool map draws an inn, so
the maps are the test's own: a settlement pinned to each form renders the inn and the test asserts the
second story present under `hatago` and absent under `wagon`, the form in `meta` and in the building
record, a bad value refused, and two seeds that resolve to different forms when nothing is pinned. The
changed lines are covered at the constitutional floor, which is total, and `make done` is green. The
frozen legacy renders are not re-checked by anything - frozen means never regenerated and never
re-gated - and this feature makes no claim about them beyond that it does not touch them.

## Success criteria

- **SC-001** (FR-001) - `caravan_inn_form` is registered with the two values and the `wagon` default,
  and its registration states the two rulings.
- **SC-002** (FR-002) - `inn()` with no form resolves the knob; with `wagon` or `hatago` pins it; with
  any other value raises; `meta` and the building record carry the form.
- **SC-003** (FR-003) - `towns.html` carries exactly one `<p class="spec">` for the inn's form under
  its caravan-inn heading, in the reader's terms, engine names in comments only.
- **SC-004** (FR-004) - every assertion the changed section makes carries a footnote in one of the
  three forms, `quote-check` returns READABLE / VERBATIM / SUPPORTS for each new one, and no sentence or
  comment in the section calls the analogue question open.
- **SC-005** (FR-005) - the docstring names both analogues and both rulings with dates.
- **SC-006** (FR-006) - the verdicts are recorded in the task, the new key judged before it is cited.
- **SC-007** (FR-007) - a test renders each form on a pinned settlement and asserts the difference; two
  unpinned seeds resolve to different forms; `make done` green.
- **SC-008** (spec-wide) - the push lands with `_entry_owed.py` naming no unanswered pair.

## Decisions recorded

**D1 - the default form is `wagon`.** A knob's default is the no-pin, no-roll fallback, as
`byre_form`'s is; with the roll in place it decides no map's form on its own. It is `wagon` because
the GM's 2026-09-12 ruling stands for that analogue and because the six frozen maps were drawn against
it - though the default can never change what THEY show, since nothing re-renders them. The one
caller that may be re-run, the `wip/` capital draft, passes no form and will roll, which is the ruling
working as intended on a draft not yet green.

**D2 - the roll lives in the glyph, WITHDRAWING the first draft's deferral.** The first draft specified
the roll on the research page only, for a future town generator, on two grounds: that no scripted
generator draws an inn, and that a glyph does not own a seed so a knob rolled below the plan is one no
manifest records. The first is true and irrelevant - `Settlement.resolve()` rolls on any settlement of
any tier. The second is false: `inn()` is a `Settlement` method with `self.seed` and `self.resolve`,
and `byre_form` is a form knob resolved inside a drawing method and declared to `meta`, three files
away. The review named the precedent; the deferral was a narrowing of *"it's a toggle"* to a toggle
nothing toggled, and it is gone. The `<p class="spec">` stays as the statement of the rule, not as a
substitute for it.

**D3 - no bias between the forms.** The record attests both and says nothing about how common either
was; 238's R2a found "commonly two-story" NOT attested for hatago and a mixed streetscape at Seki-juku.
An even roll is the honest reading until a source says otherwise.

**D4 - the `hatago` form keeps the stable and the cart yard, labeled.** The layout rule - inn fronting
the road, stable behind, ground for the animals - is the town's, not the inn's, and this feature was
not asked to touch it. Under `hatago` the stable rests on the 馬宿 definition and a 1913 literary
example (R1), the cart yard and feeding trough on nothing Japanese at all, and FR-004 says so on the
page. The alternative - a `hatago` town drops the cart yard - changes a placement rule the GM did not
raise. Declined, and named so the tier that scripts towns can take it up with the Minamiaizu 馬宿
farmhouse R1 points at.

## Review history

- **Round 1 (2026-09-13), `spec-fidelity`: CHANGES REQUIRED**, four items. (2) was the one that
  mattered: D2 deferred the roll on grounds the code contradicts - `Settlement.resolve()` rolls on any
  tier and `byre_form` is a form knob resolved inside a drawing method - so the deferral was a
  NOT LEGITIMATE narrowing of "it's a toggle"; the roll now lives in `inn()` (FR-001, FR-002, D2). (3)
  the caller census missed the `wip/` capital draft, a seventh file that is not frozen, and FR-007
  claimed the gate re-checks frozen renders when frozen means never re-gated; both corrected. (4) FR-004
  left the page calling the analogue question open; it now retires that sentence and its comment. (1)
  two `100%` figures with no key: restated as the constitutional floor, named rather than measured. The
  review upheld D4 and ruled D1 legitimate only as a fallback behind a real roll, which it now is. Also
  applied, from this feature's own R1: the umayado passage is a 1913 literary example cited for the
  word's sense, so FR-004 and D4 no longer say the stable is "attested" on it.
- **Round 2 (2026-09-13), `spec-fidelity`: FAITHFUL.** Every round-1 item verified against the code
  rather than the spec's account of it - the registration at `_knobs.py:298`, the in-method resolve at
  `byres.py:190`, the seven generator files, both sentences FR-004 retires found on the page. The
  ruling's condition (opposing sources on STORIES) is established by fn-25 and fn-26, and R1's
  softening of the umayado leg does not touch it. Two asides, neither a change: a test file is an
  eighth caller of the glyph, and FR-002's `form:` parameter is a pin channel beside `pin_knob`, which
  is within scope since no shipped caller passes one.
