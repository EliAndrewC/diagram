# Feature 298 - the GM's request, verbatim

## 2026-10-01, first message

Okay, so I do like the idea of doing that, but first, I've really been thinking about the size of our images and what is most contributing to that size? And the more I think about it, the more I think that drawing individual trees serves a useful purpose. But drawing individual blades of grass and lines for marshland and scrubland does not. So here's my question. We already do something where we essentially draw an outline around where the scrubland is and a different outline around where the marsh is. So instead of then drawing individual glyphs within that, can we perhaps have some tiled pattern where a relatively small block of background is then repeated within that, or even like set as the background image for that shape? I think that in the case of scrubland and marshland, that would be just as good. as opposed to things like forests where we actually do get a lot of benefit out of rendering individual trees. And I wonder whether doing this would make other things faster because of the ways in which other things interact with the scrubland and marshland. To be clear, it might not make a difference, but I do just wonder and feel like it's worth trying before we make further optimizations to other things. What do you think?

## 2026-10-01, second message

I don't mind the visual repetition. And I don't mind the issue about edges. Now, as for the pattern staying out of what's inside the zone, isn't that something that can be managed with layering? Like, let's say that something is inside the marsh or is placed inside the scrubland. As long as we are using Z indexing or whatever the equivalent is for SVG to make sure that that thing appears on top, then is that actually a problem? For what it's worth, I don't care as much about the size of the PNG file, And to be honest, I don't actually care about the size of the SVG file per se, except insofar as the size of the SVG file likely reflects a larger inputs size that likely slows us down algorithmically.

Now, before we move forward with this, what about the bamboo? Would we be able to do something similar with bamboo groves given that bamboo is also something where we are using a glyph rendering convention and so unlike the trees where each rendered tree on the map really does represent exactly one tree the bamboo is too small to show up on these maps and so therefore We are using a glyph rendering convention to indicate that There is a bamboo grove within a given area. How many individual glyphs do we have for bamboo on these maps? And would we be able to use a similar approach here?

## 2026-10-01, third message

Well, with regards to things like swept clearings, then worst case scenario, we could lay that down as its own rendered thing over top of the background. Though I think you're right, and something like that probably does not actually come up, but we'll see. And yes, please create a spec kit feature for this and then work the feature from start to finish and let me know when it has landed back on main. Thanks.

## The session's answers the GM was replying to (context, not the GM's words)

- Grass blades (`#A7A860`, `land/cover.py`) and marsh reeds (`#6E9377`, `land/wet.py`) are 55-68% of four pool hamlets' SVGs
  (27% of Kuwabata's); stripping them took Kashikawa's SVG 7.3 -> 2.5 MB, its PNG 8.2 -> 5.3 MB, and the page carries 4.8 MB of them.
- Proposed: one feature for marsh reeds, rough-ground grass and bamboo; each zone a pattern fill drawn at the bottom of the
  draw order so everything inside draws over it; trees stay individual.
- Bamboo: ~570 elements on Kashikawa (~1% of its SVG), ~130 on Mizuguchi, 29 marks on Inashiro, none on Sawada or Kuwabata.
