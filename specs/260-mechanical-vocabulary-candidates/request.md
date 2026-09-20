# The GM's request (verbatim, 2026-09-20)

<!-- SOURCE: GM NOTES -->

Sent after feature 259 landed with SC-002 recorded as NOT met, and after the session explained the
decision that failure left open.

> Please explain the decision you're asking me to make.

and, on the explanation:

> Go with your recommendation, thanks.

<!-- /SOURCE -->

## The decision, as it was put to them

The question: **what should count as proof that a cheaper check is still a good check, when the check's
output varies between identical runs?**

Three runs of `record-format` on one entry (`specs/259-*/research.md` R5) agree on eight terms and
differ in the tail - in both conditions, including the one that reads more. So "it reports the same
findings", which features 258 and 259 both wrote into their specs, is a bar no pair of runs can clear.

Four options were put to the GM. They chose **C**, the session's recommendation, quoted here as it was
written:

> **C. Remove the variance at its source - my recommendation.** The reason the model's choice wanders is
> that it is doing two jobs at once: noticing which words a reader might not know, *and* judging them.
> The first is mechanical now that the glossary is an index: every word in the entry that has no variant
> line is a candidate. `make record-prepass` already exists to do the mechanical half first - but on this
> entry it reports **0 candidates**, because it does not do this. If it listed the unmatched words, the
> model would judge a fixed list instead of noticing an open one, and two runs would differ much less.

and the shape the session said it would take:

> the prepass emits every word in the entry with no line in `glossary-variants.txt`, the contract tells
> the agent to rule on that list and to add anything it notices beyond it, and the acceptance bar becomes
> "every candidate the prepass raised is ruled on" - which is checkable, unlike "the same findings."

The rejected three, so that a reader knows what was not chosen: **A**, a stable core plus a declared
tail; **B**, a union over k runs; **D**, dropping the findings criterion and judging on bytes alone.

## What the session measured immediately after, which changes the shape

"Every word with no line in the index" does not work, and the spec says so rather than quietly
narrowing it: on the entry in question it raises **314 of 324 distinct words**, because ordinary English
is not in a glossary. The filter that does work needs no shipped word list - rarity within the record's
own corpus - and it is measured in R2. The GM chose the PURPOSE (move the noticing into the script so
the model rules on a fixed list); the mechanism is what the measurement decides.
