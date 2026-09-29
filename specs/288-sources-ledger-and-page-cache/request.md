# Request - feature 288

The GM, 2026-09-29, the question:

> I have a question about the research that you were doing. Let's say that you download a source and then read it in order to look up one piece of information. Do you have a record that you have looked at that source if you end up not citing it? Basically, something that I'm trying to figure out is whether you end up reading the same sources over and over again, looking for different questions or something. Or even if I ask you to do a research pass in one session and then something is marked as being unsubstantiated, and then I ask you to do another research pass in a different session, will you likely end up rereading the same source without realizing it? Is that something that we need to protect against? Is that something that we would even be able to detect after the fact if it has been happening?

> And to be clear, I am also interested in whether or not cited sources keep getting reread over and over again in order to answer different questions, because that also would suggest that we should perhaps make a tweak to how we are doing our research in, in order to do it more efficiently.

The request, after the measurement ([`research.md`](research.md) R1):

> Okay, yeah. I like the idea of the cheap fixes that you have suggested so far. So please do make that small tooling change. Both of the cheap fixes, I mean. And does this seem like something that you should even wait for the sweep to be done before landing? Because it seems like this kind of thing could help with the sweep, couldn't it?

The two cheap fixes the session had suggested, as the brief that started this feature states them:
1. a sources-consulted ledger - one line per source read, with the question and the outcome, printed before a page
   is fetched again;
2. a saved-page cache keyed by URL - a page saved once and found again, in place of the per-run scratch folders.
