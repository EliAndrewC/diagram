# Recording decisions: what was actually decided, and what is still open

**Load this file when:** You are about to build on a property of the engine nobody decided, or you are leaving a decision open for a later session.

Split out of [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md) so it is not in every diagram session's
context. The text is verbatim; the short always-on version of each rule stays in the index.

## A side effect is not a rule - check what was actually DECIDED before you build on it

The toe marsh spanned the canvas edge to edge for weeks, and three separate pieces of work treated
that as the settled shape of wet ground: a routing rule, four re-routed connectors, and a claim to
the GM that "a real valley floor has a dry footslope on at least one side" offered as though it were
research. The GM asked where both halves came from. Neither survived:

- **The width was never decided.** It arrived with the 2026-07 fix that made the toe a CONTOUR band
  so it would rotate with the fall - that fix was right and the rotation was its point; the extent
  came from the canvas corners because that was the easy way to write the polygon. The only stated
  rule was `marsh_on_low_ground` (the marsh is downhill of the field), and this file's own Akagahara
  note already recorded the opposite of wall-to-wall wetness: low ground beside the drain that sits
  at rice height is DRY, and "do not fix the gap".
- **The justification was invented.** The footslope claim was a plausible-sounding generalization
  with nothing behind it. Under the record-the-why rule that makes it not a finding at all.

The research the GM then asked for settled it in the opposite direction from the code, and the fix
is now in `research/questions/0057-marshes-and-wetlands-shitchi.html`: an alluvial fan's spring line
follows the FAN's toe, and a floodplain's backswamp is bounded by its natural levees - wet ground is
FEATURE-bounded in both landforms. `toe_band` derives its width from the ground the fan waters.

**Two transferable rules.** First, when a feature's extent comes from the CANVAS, suspect it: a
canvas is not a fact about the world, and every other feature here is derived from something on the
map. This is `feedback_derive_dont_pin` one level up - not a pinned coordinate but a pinned FRAME.
Second, and more expensive: when you are about to build on a property of the engine, check whether
anyone decided it. Two of the four connector re-routes it caused were pure waste - restored to their
original routes the same day, once the width was right - and they were re-routes of the GM's own
maps, each with a review pass spent on it.

## An OPEN DECISION carries an implementation sketch, not just the question

When a session deliberately leaves a rule undecided ("no bank-margin rule exists; if the GM wants
one, that is its own rule with its own research entry"), the entry recording the open decision
MUST also record the 2-3 line implementation sketch the deciding session would execute: WHERE the
change lands (the call site), WHAT holds it (the check or test to extend), and the deliberate
exclusions. The open decision's author has all three in their head at zero marginal cost; the
follow-up session re-derives them at full cost. Measured 2026-08-16: the cut-bank follow-up spent
its single largest LLM turn (75s) plus part of its diagnosis re-deriving exactly what the
open-decision author knew - the commons scatter's `wat_b` grid was the landing site, the
drawn-channels margin test was the one to extend, streams/marsh were the exclusions.
`research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.drawing.html` carries the retro-fitted worked example.

## Before asking the GM

Do not ask the GM what our own documentation answers, nor what history can answer (two answers make a KNOB): both rules
are repository-wide and live with the research ladder in
[`docs/research-doctrine.md`](../docs/research-doctrine.md) ("Do not put a question to the GM that our documentation or
history already answers"). The engine-side corollary follows.

## WHEN A FORM IS A KNOB, CHECK THAT BOTH FORMS CAN ACTUALLY DO THE JOB

Feature 123 rolled a `lane_web` knob over two attested forms - `alleys` (laterals off a spine) and
`back_lane` (ways parallel to the field margin behind the plots) - and shipped a first version in
which one of them could not possibly work.

**Parallel lanes never meet.** That is arithmetic, not a bug to tune around, and it means the
back-lane form was disconnected BY CONSTRUCTION: an alley crosses the spine it branches from, a back
lane runs beside its neighbor forever. Three settlement-reviews independently reported the maps
rolling `back_lane` as two and three separate lane components while the `alleys` maps came out fine,
and the knob is exactly why the defect landed on some maps and not others.

The source had already said what was missing, in the same sentence the form was taken from: the
planned form is back lanes "which, **together with the main street itself, provides a rectangular
FRAMEWORK** for the development of the village". A framework is the parallels PLUS the ties. Only the
parallels were being drawn.

**Two transferable rules.**

- **A knob multiplies your test surface, and the halves are not symmetric.** Both values need the
  same functional property demonstrated - here, "the ways form one network" - and a green cohort
  proves it only for the values that happened to roll. Ask what each form makes STRUCTURALLY
  impossible before trusting the rate.
- **Re-read the source sentence the form came from, in full, when the form misbehaves.** The clause
  that fixed this was in the same quotation the feature was built on, and had been skimmed past as
  scene-setting. A form taken from a source usually arrives with its own constraints attached.
