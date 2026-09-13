# Feature 239 - the GM's request, verbatim

Asked after feature 236's second amendment landed, having been told it took about three and a half
hours (2026-09-13):

> Okay, so let's talk performance and timing and procedures. The work here which was basically "make
> our hook do the correct thing for sed commands" and it took about 3 and a half hours, right? So
> break that down for me. I feel like we need even more fixes to our tooling if this round of changes
> took so long. Am I wrong? Give me some numbers on the breakdown of where all that time went.

The session answered with the census now recorded as `research.md` R1, and named three tooling gaps:
the guard's decision cannot be imported so measuring it costs a process per command; nothing freezes
the command window so every question re-derives it; and half the review findings were figures rather
than judgments. The GM's reply:

> Yes please spec those three as a new feature. Additionally, if you had waste from handing the
> reviewer numbers you hadn't derived reproduceably then is there a possible tooling or procedure
> change there? Like maybe a reviewer, when asked to look at that category of numbers, should exit
> immediately if given the numbers directly and should instead be given either a file containing
> measurements with how they were generated i.e. the reproduceable command which systematically
> generated them, or something? I'm just spitballing here, maybe this isn't a good idea, but anytime
> we make the same mistake repeatedly it's worth thinking about the tooling changes that might fix
> things.

So: three items the session proposed and the GM approved, plus a fourth the GM proposed - and the
fourth is put as a question ("maybe this isn't a good idea"), which this spec answers with the record
rather than with a preference (`research.md` R2, R5).

## The GM's ruling on the five-round escalation (2026-09-13)

The spec reached its five-round cap with round 5's three items applied, and the session escalated with
three options: accept it as it stands, run one more round, or change FR-011c. The GM, verbatim:

> I accept the spec as it stands, so please proceed.

## The GM's ruling on the cost to older specs (2026-09-13)

Told that with no scoping, 134 of the 156 existing specs would owe keys or labels on their next edit,
and offered a narrower form that checks only the paragraphs an edit changes, the GM, verbatim:

> I'm not worried about older specs; we don't usually edit older specs so that's fine.

So the narrower form is not built, and check 5 applies to every spec an edit touches.
