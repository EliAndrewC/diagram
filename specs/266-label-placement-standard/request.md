# The GM's request (verbatim, 2026-09-27)

Context: the GM had just had lane junctions, lane ends and the scrub under the windbreak fixed on Inashiro. They then
turned to the one label every hamlet carries:

> Thanks.  Now the notice board label seems a little far away from the notice board, in a way that looks a little weird.  This seems important to get right since this is currently our only label but we will eventually have many other labels, so if we can get this one consistently looking good then that seems nice.
>
> I wonder if there are some known best practices for labels on maps and diagrams that are applicable here that we should import rather than trying to reinvent the wheel.  Things like "don't overlap other map features unless you have to" or the ratio of how far away you should put the label from the thing it's labeling, and when it's better to overlap soemthing than move too far away, etc.  What do you think.  Is there some kind of visual design standard for labels on maps and diagrams we could just apply here, or does everyone kjind of jusyt go with "what looks right"?

The session measured the Inashiro board's caption (about 12 ft of air between board and text, roughly 1.5x the text
height, and slid about 17 ft back along the board's axis), explained that its seats were laid out on the page's axes
with hand-chosen gaps while the board stands at 47 degrees, and answered from memory, marked as not yet checked
against the sources: Imhof's "Positioning Names on Maps" (1975) for the principles; the ranked positions around a
point (Yoeli 1972; the textbooks; QGIS "cartographic" mode, Esri Maplex, Mapbox anchors) with upper right first; the
cost formulation of Christensen, Marks & Shieber (1995) - labels never over labels, point symbols and the feature
itself very expensive, lines expensive and crossed square if at all, background cheap, distance costing more the
further out - with a leader line or a dropped label past a limit; a small gap, the same for every label of a class;
point labels conventionally horizontal, rotated text being for line features. It proposed a spec-kit feature: read
and record the sources, one placer for every label, and three calls for the GM - tilted or horizontal text for small
point features, whether a leader line is allowed, whether a label that cannot sit close may be dropped. The GM:

> Yes please adopt this standard into our project, after looking up the details enough to be able to implement it faithfully.  I also agree with one placed for all labels.  Tilted or horizontal text is okay for small point features like the board, and in general is fine if the standard says it might be preferred for things which are themselves tilted, etc.  A leader line is allowed but we should follow the standard for deciding whether to do it.  Labels should not be dropped for now; if our maps grow so large that we find we have so mnany that it's unavoidable then we might start dropping them since our interactive maps let us highlight things, but for the time being we'll treat labels as mandatory when the thing is marked as needing a label.
>
> Go ahead and claim a feature for this and then implement it start to finish, making sure our notice boards use this standard but that other future labels will be able to do so as well.  Let me know when it has landed on main.  Thanks.
