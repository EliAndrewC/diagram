# Where this feature comes from

Feature 242's spec amendment on 2026-09-14 took two `spec-fidelity` rounds that together were just
over half of an eleven-minute change, and the batching guard blocked a read with no notice before it.
The GM asked for the breakdown, then ruled on both.

## The GM's words that created it (2026-09-14)

On whether a round after the first owes a full re-read:

> However, I do believe that as per your question about a verbatim application and whether it should
> still owe a full fresh round, my thinking is no. I think that it is okay for subsequent rounds to
> essentially review the paragraphs that have changed or the items that have changed or what have
> you. I think that would be much quicker, don't you?

And, told that the rule already existed in the agent's contract and was not followed because of how
the session dispatched it, and that the batching notice had a gap:

> Yes, I want this all to be automatic since instructions are not reliably followed, but things which
> happen automatically enforced by make files or by tooling such as hooks are more likely to actually
> be implemented. Thus, I do want you to make the change you mentioned before when you said "The fix
> is free. The notice is additionalContext on an allowed call..." as well as making both of these
> changes. Go ahead and do that now in advance of starting on 242 - thanks.

The three changes the GM is approving, as the session had described them to them:

1. *"The fix is free. The notice is additionalContext on an allowed call, which costs no round trip,
   so it can drop the shape test and fire on any single call once the window is one below the bar.
   The block keeps its shape test, since a folded command is never the right thing to refuse."*
2. *"A hook line on a spec-fidelity dispatch. When the feature's spec already carries a Review
   history, the pretool hook adds context saying this is MODE 3 and the prompt must carry the previous
   round's items and the diff of their application, nothing more."*
3. *"Step 3 of MODE 3 narrowed. 'Scan the rest for contradictions' invites a full read. Stating it as
   'grep for the ids and terms the changed passages name, and read only the hits' gives the reviewer a
   bounded procedure."*

Then, mid-turn:

> Goal set: After you have finished the speckit feature for these tooling improvements, please
> implement as much of speckit feature 242 as you are able.
