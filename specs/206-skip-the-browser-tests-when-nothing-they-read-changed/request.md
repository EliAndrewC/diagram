# The GM's request, verbatim

2026-09-07, session "Diagram tooling", after the rolled-page browser tests and the timing caps were retired
earlier the same afternoon and 17 synthetic-page browser tests remained:

> Now those five synthetic tests which pass in five seconds: Do we have logic in place to skip them if the
> content which they are testing has not changed? I think that five seconds is long enough to care about
> adding that kind of check. especially when these tests are something that would be run on a make done.

The session answered that no such logic exists, that the pieces are half built (the `page` stamp of feature
188), that the wall-clock saving inside the gate is near zero because the package is one module on one of
eight worksteal workers, and that the coverage floor would survive a skip because the package reaches no
engine line the Python tests miss. The GM:

> So if that fix is on main with the retirement, then is there actually anything to still change? I'm a
> little unclear what you are recommending. Is the "not ia make" thing fixed or not?
>
> While I agree that we are not saving time by adding the check for whether we can skip the synthetic tests,
> it sounds as if we will be saving three gigabytes of RAM, and that is significant. I often have five or six
> concurrent Claude code sessions running within this container. If all of them are running make done at the
> same time, then we can easily run out of RAM. If we are using up three gigabytes of it unnecessarily. Now in
> practice, there may be enough time between when those five or six sessions are pushing back to main that
> this does not come up. However, because I am running in a RAM constrained environment, then I think it
> would be best to build in this kind of a check. In other words, this is about saving memory, not saving
> time. Although the time saved will become more significant once we add more tests of this nature, because
> I presume that once we add villages and towns and provincial cities and capital cities and so forth, that
> the number of tests will grow. And so having these kinds of checks... to prevent us from running
> unnecessary tests will only become more useful as this project matures. With this in mind, do you still
> recommend against this? if you do, then I would like to hear the reasons, and we can talk more because I
> might be wrong about some of this. If you do agree, given what I have said, then please move forward with
> implementing that. Thanks.

The session corrected the number before proceeding (the 3 GiB was the retired rolled-page tests; the
synthetic package costs one Chromium at about 430 MB for under 9 s inside a gate - `research.md` R1) and
agreed on the GM's other grounds: the project's established pattern for tests whose inputs are enumerable,
a floor that a skip can only tighten, and a package that will grow with the tiers.
