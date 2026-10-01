# Request (GM, 2026-10-01, verbatim)

Three messages from the session "Diagram organization", with the session's answers between them summarized.

## Message 1

We have recently landed an excellent set of changes to our diagram research. However, at a glance, it looks like there are some improvements that we can make.  Consider that this is what we have so far as our top-level organizational structure on the main research index:

```
The research record
The whole record on one page
Research
Field archetypes: the research behind the overlay, polder and dike-pond rules
Historical grounding: the "why" behind the building-plan realism checks
Fields: the research behind the paddy, plot and crop rules
Homesteads: the research behind the farmhouse, yard, garden and grove rules
Presentation: the map's drawing conventions - labels, captions, framing and cropping
Religion and the dead: the research behind the shrine, torii and funerary rules
The settlement tiers: what each is, and what its map states
The town tier: the research behind the layout, wall and market rules
Urban features: the research behind the state markers, trades and services
Vegetation and terrain: the research behind the windbreak, commons and forest rules
Water: the research behind the flow, channel and wetland rules
Ways: the research behind the roads, lanes, bridges and planks
Cities
Domain capitals: the research behind the castle-town tier
City defenses: the research behind the wall, gate and tower rules
Urban fabric: the research behind the frontage and row-packing rules
The government quarter: the research behind the ministries and martial training
Outside the walls: the research behind the estate and in-wall farmland rules
River cities: the research behind the river, moat-junction and wharf rules
Sizing a city: the space budget and the population rule
How our maps draw it
Field archetypes: how the maps draw them
Buildings: how the maps draw them
Fields: how the maps draw the paddies, plots and crops
Homesteads: how the maps draw them
Religion and the dead: how the maps draw them
The settlement tiers: how the maps draw them
Towns: how the maps draw them
Urban features: how the maps draw them
Vegetation and terrain: how the maps draw the groves, woods and ground cover
Water: how the maps draw the canals, ditches and ponds
Ways: how the maps draw the roads, lanes and bridges
How our maps draw cities
Domain capitals: how the maps draw them
City defenses: how the maps draw them
Urban fabric: how the maps draw it
The government quarter: how the maps draw it
Outside the walls: how the maps draw it
River cities: how the maps draw it
Sizing a city: how the maps draw it
Sources
Sources
```

So just off the top of my head, here are a few issues that I would like to flag with this as the organizational structure.

First, we have a top-level section that is just called "Research" And then the next top-level section beneath that is called "Cities". But everything under cities is research about cities. So this is just confusing. it totally makes sense to have a research section specifically about cities but if that is about cities then the top level section should probably be about farming settlements or something like that would make sense to me if the first research section was something like "Farming settlements" and then another section was on "Towns" or something. Now that may not make perfect sense because things will not divide evenly between them. So for instance, many of our research sections involve things like funerary rites, which apply to both the countryside and in cities. So maybe it's not that. to be honest, I'm not totally sure how to group it. For example, "Religion and the dead: the research behind the shrine, torii and funerary rules" seems like it could get its own "Funerary rites" section, since that section has a LOT of subsections, and those individual subsections could respectively be tagged with things like religion, or countryside, or cities, etc. I'm not sure. but we could use those tags to help decide what goes where. Like maybe our current approach could be to just assume that the very first tag is the primary one and that determines which section something goes in, but it would help in reorganization down the road if we kept these tags up to date and then decided to group things differently instead of only treating the first tag as the primary one, because then suddenly it becomes very easy because it is just a straightforward change to the make file to do a total reordering of everything once we have a functional tagging system. This is just an idea, though. I'm not super sure about it.

This does bring us to the question of the ordering of the sections. So right now, the very first section under the top-level research category is "Field archetypes: the research behind the overlay, polder and dike-pond rules". But that seems like a really arbitrary starting place. And I think that it is worth thinking about the order in which this data is presented.  Now consider this section and its two subsections:
```
The settlement tiers: what each is, and what its map states
The five sizes of settlement: hamlet, village, town, provincial city and capital
Households: how many live in a house, and under how many roofs (ie)
```
that seems like an excellent place to start since we're literally beginning with saying, hey, what are the different types of places that we are mapping and how did we arrive at them? which is exactly the kind of thing we would want to start with. From there, I would expect us to do something like move on to talking about fields and homesteads and such. Now, to be clear, I do not think that we should reorder our research files because right now we have a convention of having a number associated with each kind of little piece of research that we've done. And I do not believe that we should change that system. However, consider that if we have a tagging system, then we could have different types of tags. One type of tag could be about the categories That's something the longs too. So for instance, farming settlements or magistracies or cities or religion, etc. But another type of tag could be about the level of specificity of the research. So for instance, anything with a "foundational" tag would get presented before anything with a "subtype" tag or a "detail" tag or a "counts and measurements" tag. that kind of thing. In that way, we would not need to impose a total ordering. But rather, it should generally be the case that things could be presented in any order within their level of specificity. And then we probably should use something as a tiebreaker that will be consistent, such as falling back on the research item number, just so that running the makefile command twice in a row will never give output HTML files in two different orders.

