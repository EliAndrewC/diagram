# Request - feature 285

The GM, 2026-09-28, answering the session's suggestion (below):

> I agree with your suggestion that if we are marking things as guesses, then a make target which assembles a list of guesses that could use a research pass is better than trying to assemble something by hand, which then will drift out of date due to repeating ourselves in multiple places. So yes, please go ahead and implement that as a new makefile target.

The question that led to it, the GM the same day: "Is that deficiency documented as something that needs another research pass? Like in our list of open questions that research has not yet settled? I mean, do we have that kind of a list right now?"

The session's suggestion it answers: "Every guess and every 'no public source' note already has to carry its label, so a `make open-questions` target could collect them across the whole record: the question, the entry, what was searched, and which map feature depends on it. It would never drift out of date, because closing a guess in the record removes it from the list."

The motivating case: the rack length per household (research homesteads 500 and 505) is a labeled GUESS that no list surfaced.
