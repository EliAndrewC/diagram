# The GM's request, verbatim

2026-09-07, session "Diagram tooling", after features 208 and 210 had landed and the session had broken
down a full gate's 5.5 GiB peak. The session proposed six changes (quoted back by the GM below). The GM
first asked for the roll count to be nailed down:

> Wait. We're re rolling thirty hamlets? I remember putting in quite a lot of work to get that number
> down to only eight or nine. when did it go from that low number to the full thirty? ... So what
> happened? Did we add another twenty something? Hamlets, when I wasn't paying attention ... it does seem
> in general like we are not making particularly efficient use of caching entity duplication, but Before
> we talk about that in more detail, I would like to nail down the number of hamlets which are being
> rolled. Please do remember all of these options that you are suggesting because I suspect that we will
> implement a number of them. But let's get this Hamlet roll generation thing figured out first.

Then, on the recurrence:

> Whatever we end up doing about this, it sounds as if we need some kind of automated check-in place to
> make sure that this problem doesn't repeat because we definitely had this solved at one point, and then
> the problem just came back on its own. So that is usually a sign that something about our testing
> procedures is bad. Granted, performance problems are less likely to be detected in an automated way.
> than correctness problems. But now that we have identified a specific recurring issue, then I'm sure
> there is some manner by which we could program our unit tasks to never allow the same hamlet to be
> rolled twice within the tests and also to have some required process around adding another hamlet that
> gets rolled. when we have already identified what we believe to be the number that need to be rolled in
> order to gets to one hundred percent code coverage. Again, I am not asking you to make these changes
> right this second. Just Keep this in mind so that when we are writing our new speculative feature,
> which is intended to take care of this, then we can make sure that whatever feature we are implementing
> both addresses the problem as it is currently identified and then prevents it from recurring again.

The census (research R1) then counted 37 real rolls of 14 distinct specs in one gate, and the session
proposed three levers (one roll per seed shared by `build` and `generate`; a lock so the first wave of
workers waits rather than each rolling; first-attempt seeds where a test does not exist to exercise the
re-roll) plus the census made permanent as the gate. The GM:

> Okay, that sounds like a good plan. You had previously proposed these changes:
>
> 1. Tests must not render real maps. The 444 MB child was the pool-cache round-trip test regenerating
> a real map with its picture, and earlier gates showed resvg at 420 MB rendering PNGs for tests. The
> suite has no skip-render default; the gate reads manifests. A suite-wide default, with the handful of
> tests that test rendering itself opting in, removes the largest transient left. Simple, and it stacks
> with 208.
> 2. Finish the child roll-out. The remaining in-process rolls are exactly the highest worker peaks now:
> the cohort test at 271, the immune test at 222, the re-roll tests at 194. With them in children the
> workers sit near 130 and stay there. Three hundred to five hundred MB at peak, and a flat profile
> instead of spikes.
> 3. Measure the pool sweep's children. In the first 210 gate one sat at 550 MB rolling Inashiro under
> coverage run, where the same roll in-process ends at 121. I do not know why, and up to five of them can
> coincide under worksteal, so at other moments they are likely the true peak. That wants a profile of
> one child before anyone touches it.
> 4. The collection baseline is structural but tunable. Eight copies of the same 110 MB is 880 MB, and
> half of it is every worker importing every test module. The honest lever is the worker count against
> the container's CPUs, which is a time-versus-memory measurement to take rather than a guess.
> 5. Caching, the real one. A full gate deliberately bypasses the roll cache so coverage sees every roll,
> which is why it re-rolls about thirty hamlets every time. The other session's incremental gate, feature
> 207, is precisely the fix: coverage contexts merged over the last full run, so a small change re-rolls
> only what it can reach. I would let that land rather than build a second answer.
> 6. Ordering. The long roll tests start late under worksteal (the cohort test began four minutes in),
> which lengthens the tail. Scheduling them first shortens the gate; bounding how many rolls may run at
> once would cap the coincidence peaks at a small time cost. Both are cheap.
>
> All of those changes sound good to me, and I think you should make a spec kit feature, which implements
> all of them as well as the census plugin and its aggregation, which you are proposing now ready to
> become that gate. Any objections? If so, then let's talk more before you get started. And, otherwise,
> you can proceed with implementing that spec kit. feature and then going through it by taking it start
> to finish. Thanks.

The session raised no objection; it noted that item 5 has nothing to build (feature 207 is another
session's, in flight) and that the gate's test target is shared with that feature, so main is merged
before the Makefile is touched.

## Relayed from the "Diagram html" session, 2026-09-07 (the GM's request through that session)

> The GM asks that the spec-kit feature you are working on include a task that confirms the following is
> addressed, whether by your existing work or by a fix you add, and the task should exist and be ticked
> even if no change turns out to be needed.
>
> The problem, measured under feature 207 (specs/207-incremental-gate-and-content-as-data, research
> R7/R8, decision D14). On an incremental gate run, the selected tests re-roll a changed subject under the
> test fixtures' cache subject (the `hamlet()` share path), and then the hamlet floor phase rolls the same
> spec AGAIN under `report:`'s subject, because `hamlet_floor.module_set` asks `rollcache.report_deps` per
> fixed subject and a subject whose cache key moved re-rolls itself, serially, at about 40 to 60 s each. On
> the polder-only run that was about 140 s of a 219 s gate: 79 s of pytest and the rest the floor rolling
> the two polder subjects a second time. It is feature 192's double-roll shape, on the incremental path.
> The fix I sketched and deliberately did not attempt inside 207: one cache subject per spec across the
> two callers, so a roll the tests made serves the floor's dependency record. The GM suspects your
> roll-census work may already cover it. Please read D14 and R7 in that spec directory, decide, and record
> the verdict in a task of your own feature.

Carried by FR-001, SC-004 and T10.
