# The GM's request, verbatim

Captured BEFORE `spec.md` was written (constitution XVI). Nothing here is edited.

## 2026-08-28, after feature 135 landed - the cache question

> Before we talk about the specifics of what further improvements I want, talk me through the difference between the cashed and uncashed versions of these tests that you were describing because it sounds like you were saying that the tests run very, very quickly when there is a warm cache, and then they still take five or six minutes to run when there is a cold cache or something like that. Did I understand that correctly? Talk me through what you meant by all of that.

(The session explained: warm = every roll's key matches and the map is served; cold = an edit to a function the rolls execute re-rolls every hamlet at once - the three polders at ~100 s each, the re-roll ladders, the reference - which is the 5 m 42 s run; the levers are the rolls themselves, or warming the cache from the idle-tests hook after a sync.)

## 2026-08-28, the direction

> Having the idle tests hook the other session just landed. warm the cash after a sink so that the next inactive gate is warm does seem like a really good idea. So I think we should do that. That can be part of our next feature. More broadly, I do think that speeding up the cold cash runs is our next feature. So this fits in nicely with that. Along those lines, though, before we actually open that feature, tell me why the three polders specifically take about one hundred seconds each. I mean, you sort of did just tell me, but one hundred seconds is so long. And you were saying that, like, ten households instead of sixteen might make a difference, but that seems crazy. I mean, even with an n squared or an n cubed algorithm, I wouldn't expect that to matter, nor would I expect one hundred seconds of CPU time for the kinds of maps that I have looked at. So you mentioned that subdividing the fields is part of what's causing it to take so long, but are you doing some kind of NP complete problem? like a literal exponential complexity problem or something. I'm just confused about why it would take one hundred seconds, particularly when most of our map generation is so much quicker. bisecting a field several times per map does not seem like it would add up to one hundred CPU seconds. So help me understand what's going on here. Thanks.

(The session profiled a polder roll: 57 s in `stage_web` and 22 s in `stage_track` - the lane router's clearance test walks every fabric segment per lattice cell with no spatial index (36 million `seg_dist` calls), and `path_violations` compares every pair of water crossings (170 million `hypot`); nothing NP-hard, a brute-force inner loop; the budget file's "field bisection" explanation was wrong.)

## 2026-08-28, opening the feature

> Yes please open that as a feature and then work it to completion, thanks.
