# Where this feature comes from

The GM opened the session "Diagram buildings" on 2026-09-19 with the message below, in full. It asks
for two things at once: a second Mode A building type (the country shrine, the first type added since
the magistracy), and a decision about how the automated checks are structured now that there is more
than one type. It also states that the country shrine is a RESEARCH question first.

## The GM's words (2026-09-19)

> I am interested in adding other types of buildings to what we are able to generate. I suspect that
> most of these building diagrams, or I guess some of them will be compounds rather than individual
> buildings. Like I think of the magistracy diagrams as building diagrams, even though it is an estate
> with walls with a number of buildings inside of those walls. But regardless, I would like to add
> other types of buildings to this. And I expect that most of what we are adding will remain in the
> mode where we generate them by hand, but then have automated checks that we run on them. Some of
> those automated checks will likely just be the same for all types of buildings, like whether
> different shapes end up overlapping with each other, and some of them may be specific to individual
> building types. So since this is the first time that we are adding a second type of diagram, then I
> think it would be good for us to think about the implications of how our code will be structured for
> those automated checks, and then of course how the processes will work.
>
> So let's keep things simple for now and say that the next type of building that we are going to
> generate is a country shrine, which is to say the shrine of a country monk in a village. I have
> always expected that, and I guess this might actually require a research pass because I have never
> confirmed this, but I have always assumed that in such a country shrine, the country monk would live
> in the shrine, such that the shrine is both their home and the place where the villagers come. for
> religious rites and things of that nature. That is probably worth some research.
>
> regardless, it seems like something that we would want to do a research pass on to just see what a
> country shrine like this would involve. This is the kind of family business shrine where a monk is
> allotted a small plot of land where they're able to work tax-free, or if we want to get really
> technical, it is likely the case that the monk is allocated usufruct rights over some slices of the
> common village fields, and that the monk themselves is not taxed. This is what our previous research
> has shown. The monk also receives income in gifts and fees for various religious functions performed
> for the villagers and such.
>
> Regardless, I am going to want to know what is in one of these shrines. Like, you know, how big it
> is, which, come to think of it, I don't know if we actually are accurately representing that on our
> village maps at the moment. Because I don't know that we did a research pass on whether a shrine
> would be the size of a farmhouse or would be a different size. Would it be larger? Would it be
> smaller? And actually, would the monk even live there? I have assumed that they do. And if there is
> any choice in the matter, then I want to make that the case for consistency with past adventures and
> the source material of the tabletop RPG. But I want to at least know what the answer is.

## What the record held when the session started

- The campaign notes (`setting/l7r.md`): every village district has a country monk, an Adept-rank
  monk on a plot of tax-free land, who may have a few acolytes to help farm it; country monks "serve
  in village shrines"; the country monk keeps the district's birth, death, marriage and travel
  records.
- `research/religion-and-death.html`, "What religious and funerary features does each size of
  settlement carry?": a village has a Shinto shrine "tended by the one tax-free religious figure of
  the district, whose dwelling may double as the shrine itself" - the GM's tier rule, no source.
- `research/religion-and-death.html`, "Where does a village put its shrine, and how big is it?": the
  village hall is drawn about 60 by 48 ft, "a touch larger than a plain farmhouse"; "No source gives a
  village shrine a footprint: the whole band is this project's own calibration on the drawn maps." So
  the GM's suspicion is right: the size was never researched, and neither was residence.
- Mode A today: one type (the magistracy), one program catalog entry (`buildings/programs.md`), one
  scripted audit (`tools/pack_audit/`, keyed on the palette vocabulary and requiring a compound
  interior), one size prepass (`scripts/_size_table.py`) and two review agents (`building-review`,
  `size-audit`) that read the program at review time.
