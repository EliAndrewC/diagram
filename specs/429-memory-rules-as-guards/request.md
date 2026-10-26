# Request: the GM, 2026-10-26, retiring project memories (verbatim, dictated)

```text
I occasionally see a message that looks like this:

> Feature 387 is on main. Last, saving a project memory so a later session doesn't repeat this one's dead ends.

That is a huge red flag for me. A core part of our project guidelines is that memories are unreliable. Instructions are unreliable. When a project grows large enough that there are dozens or even hundreds of different extremely hyper-specific things that we must remember to do in a particular order, then it empirically does not work to simply tell you to remember them. No human or current generation LLM is capable of following complex instructions that reliably to that degree over time. That is why our tooling must enforce the correct behavior every time.

I think that as a result, I probably want two things to happen here. First, I want an audit of our project memories. To see what we have saved as a reminder that either should be tooling or that has already been made into tooling or that is just quite frankly out of date.

Second, I wonder if we should simply turn off memories for this project entirely. I mean, when I work at my day job, then I want user-level memories because I personally have different preferences for shared projects than my coworkers. However, I am the only one working on this project, so anything that would go into a memory probably either needs to be a tooling fix or it needs to live in the documentation, right? Like, I'm not sure what use case memories have for this specific project. What do you think?
```

The session's audit proposed, among other steps, "File the four guards as one tooling feature", naming them:

1. No engine edits while a review is running (`freeze_engine`): the memory itself says this guard was "proposed, not
   built", and `review-gate.sh` only reports NOT-REVIEWABLE after the fact.
2. Questions to the GM need `escalation-check` first (`record_questions_not_gm`): the guard only arms when a review agent
   is dispatched; on 10-25 a report asked the GM two questions with no review behind it, and nothing fired.
3. No edits inside the gm-assistant tree (`gm_assistant_edits_from_clone`): `repo-safety-hooks.sh` blocks git writes to
   `/host-l7r-repo`, but Edit and Write on files there pass.
4. Compare rerolls against HEAD (`compare_rerolls_against_head`): a make target that diffs the manifests against HEAD,
   rather than a habit.

The GM's answer, 2026-10-26:

```text
Sounds great. I approve all of that. So please do it end to end. Thanks.
```
