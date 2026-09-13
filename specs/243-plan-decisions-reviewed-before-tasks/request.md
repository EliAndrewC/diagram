# Feature 243 - the GM's request, verbatim

Asked why feature 239's implementation took 42 minutes, the session found that a quarter of it was a
loop it caused: plan decisions that narrowed the accepted spec shipped without the independent
Principle XVI check, the escalation filter caught the omission after landing, both decisions were
overruled, and the fix needed a second gate, push and review cycle. It proposed:

> A plan-stage gate could refuse to let tasks be ticked while a plan decision marked as narrowing the
> spec lacks a recorded Mode 1 verdict. It would work like the existing push-time review gate for specs.
> It's small, and would have saved most of the last 11 minutes. Want it as a feature?

The GM, verbatim:

> Yes please implement the plan-stage gate as a feature, thanks.
