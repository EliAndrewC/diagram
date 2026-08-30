# The GM's request, verbatim and unedited

This file is the authority for `spec.md`. Nothing here is paraphrased.

---

Our linting is set to autocorrect, isn't it?  I mean, usually, the reason to do linting first is because you want to catch lint failures before you waste a lot of time running unit tests.  However, in this case, I don't think it actually matters, does it?  I mean, yes.  On general principle, we should probably make linting go first.  So you can go ahead and do that reorder, but I don't think that it will yield an efficiency improvement.  It also sounds like the firing log should record more data for us to be able to use to make improvements in the future.  So please add that.  I agree that the gate getting slower is the most important thing, but I will hand that off to a different session. to work because I already have a session working on improving the efficiency of our unit tests.  So please do the other two things, and I have already written down your findings about the make done times.  So I believe I have everything that I need there.  Thanks.

---

## What the two things are, from the message the GM was answering

The session reported three known-and-unfinished items and asked which to take:

1. **The gate rolls a 29 s reference map before it runs 1.8 s of lint/format/typecheck** -
   `specs/162-guard-block-economics/research.md` R7. **HANDED OFF? No: the GM says do it.**
2. **The firing log covers 2 of 12 guards** - `batching` fired 119 times in six days, more than every
   other guard combined, and records nothing (`specs/162-guard-block-economics` FR-006, R6).
   **The GM says add it.**
3. **The gate's median has risen from 35 s to 148 s in three days, unexplained.** **NOT this session's
   work**: the GM is handing it to a session already working on unit-test efficiency, and has the
   findings already.

## The GM's premise, checked before anything was specified

*"Our linting is set to autocorrect, isn't it?"* Yes: the gate's `lint` phase runs
`ruff check --fix` and its `format` phase runs `ruff format` (not `--check`). And the GM's conclusion
follows from the record - of 317 recorded gate runs, only **8** failed on a static phase alone
(3 format, 2 lint, 2 typecheck, 1 lint+typecheck), so the reorder recovers about **4 minutes across
the whole history**. It is done on principle, and this spec says so rather than claiming a saving.
