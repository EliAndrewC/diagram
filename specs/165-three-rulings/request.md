# The GM's request, verbatim and unedited

This file is the authority for `spec.md`. Nothing here is paraphrased.

The GM asked what the three queued decisions were; the session explained them with the evidence, and
made a recommendation on each. The GM's reply, in full:

---

I agree with your recommendations, so please implement them for those things.

---

## What the recommendations WERE, quoted from the message the GM was agreeing to

Reproduced here because the ruling is "yes to those", and a later reader needs to know what "those"
were without reconstructing the conversation:

1. **`discard`** - *"leave the guard's rule alone; narrow only the merge case"*: during an active
   merge, `--ours` / `--theirs` is the normal conflict-resolution verb rather than a discard of the
   session's own work, and the guard has no notion of merge state.
2. **`no-poll`** - option C: *"Permit it only when backgrounded and the loop's condition reads a
   file, which is the detached-run shape and nothing else."* Option A (permit whenever backgrounded)
   was declined in the same message as usable for a general bypass.
3. **`review-gate`** - option A: *"let the review gate pass a delta that is exactly one new
   `specs/NNN-slug/` directory and nothing else - no implementation can hide in that, so the
   reviewed-before-implementation property is untouched."*

The evidence behind all three is `specs/164-guards-that-correct/research.md` R3, R4 and R5, and the
five `discard` firings read out in the session that produced this ruling.
