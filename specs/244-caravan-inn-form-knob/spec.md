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

**What is true of the pool today, stated because it shapes every requirement below.** No scripted
generator draws an inn. The six callers of the glyph are all hand-authored legacy generators - three
towns, three provincial cities - which are frozen and never re-run, so a per-settlement roll has no
site to live in yet. The knob therefore lands in two halves: the GLYPH takes the form now and draws
both, and the ROLL is specified on the research page in the form feature 229 reserves for a rule no
generator yet encodes, to be picked up by whatever feature scripts the town tier.

## Functional requirements

**FR-001 - the glyph takes a `form`.** `inn()` in `settlement/civic_grounds/lodging.py` accepts
`form="wagon" | "hatago"` and draws each from its analogue: `wagon` as the single-story building the
glyph is today; `hatago` with a second story that reads as one at map scale. Any other value is refused.
The record it writes to `M["buildings"]` carries the form, so a page or a check can tell them apart.

**FR-002 - the default is `wagon`.** The frozen legacy callers pass no form, and the GM's 2026-09-12
ruling stands for the analogue those towns were drawn from; a default of `hatago` would silently move
what they mean without re-rendering them. The default is a recorded decision (D1), not an accident of
argument order.

**FR-003 - the roll is SPECIFIED where the future generator will find it.** `research/towns.html`'s
caravan-inn section carries a `<p class="spec">` opening *The rule the map follows:* stating that a
town's inn takes one of the two forms, rolled from the map's own seed like every other knob, with no
bias between them the record would justify. It names no engine identifier in visible text; the
parameter name is in a comment beside it.

**FR-004 - the research page states both forms as ACCURATE to their analogues, and labels what is
not attested.** The section says the wagon inn is single-story on fn-25 and the hatago two-story on
fn-26, that a large stable behind a Japanese travelers' inn IS attested (the umayado usage example, to
be footnoted from 238's R2a reading), and that nothing read describes a cart yard or a feeding trough
at a hatago - so a `hatago`-form inn standing beside the town's cart yard is that much GUESS, and the
page says so rather than letting the glyph imply it.

**FR-005 - the docstring is the record at the point of change.** `inn()`'s docstring names both
analogues, the ruling and its date, and the default's reason, and drops the sentence saying the
question is open - it is not open any more.

**FR-006 - the checks the changed material owes.** `quote-check` and `record-format` over the changed
section of `towns.html`; any new footnote's key already judged by `source-applicability` in 238
(`okabe-hatago-jawiki`) or judged here if new; `scripts/_entry_owed.py` consulted, though no modal
class is written from this section today.

**FR-007 - verification without a live map.** The knob rule owes one map per knob value, and no live
map draws an inn. So each form is rendered and asserted by a unit test of the glyph - the second story
present in one and absent in the other, the record carrying the form, the refusal of a bad value - at
100% coverage of the changed code, and `make done` is green. The legacy renders are checked UNCHANGED
by the gate's own pool phase, which is what "frozen" means.

## Success criteria

- **SC-001** (FR-001, FR-002) - calling `inn()` with no form, with `wagon` and with `hatago` produces
  the recorded form `wagon`, `wagon` and `hatago` respectively, and any other value raises.
- **SC-002** (FR-003) - `towns.html` carries exactly one `<p class="spec">` for the inn's form under
  its caravan-inn heading, in the reader's terms, engine names in comments only.
- **SC-003** (FR-004) - every assertion the changed section makes carries a footnote in one of the
  three forms, and `quote-check` returns READABLE / VERBATIM / SUPPORTS for each new one.
- **SC-004** (FR-005) - the docstring names both analogues and both rulings with dates, and no longer
  calls the question open.
- **SC-005** (FR-006) - the verdicts are recorded in the task.
- **SC-006** (FR-007) - `make done` green with the changed lines at 100%, and no legacy render or
  manifest differs from main.
- **SC-007** (spec-wide) - the push lands with `_entry_owed.py` naming no unanswered pair.

## Decisions recorded

**D1 - the default form is `wagon`.** Six frozen callers pass no form. Their towns were drawn against
the wagon-inn analogue and the GM's 2026-09-12 ruling stands for that analogue; changing the default
would change what those maps MEAN with no re-render to show it. The alternative - no default, every
caller names a form - was priced: it edits six frozen generators that are never re-run, to no visible
effect. Declined.

**D2 - the roll is specified, not implemented.** There is no scripted town generator to roll in.
Feature 229's `<p class="spec">` form exists for exactly this - a rule the future generator must
satisfy - and the class attribute is how that feature finds every rule it owes. Rolling inside `inn()`
itself was priced and declined: a glyph does not own a seed, and a knob rolled below the plan is a knob
no manifest records and no test can pin.

**D3 - no bias between the forms.** The record attests both and says nothing about how common either
was; R2a's reading found "commonly two-story" NOT attested for hatago and a mixed streetscape at
Seki-juku. An even roll is the honest reading until a source says otherwise, and the spec paragraph
says so.

**D4 - the `hatago` form keeps the stable and the cart yard, labeled.** The layout rule (inn fronting
the road, stable behind, ground for the animals) is the town's, not the inn's, and the Japanese
umayado arrangement attests a large stable behind a travelers' inn. The cart yard and the feeding
trough are attested only at the wagon inn, so under the `hatago` form they are a GUESS and FR-004 says
so on the page. The alternative - a `hatago` town drops the cart yard - changes a placement rule this
feature was not asked to touch. Declined, and named here so the next tier can take it up.

## Review history

- **Round 1**: pending.
