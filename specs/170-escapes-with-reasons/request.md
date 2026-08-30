# Feature 170 - the GM's request, verbatim

The GM, 2026-08-30, on reading feature 169's close-out (which reported that `make-only`'s
`GUARD_EDIT_OK` escape permits without recording, deferred with a sketch):

> I don't see why we should ever Permit escapes without recording. I mean, permitting escapes makes
> sense, but should we just always record that they happened and force the Claude Code session, which
> is performing the workaround to specify why they are doing it? Otherwise, we have no way to audit
> later when this workaround was taken and whether the stated reasons were valid use cases. which in
> turn affects our ability to determine later on whether or not the workarounds are being abused or
> being used as intended and whether the tooling needs more changes. Am I wrong about any of this?
>
> In general, I do want our rules to be enforced rather than unenforced.

And, in the same message, on a defect another session reported about itself:

> One final thing: another Claude Code session reported this:
> ```
>   3. I made two process errors worth naming: I let a bare cd /diagram leak into the next command and
>      stranded a commit in the mirror (blocking a peer until I recovered it), and I reported the gate
>      as "waiting" when it had actually failed four hours earlier because I never saw the
>      notification.
> ```
> Is this something that our new tooling would have prevented? If not, then we should incorporate this
> into the feature before we close it out or into whatever our next feature is. Either way, I just
> want to make sure that it's captured so that we can work on it in this very session at the
> appropriate time. since this is the tooling session where we are making these kinds of
> improvements, then I want to make sure that we do not miss this and that we address this as we are
> able.

The session's answer to that question, which is what this feature acts on: the FIRST error is now
prevented (feature 169's `main-tree-hooks.sh` refuses a `cd` into the mirror root followed by a write
or a commit, and `sync-with-main.sh` now detects the stranded commit instead of reporting success).
The SECOND is not prevented by anything, and nothing in the repository would have caught it.
