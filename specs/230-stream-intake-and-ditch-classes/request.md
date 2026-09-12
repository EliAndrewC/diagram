# Feature 230 - the GM's request, verbatim (2026-09-12)

The GM, looking at the reference hamlet (Inashiro):

> I'm looking at the diagram for our reference hamlet, and I have a question about the difference between a stream and a field ditch and a drainage ditch. First of all, it looks like the irrigated ditches and the drainage ditches are both just labeled as field ditches. How do we feel about that? like, those are more or less the same thing in that they are both irrigated ditches that were artificially created in order to direct the flow of water. On the other hand, the ones at the top of the field are feeding water into the rice patties, and then the ones at the bottom of the field are collecting water from the rice patties, and then taking it away into a drainage pond or feeding it into a stream or otherwise sending it off the edge of the map. So do you think it makes sense for those things to be different? I mean, they are both technically a type of sealed ditch. So maybe there should only be one field ditch item, but I was a bit surprised to see them lumped in together. if for the other reason, then that there's a lot of information. about the channels that feed water into the patios that doesn't apply to the ditches that drain it away and vice versa. Additionally, the map looks kind of strange at the top where the stream just kind of becomes a field ditch, and that seems to happen at kind of an arbitrary point. like, I probably would have expected the stream to still be called a stream right up until the point where it branched into two. But I suppose that there's also an argument to be made that it becomes a ditch at the point where it has become artificially dug. But even still, the fact that it was going in a straight line more or less and then just suddenly started becoming a ditch. with no notable feature or even bend in the stream seemed a bit unusual. Is there any logic currently to determining when a stream becomes a ditch? Should there be?

The session's assessment (the parts the GM's second message refers to), in the session's words: that the
engine already carries a role on every ditch record (`main`, `branch`, `drain`) and paints the drain a
different blue, but one hover class covers all of them; that the two should be two classes; that there is
"one inconsistency worth fixing at the same time: when a hamlet drains off the map instead of into a pond,
the drain's continuation is drawn and classed as a stream, while the same continuation into a pond is a
field ditch"; that the stream-to-ditch point has no logic at all - a fixed 420 px brook ending at the
intake, then a hardcoded 90 px head race straight to the fork, with no weir, gate or bend and no
research entry justifying the 90, "an unlabeled guess"; that in reality the transition is (unresearched)
a diversion weir with a head gate from which the canal leaves, the stream normally continuing below the
weir with the surplus; and the three candidate outcomes - the stream runs on past a drawn weir; the whole
brook is captured but a weir or head-gate glyph marks the point and the head race gets a reason for its
length; or, if both forms are attested, a knob rolled per settlement.

The GM:

> Yes. I do want both of those things pursued. So, yes, go ahead and make the spec kit feature to include both splitting the field ditch, labeling into two classes. fixing the inconsistency you mentioned. and doing the research pass in order to answer the question of exactly when the stream to ditch point should be, and then making that change as well. Please proceed with that. Thanks.
