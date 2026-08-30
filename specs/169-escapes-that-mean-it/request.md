# Feature 169 - the GM's request, verbatim

The GM asked, 2026-08-30, after feature 168 landed:

> Good to know. Thanks. Are there any other improvements that we are aware of which have come up in
> our session related to our tooling? This should include anything involving our Claude Hooks or our
> makefile and its logic about what to run and in what order, etcetera.

The session answered with five verified findings (the answer is reproduced in `research.md` R0, since
it is what "these fixes" refers to):

1. every guard's escape token matches a MENTION, not an invocation - and `measure` and `gate` also
   reset their state on that branch, so a command that merely mentions the token disarms them;
2. `scripts/test-review-gate.sh` writes its fixture firings into the live census (24 of 113 entries);
3. `guard-file`'s `reminded` branch records no rule slug, and the static test's `multi` set omitted
   several guards, so nothing caught it - plus that reminder fired 56 times in one day;
4. `sync-with-main.sh sync-in` reports success when the mirror carries a commit GitHub main does not
   have, while `CLAUDE.md` documents it as refusing with "mirror cannot fast-forward";
5. the bare-`cd` trap now has a shape narrow enough to enforce - a `cd` into the MIRROR ROOT in a
   command that then writes or commits - which is the condition `CLAUDE.md` set for reopening it.

The session recommended 1, 2, 3 and said 4 and 5 each wanted the GM's own decision, since 5 is a hook
the GM had priced and declined once before. The GM replied:

> Yes please make these fixes as their own feature, test them out, and then close out the feature and
> push back to main when you're done.
