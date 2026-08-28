# The GM's request, verbatim

Captured BEFORE `spec.md` (constitution XVI). Nothing here is edited.

## 2026-08-28, after feature 141 landed

> That's fine. I'm not worried about a one hundred percent code coverage floor on cities. So long as we do have one hundred percent code coverage on anything involving hamlets. The idea is that we will maintain one hundred percent code coverage on the scripted procedure and anything related to it, and that that will be maintained as we expand it. But that because there are things related to towns and cities and even villages since we are still on hamlets, that We are not currently exercising, then it does not make sense to maintain code coverage for them because they might be deleted entirely. With that being said, are we able to enforce one hundred percent code coverage on the hamlet generation and anything included with that? like, I want that threshold to be automatic rather than something that we just remember to maintain if possible. but I realized it might be difficult if there are some things where it's not obvious whether they relate only to hamlets or not.
>
> Now as for what to do next, the thing I am most interested in is the seventeen seconds of genuine unit tests. especially with the settlement geometry. The roles themselves being sixteen seconds each sounds like the next obvious place to look. does it take so long? That's a really long time. That's like billions of computations. What are we doing billions of computations on exactly? As you said, maps are now allowed to move. So if the only reason why we weren't fixing that was to keep the maps the same, then we should just go ahead and fix it.

(The session answered: the hinterland scatter's 1.3 million point-in-polygon tests per roll and `fit_field`'s seven full carves; the floor is enforceable once "the hamlet path" is defined - the precise definition derives it from the functions the scripted rolls execute, and it means something only when measured against the unit tests alone.)

## 2026-08-28, on the floor's definition

> That sounds good. Thanks. I'm okay with it being done at the module level for now. because eventually, we will just go back to one hundred percent code coverage everywhere. and for now doing it at the module level seems sensible.