Now, somewhat separate from the question of research is that I do see a lot of sections on rendering conventions mixed in with the actual research. For example, "Presentation: the map's drawing conventions - labels, captions, framing and cropping" and everything underneath it look like they belong in one of the sections on how things are drawn.

Speaking of that, we have a top level section called "How our maps draw it" and then the very next top level section is called "How our maps draw cities" which makes no sense to me as far as being two different sections. Those should either be combined into the same section or the first one should be called something like "How our maps draw farming settlements" or whatever. If we have enough sub-subsections within each of these that it makes sense to split "How we draw it" into multiple path level sections, then that is fine. But we should not do it so haphazardly.

What do you think about all of this? This is a relatively major change, although it does not actually involve rewriting things. So I do not expect it to be as big a deal as our original large reorg. Obviously, this would still be a spec kit feature, but before we actually begin on that, tell me what you think a good way forward would be for trying to accomplish the kind of top-level organization that I'm talking about. Please keep in mind that I have thrown out some suggestions and ideas here, but those are just to get the discussion moving about implementation and I am not directing you to make those specific implementation choices in order to achieve the general kind of top-level organizing that we are talking about. Does that make sense?

## The session's answer (summarized)

The top level is the directory layout (`site.py` GROUPS), not a design. Proposed: keep storage as the identity and URL,
drive navigation from tags in each fragment (subject, setting, level) against a controlled vocabulary the build enforces;
the rendering twin inherits its research question's tags (the two trees pair by number); one table-of-contents file
declares the sections, their order and which tags each takes, ordering within a section by level then number; the
research and drawing halves share one section structure, Presentation becoming the drawing half's "Map conventions".
A first section order: settlement tiers, the countryside, buildings, towns, cities, trades and services, religion and the
dead. Suggested holding off on merging research and drawing into one tree.

## Message 2

While I agree that separating where research is stored from where it is displayed makes sense, do you think it even makes sense any longer for things to be stored in the organizational directory structure that we currently have? I mean, should we just kind of combine things into a single research place where we've got our research and our sources and our citations or whatever, but I mean, considering that they are all like individual files now, are we actually getting anything out of having a directory called cities? Or is that just literally confusing things? I don't think we should hold off on that question. The separation was deliberate in earlier reorganization to save tokens, but that was prior to us splitting up every section into its own file. So there is literally no longer any applicable reason, and I don't think that we should do that kind of file reorganization as a separate pass. I think that whatever it is that we do in order to tag things or apply ordering or categorization or whatever should just happen at the same time as we decide where things are located and how they are assembled. How does that sound? I don't actually do it yet, I just want to kind of talk through it, but for what it's worth, your first pass on section ordering seems reasonable... except that I don't know that buildings is a good top-level section because homesteads probably talks about farmhouses, and a farmhouse is a type of building. So does that go under buildings, or does that go under the countryside, etc.? The same thing will apply to a samurai country estate, which is also in the countryside, etc.

## The session's answer (summarized)

Flatten storage: one place, one stem per question (`NNNN-<slug>.html`, `.drawing.html`, `.notes.html`,
`.originals.html`), like the sources; numbers are unique only within a folder today (52 collide), so a global identity
number is allocated once and means identity, not order; the drawing page becomes the question's second file and
inherits its tags; part openings move into the table-of-contents file; the ~808 pointer lines in ~233 files are rewritten
by the existing fragment-move machinery. Buildings: a question's home follows the place a reader is looking at from the
map; a subject that genuinely spans settings (religion and the dead) gets its own section; the current buildings part is
really the building-plan (Mode A) research and stays as its own section; every tag gets its own built page, so a
question with one home is still found under every tag it carries.

## Message 3

Nothing is bookmarked, so you don't need to worry about old bookmarks. You should, of course, make sure that places in our code base that refer to individual research files by file path or something, or for that matter by number, uh, use the correct new number, but you don't need to worry about redirecting from old locations to the new one.

As for the buildings section, how about this as a name: "Estates and other compounds"? That seems a little bit more clear. And captures all of the types of buildings that would go into that section.

If that all sounds good to you, then please create a spec kit feature for this.
