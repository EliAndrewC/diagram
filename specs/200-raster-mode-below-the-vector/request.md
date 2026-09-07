# The GM's request, verbatim

2026-09-07, session "Diagram tooling", after feature 199 (the merged scatter paths tiled by cell) had
landed and the pool pages regenerated:

> Okay, that is better but still slow.  How much better do we think we can make it?

The session measured the remaining cost (a Chrome DevTools trace: rasterization of the visible ink on
every hover, scroll and zoom), asked which browser and which action, and offered three levers, the
second of which it recommended:

> **A hybrid: the ground cover as a pre-rendered image at low zoom, the vector tiles above 4x.** At the
> opening view every blade is visible and drawing them costs the 100 to 170 ms above; as an image that
> is a bitmap blit, a few ms. Above 4x a viewport covers only a few cells, and the tiling already makes
> the vector cheap there (16.6 ms per move at 4x). This should make every action on every page 5 to 10x
> cheaper than today with no loss of crispness at any zoom, at the price of about doubling the page size
> (two images per map, normal and highlighted). Feature 134 declined raster layers for blurring at 16x;
> the hybrid avoids that. This is what I would build, and I would prototype and measure it before writing
> the spec, about half an hour.

The GM's answer:

> I'm using google chrome, and all of the above feel slow, so please proceed with the hybrid approach.

"All of the above" are the actions the session had listed as still slow: hovering, scrolling, zooming,
and the first load.
