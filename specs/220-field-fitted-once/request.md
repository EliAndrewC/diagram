# Feature 220 - the GM's request, verbatim (2026-09-09)

After feature 218 landed (the windbreak 7.3 s -> 0.5 s, the hinterland 8.1 s -> 1.3 s), the GM:

> Thanks.  What do you think we could do about the field placement time?  Any low hanging fruit there?

The session profiled `stage_field` (5.4 s on the reference hamlet's seed 4) and answered - the answer
is what the GM then approved, so it is reproduced here as the request's substance:

> Yes, there is real low-hanging fruit, and the biggest piece is not an overlap check at all.
>
> **The comb is built four times per roll.** The field stage is a search: it bisects a size multiplier
> and builds the whole comb at each guess until the drawn acreage lands within 6% of the household
> target. On seed 4 that is four full builds at about 1.35 s each. The search's own docstring says a
> build "costs well under a second", which was true when it was written. Seam closing was added
> afterwards and is now two thirds of every build, and the search pays for it on the three guesses it
> throws away. [closing the seams 67%; the carve 26%; everything else 7%]
>
> The cheap fix is to search on the bare carve and close the seams once, on the winner. The seam
> passes conserve ground by construction, so the acreage the search sees should barely move. That
> alone is roughly 2.7 s off a 5.4 s stage. The maps would shift slightly, which you have said is
> fine. The docstring's stale timing claim is worth fixing at the same time.
>
> **Two smaller items are the overlap shape again.** The supply-bank clearance test is called 86,000
> times per roll and walks every segment of the supply channel on each call, and the "is this plot
> inside a supply stroke" test walks every plot edge at a 3 px step against every stroke. Both are the
> per-candidate scan of geometry that does not change. The grid pattern from feature 218 applies
> directly and would take perhaps another half second, exactly, with no map change.
>
> **The deeper cost is shapely churn.** One build constructs about 35,000 shapely polygons, calls
> buffer 38,000 times and asks for bounds 268,000 times, mostly inside the trade and absorb passes,
> which rebuild each plot's polygon from its coordinate list every time they look at it. Caching one
> geometry per plot and finding neighbors through a spatial tree instead of a scan would cut that
> substantially, but it is a refactor of the seam passes rather than a drop-in index. I would do it
> third, after measuring what the first two leave.
>
> **Expected outcome.** The first change takes the field from about 5.4 s to under 3 s and the whole
> roll from 10.2 s to around 7.5 s. Adding the two index conversions gets the field near 2.4 s. Under
> a second would need the shapely refactor as well, and possibly the carve itself.
>
> If you want it, the natural shape is one feature with those three steps in that order, each
> measured on the reference hamlet before the next, with the seam-closing change judged by the gate's
> placement tests and a settlement-review pass rather than a manifest diff.

The GM:

> That sounds great. Please implement that feature. Start to finish. Thanks.

Standing over this feature, from the GM on 2026-09-08 (feature 218's request): *"It is absolutely
not required that the changes that we are making here result in bite identical output or even in the
things being placed in exactly the same manner as long as they still follow our general rules, and
the maps end up looking more or less the same"*, and further speed *"at the cost of having the maps
look a little bit different than that is okay so long as nothing ends up overlapping, which isn't
supposed to overlap, etcetera."*
