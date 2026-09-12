# The GM's request, as written

2026-09-12, after a 201-minute session on features 233 and 234, asking where the time went:

> So are those old changes the reason why this took over half an hour then? I'm so basically just trying
> to figure out why things take a long time when they do. And if you ended up doing a bunch of audits and
> then going back and catching things that no one had found before, then that's a very good use of your
> time and mine, and I'm very happy with that. I just want to make sure that I understand where the time
> goes when you spend thirty three minutes or more on something that I thought would be a much simpler
> feature. So can you do another breakdown of that time that you spent so that I can take a look and see
> whether there's anything that we should make in terms of a process change or a tooling change or
> efficiency improvements, etcetera?

Then, on being shown the breakdown - and on the session calling its own rework "the honest embarrassment"
that needed no tooling:

> Now you say for the rework, which you call an embarrassment, that this is not a tooling matter, but I do
> somewhat question that because it is natural for people, which is to say humans and LLMs, to simply
> promise to do better rather than looking at process improvements. But that is not good engineering
> practice. Mistakes are inevitable, and good systems catch mistakes early and cheaply. And if a system is
> set up such that mistakes are very expensive, particularly mistakes which it is easy to make and which
> are made frequently, then the system design is poor. So for example, I don't know whether there is some
> kind of shell quoting lint check that we could do that is very cheap, that would have caught your two
> shell quoting failures in a cheaper and less expensive way or not. If those failures were errors in an
> actual script that you were running, then depending on the shape of the error than it may or may not be
> detectable. So for example, if what you did was along the lines of putting backticks in A place that they
> do not belong or in a way that causes the parsing to fail that is detectable through static analysis,
> then we can probably make those kinds of failures less costly when they happen. Similarly, if there is
> some kind of issue with commands that you are running involving backticks, which is knowable through
> aesthetic analysis to be something that we don't want to do, then we could have a hook detect that and
> then reject it early in a way that is potentially much less expensive. Again, I don't know because I have
> not looked at these errors whether any of this makes sense, But anytime someone says, "oops, that's
> embarrassing. I'll just do better in the future", Then a good engineer says, hold on. This might be a
> system designs problem masquerading as a personal failing.

On the British spellings and on the re-review:

> For example, if No British spellings is a thing, then we can have that as a checklist item in advance as
> well as having an automated check for it in, for example, our quick tests, which could do a simple prep
> for common British words.
>
> Similarly, if you are rereviewing whole specs to verify fixes, then I agree that that is something that
> should not happen. And I guess the shape of our process should change to accommodate it because it would
> not be enough to simply mention in our spec hit constitution that you should not do that. We would need
> the checklists in the tasks to be very explicit about the fact that that is how this works. So I presume
> that in the future, when you are looking at the next task and then it says to rereview something or to
> submit something for another round, then you will Narrow it in scope in the appropriate manner. by only
> rereviewing the new stuff and so forth.

And the scope ruling:

> Please do all 6 as part of the same spec-kit feature, thanks.

The research record is explicitly NOT a target: *"I agree that the research record was valuable, and I
don't see anything there that I want to change either."*
