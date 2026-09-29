# Feature 287 - the GM's request, verbatim (2026-09-29)

Context: feature 284's report named five rules the gate checks on the finished pool maps that no placer guarantees (a bund
built as a flight of steps, three woodland parcels in a ruled row, a copse clump off its house's bank, a brook leg on a
screen axis, the settlement's seat off the regional northwest wind), and proposed making each a guarantee of the placer
that decides it. The GM asked what that meant; the answer was that these rules hold on the shipped seeds because those
rolls happened to satisfy them, and that a guarantee moves each rule into the code that places the feature, so a
violation cannot be produced.

The GM:

> So I thought that we had already moved away from what you are describing, in which we have automated checks for what the
> map is doing. Like, I believe that we eliminated automated checks from the map generation process, but it sounds like if
> I understand what you are telling me, then what you are basically saying is that there are five things right now for
> which our placement algorithm does not guarantee them, and the unit tests will catch them if they fail. Is that right? If
> so, then I completely agree that we should update the placement algorithm in order to make it so that it is impossible
> for those things to happen. So please create a new feature. that includes all five of these items, and then, yes, make it
> so that each and every one of them is guaranteed by the placement algorithm rather than just happening to work on
> particular seeds. also if there are literally any other things of this nature where our placement algorithm is not
> guaranteeing correct behavior, then we should include those along with this feature as well. Thanks.

## The GM, on starting the work (2026-09-29)

> Sounds great, please work on feature 287 and take it start to finish until all placement rules are guaranteed by the
> placer.  Make sure to retire any unit tests which are no longer necessary after this refactor, especially ones which
> impact performance without any longer being needed to guarantee correctness.
