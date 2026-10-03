# Request (GM, 2026-10-03, verbatim)

After feature 317 landed, on seed 47 at 40 households seating three margins:

I do want to immediately talk more about this notion of throwing out and then relaying out houses when we run out of space. That can be a separate feature, which we will talk about after you have landed these changes on main.

Then:

So I guess this sounds like it is a problem for what you have called nucleated settlements and not for other types of settlements because presumably other types of settlements are not as packed together, and so it is simply okay for them to be spread out. Is that correct? So here's my question. is the amount of area specifically that is defined for a nucleated settlement the result of our research findings? So for example, is there a specific housing density that we are targeting that has come directly from a historical source? And that is why we are so rigorously restricting ourselves to it? Or did we just kind of arbitrarily pick a density that we are targeting for our nucleated settlements? And then we are enforcing that without regard to whether the houses could be a little bit more spread out while still being the kind of nucleated settlement that we are recreating from the historical record? Because I do think that restarting makes sense if there is a specific achievable goal that fits the historical record that we are trying to But if we are just trying to create a general type of settlement where it is nucleated so the houses are as close together as they can reasonably be while still having organically sprung up, then I don't think that limiting the area in the specific way that we are doing it makes sense. Because once we run out of space, we would just expand in the same way that actual farming communities expanded. I mean, if we think about this, the way that we are placing our homesteads is to some degree the way that actual historical farmers did. And certainly when someone else moved in, everyone did not move their houses or homesteads to accommodate them. They would get set up along the edge of where the other houses were. So I think that it is generally okay for overflow to be outside of the initial nucleation because that matches how farming communities expanded historically, to my understanding. but I don't want to assume, and I do want to check whether this strict limitation on area was picked for any particular reason, or if it was just an implementation that we have continued to follow blindly. Don't make any changes yet, just see what's going on. And then we can decide how to move forward.

The session found the seat radius (1.15 x the band's half-diagonal, 162 ft square per household) labeled GUESS / UNRESEARCHED,
page 0032 stating "How tightly a clustered village packs is a calibration against the drawn villages, not a historical figure",
and page 0004's drawing page stating the placer "searches wider ground rather than starting over". The GM:

Okay, I think that we should eliminate the throwaway and then redraw logic for farmhouses specifically. Now, out of curiosity, are there any other places where we use this logic? I could imagine places where it might theoretically make sense, but to be honest, I'm a bit suspicious of that just as a concept. Because I think that, at the very least, it is a code smell, and it might even be an anti-pattern, because a better placement algorithm ideally would solve this. I mean, I'm aware that there are many algorithms that really do involve doing this. Uh, there is no polynomial solution to the bin packing problem that I am aware of, so you really do just have to keep trying things and then undoing things, and then trying them again. But, given that we are not constrained with a hard constraint in the way that we would be if we were doing a literal bin packing problem, then I think that it probably makes sense to get rid of this pattern completely. Now, I agree with the 700-foot field reach as a real limit because that is research based. I'm not sure what you are referring to with the quarter built floor, but if it is based on our research, then I agree that we should keep holding it. And in general, yes, I think that we should in addition to getting rid of the relaying out, we can start with a nucleation and then just keep placing houses outside of the boundary when that happens within the seven hundred foot field reach. How does that sound? Don't actually do it yet, just let me know what you think of this and then I will tell you whether or not to proceed with a new feature. Thanks.

The session proposed the scope: remove the margin ladder, the rescue, feature 317's withheld re-seat and early stop, the 12:1
shape refusal and the passage recheck (relay); grow overflow outward within the 700 ft field reach; demote the quarter-built
floor (page 0032, a calibration, not research) to a report; leave the field acreage solvers and the lane settle rounds (the
latter a separate redesign). The GM:

Ah, I see. I had misunderstood about the 700 feet thing. Um, yeah, in that case, I agree that it is not a hard constraint, and um, it can remain as like a preference or something similar to drawing within the nucleated area. where we do it if possible, and then otherwise it doesn't block anything. So yeah, that should definitely be included too. Um, and then yes, please claim this as a feature and then do everything that you have suggested. Thanks.

Asked which limit was meant, the GM chose: "700 ft hard, floor soft" - the 700 ft field reach stays the one hard limit; the
quarter-built floor becomes a reported measurement that blocks nothing.

## Amendment (GM, 2026-10-03, verbatim)

The session found that seed 18 (cohort spec, 15 households) cannot seat everyone within 700 ft of its field on its first
margins, offered three options, and the GM chose "overflow to the next site", adding:

Let's overflow to the next site. The seven hundred feet is based on real research, but my understanding of that research is not that in literally every single farming community in all of Japan, that this was always the case 100% of the time, merely that this was the norm, this is what was expected, therefore this is what we try to do. Does that sound right? If so, then please go with that. If my understanding of the research differs from yours, then we should talk more. But otherwise, you can proceed with option A.

The session then read the record and corrected itself: the 700 ft is not research. Page 0029's drawing page: "No farmhouse
is held to a maximum distance from its fields"; page 0032's: the 700 ft is the back-row distance its own drawn villages showed,
"which reads as the back of a compact village rather than as a stranded arc". It recommended keeping growing at the edge. The GM:

Gotcha. Uh, yeah, let's just keep going at the edge then. I mean, I guess if we have multiple options in our placement, and one option is closer to the fields, then we should take the one that is closer to the fields, because people generally did not want to have to walk a long way. to get to the fields, but that is not any kind of a limit. And it sounds like we can get rid of these 700 feet measurement completely, because really what we're just talking about is how we grow the settlement. I don't know. Does that make sense? If so, then go with that. Like, do you think there's even a reason to keep the 700 feet as a measurement? If that's some kind of useful thing in our implementation, then I'm not opposed to it in principle. I just am not sure what it's even doing for us at this point, you know?

## Amendment 2 (GM, 2026-10-03, verbatim)

The session explained the band-3 slowdown (+11.9%) as the nearest-the-field order, implemented as the growth's primary
key with sixteen directions at three rings offered at once, the near-field seats refused only after the access-corridor
search. The GM:

Okay, so a couple of things:
-> My "ruling" on preferring to stay close was not a hard requirement; merely an "all else being equal, try this first".  I don't see why that would add time.
-> You keep talking about the need to calculate the access-path search, but I feel like there's probably a better way.  Like what if we just added a slightly higher minimum distance from your neighbors?  Wouldn't that guarantee space for an access path?

Don't make any changes, just tell me what you think about this.

The session agreed the order should be a tie-break; on the gap, that homesteads kept a path's width apart cannot enclose a
pocket on their own, but the paddy, water and the map's edge can, and proposed a reachability raster as the cheap check.
The GM:

But if there is a minimum distance between homesteads then doesn't that guarantee that it will **always** be possible to put a lane connecting the path to the lane network?

The session answered: yes among homesteads alone; the exceptions are pockets against the paddy, water or the map's edge;
the gap plus a cheap raster check would let the seating drop the path search. The GM:

I would like this folded into 318, both the field preference being made a true tie-breaker and the lane spacing.  This is not going to spread things out by enough to make the map appear too dispersed and I'm not concerned about the other lane-blocking map features because we already know it's okay for people to cut through neighbors' yards in a pinch.  So with this in mind, I think we can do the gap rule plus some kind of cheap check; the lane layout is expensive and could be made relatively cheap if we guaranteed space for lanes during homestead placement.  This does let us drop the search entirely, as you say, which will also be helpful.
