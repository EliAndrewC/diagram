# The GM's request - verbatim and unedited (2026-08-28)

> Thanks.  I have a separate "Diagram tests" session running which is working on test efficiency.
> I would like you to communicate with that session to let it know that you are merging its changes
> into your branch and that you will be taking on actually fixing the expected failures. that we
> have in our tests. Your goal, which is to say the current goal for this session, which should
> become its own spec ticket feature, is to get one hundred percent of those tests passing. While
> the goal of the "Diagram tests" session is to improve the efficiency of those tests. While these
> poles are notionally orthogonal, they are ultimately complementary in the sense that faster tests
> will make quicker iteration, which means that you will have an easier time, which is why I want
> you to, after you pull from the latest main checkout into your clone I want you to further pull
> in the changes made in that session prior to beginning work on test correctness. Your two
> sessions came in work together. With the other session, working on test efficiency and you
> working on test correctness. When you have a set of correctness improvements to hand off to the
> other session, then you should let them know so that they can pull your changes into theirs. and
> when they have additional efficiency improvements. then you can pull those improvements into your
> branch. The reason why you should communicate with one another is to know when it is okay to do
> these pulls. For example, while I have told you to pull in their changes, what I really mean is
> that you should pull in the changes which they communicate to you are safe or at least that they
> expect to be safe. In particular, I don't know whether they are committing in advance of fully
> testing their changes or if they are committing changes that they make prior to testing out those
> changes to see if the changes even work or if they are faster, etcetera. Similarly, I do not want
> that session to pull in fixes which you have made, which are not fully tested. So in this way, you
> can probably communicate with each other to coordinate. when it is good to pull your branches
> into one another.

The expected failures this refers to were pinned during feature 133 under the GM's waivers
(tasks.md T91/T92 there), the GM's words then: *"have any failing tests on the acceptance gate
marked as expected failures and documented as something for a future session to take care of, and
then I will handle those separately"* and *"I will have a specific background session work on
fixing them instead of either blocking on getting them fixed before merging into main or having a
bunch of different sessions, all duplicating work."* This session is that session.
