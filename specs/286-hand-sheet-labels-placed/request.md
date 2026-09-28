# Feature 286 - a hand-drawn sheet's labels placed by the one placer - the GM's request

The GM, 2026-09-28:

> for our generated maps, we have added an implementation of a standard for labeling. I forget what the name of it is, or what the sourcing was, but it was basically just kind of the best practices that exist for how labels are applied to maps. I think it would be good if we were to automate the labeling of things on our maps that are hand drawn. Because I think that there are really good reasons to want to still hand draw these maps for variation. But applying labels feels like something that is able to be done more efficiently and accurately and reliably and consistently if that part is automated. So for example, I can see a label on one of the maps that really just does not look well placed, but if it's placed by hand, then at best I have to come up with some kind of automated check for it. Whereas if we just say, hey, we'll simply use the normal labeling conventions, then that should be good. I think it would be ideal if we were able to even reuse the same literal code that we are using for the generated maps. And to be honest, I'm not sure that that would be a problem since we have a fairly similar pipeline, but I haven't looked at the code, so I don't know whether that would work exactly. But either way, what do you think about this as a general idea?

The session's answer: feature 266 already built one placer (`l7r/diagram/labels/`, the QGIS / Krygier-Wood cartographic
standard) that both the generated maps and the hand sheets use - the hand sheets through `make seat-label`. Three gaps
keep it from "the machine decides": a hand-seat exception (where the placer finds no free seat, a caption's hand
position is kept if it covers less ink, so the result depends on where the caption started); placement is a tool run by
hand, not a step of the pipeline; and the sheet reader infers what a caption names from the SVG's groups. The session
proposed: remove the hand-seat exception and improve the placer's fallback instead; seat the captions in the render
pipeline, a sheet declaring only a caption's text and what it names; and leave the check in place for whatever the
pipeline has not reached.

The GM's answer, 2026-09-28:

> Yes, I agree with your recommendations, except that I don't think that we need the automated check anymore at all. Like, leaving it in place seems pointless if the labels are placed by an automated process. There is no point in having an automated check run against an automated process. Our automated processes can have unit tests to ensure that they are correct, but there is never any reason to write code to see whether the automated algorithm is correct, because that is what unit tests are for.
>
> I would rather not tell you which label looked badly placed because I would like to see whether it is well placed afterwards. Like after we make this change, and then that will be a good way for us to determine whether what we have done fixes this class of issue.
