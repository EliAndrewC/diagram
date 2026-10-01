# Request (GM, 2026-09-30, verbatim)

The GM's first question, on the reference hamlet:

How long does it take to generate a hamlet map?  Can you profile it for me and let me know which parts of the scripted generation process are slowest?  Let's limit ourselves to our reference hamlet for now.

The session's answer: Inashiro (seed 4) regenerates in ~7.5 s (7.0-8.5 s over four runs): the stages ~5.0 s (field 1.25-1.4,
homesteads 1.07-1.13, hinterland 1.0-1.6, web 0.82-0.87), the finish ~1.9 s (the page's picture 1.2 s on its critical
path, the PNG hidden in a thread), the child and cache ~0.35 s.

The GM's reply, verbatim:

Yeah, while I understand this is much faster than it used to be, most of those times are still much higher than I'd expect.  For example, >1s is a lot to place 15 farmhouses.  Like, a crazy amount of time for that.  I mean, that's nearly a tenth of a second per farmhouse, which on a modern processor implies we're doing a ton of computations, and it's hard ot believe that's actually necessary.

And even 1.9s to generate the interactive HTML map seems like a lot.  (Side question: could that be done in parallel with generating the svg / png map?)

12,000 drain-bank clearance checks seems like a lot of checks, and it's hard to imagine we actually need that many.  Same with roughly 100,000 spatial-index lookups for the hinterlands, which makes me think we're doing a bunch of math before putting down each individual blade of grass or marsh glyph instead of drawing a box and then filling it in with a much simpler algorithm, etc.

The session's answer, the levers it proposed (verbatim from its reply):

1. **House seats** drawn only from a precomputed "reachable and buildable" region, with the lane test done once per seat rather than once per orientation.
2. **Marsh, village grove and open-ground fill** done as region-then-fill.
3. **The lane rules** kept true as the lanes are laid, rather than checked afterward.

Maps would shift within the rules, which you've allowed for speed. I'd expect the stages to drop well under half, but that's a guess until it's measured.

The session also answered the side question: the PNG already renders in a background thread while the page is built; the
page needs the finished drawing (which exists ~20 ms after the stages); about 0.3 s of the page's Python work (the
explanations and hit regions) could still run alongside its picture.

The GM's request, verbatim:

Yes, please build and implement all of that as a spec-kit feature, working it from start to finish.

The GM, during the spec's first review round (2026-09-30), verbatim:

To be clear, it is perfectly acceptable for maps to change as a result of these optimizations.  They do NOT need to remain identical in output.

And then, verbatim:

Thanks; in general if anything in our project guidelines says that maps can't change when making optimzations then ew should strike it and say the opposite.
