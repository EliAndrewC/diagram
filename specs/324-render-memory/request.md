# The GM's request (2026-10-05), verbatim

> yes please do all 3 as a single feature, thanks

The three the GM was answering - the session's proposal, verbatim:

> | fix | memory | cost |
> |---|---|---|
> | 1. Stitch tiles one at a time (decode, paste, free) | stitching child 300 → ~185 MB | none measurable |
> | 2. Cap simultaneous tile renders at 3 | per-map render peak ~970 → ~540 MB | about +1 s per rendered map (render 2.2 → 3.2 s, ~12% of an 8 s hamlet regen) |
> | 3. Cap the post-landing render step at 4 parallel maps (now 22) | its peak 1.46 → 1.22 GB, typical (p90) 889 → 448 MB | about +15 s, in a background job nobody waits on |

And the GM's question it answered: "Any other low hanging fruit you can see with the map generation? Frankly even 236 MB is a
lot of RAM to use, so I wonder if there are some other straightforward optimizations which might help."
