# Request - the claims switch (feature 445)

<!-- SOURCE: GM NOTES -->
## The GM's words, verbatim (dictated), 2026-10-28

On per-claim tasks in 405: "Do we really need to be marking individual claims in 405, given that 405 is the "resolve all open claims in the claims report" feature?"

On closing 405: "With regards to feature 405, do we even want this featuer specifically to remain open? Or does it make sense to close it and then we'll open a new version of that feature after our Rust rewrite?  And then  for now we just allow claims to be ope nwhilwe closing feaures until a new feature closes them all out all at once?"

The ruling: "Yes, that's fine. I accept your recommendation, and I accept the fact that both of my earlier rulings are essentially invalidated at least temporarily, and really what I want is that in the long run I want the first of the rulings which is that once everything is working, then I want claims issues fixed within the task where they are noticed, so that every time a feature lands, there are no open clams. But until we have closed out all of the open claims, then for now, I just want to basically ignore claims so long as they are properly marked and show up in the claims report when we notice them. So maybe the answer is actually just building the check that we want, but then disabling it?"
<!-- END SOURCE -->

## The recommendation he accepted (the session's, 2026-10-28)

Close 405 and open a claims feature after the Rust rewrite: each phase 444 rebuilds clears its own claims at acceptance, and
the new feature works what the claims report still lists. 405's engine fixes (T98, T101, T104, T106, T111) and drawing-page
notes (T165) move to 444 as inputs to their phases. The two rulings set aside for now: the 2026-10-17 option 3 (a finding on
unchanged code filed as a task holding the landing's feature open) and the 2026-10-26 rule sending those carries to 405.
