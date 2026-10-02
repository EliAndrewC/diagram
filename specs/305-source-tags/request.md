# Feature 305 - the GM's request, verbatim

## Message 1 (2026-10-02)

We have recently landed an excellent set of changes to our diagram research. However, at a glance, it looks like there are some improvements that we can make to the citations.  Here the first cited source for the "Groves of trees around farmhouses (yashikirin)" page:

```
visit-toyama-sankyoson

Visit Toyama, the Tonami dispersed settlement (https://visit-toyama-japan.com/en/travel-inspiration/sankyoson)

What it is: The English page on the Tonami Plain dispersed settlement (散居村, sankyoson) from Visit Toyama, the tourism site for Toyama Prefecture. It describes an alluvial fan on which more than 7,000 farmhouses, each ringed by its own kainyo homestead grove, are scattered across roughly 220 square kilometers, a landscape it dates to more than five hundred years of formation.

Why it applies, and its limits: It describes the dispersed-farmstead country of the Tonami plain - thousands of farmhouses each standing in its own fields inside its own grove, and what the grove did for the house - which is the pattern one of our settlement forms is drawn from. Its limits are that it is a tourism organization's promotional page that cites no survey or study; that it describes a living landscape in the present tense and gives modern round counts, used here as an anchor for a premodern pattern; that it is one plain in one prefecture; and that the density our text gives, about thirty farmsteads to the square kilometer, is our own division of its two round figures and not a number the page states.
```

So the overal structure here is great, but I think there are a few related improvements we could make.

First, there are some tags we could apply to our sources which allow us to group them and also display information about them with labels and tooltips.  For example, this is a `modern` source, which means it is about contemporary farms and farmland in the modern era.  While this is still useful information, we give it less weight than maps and surveys and historical findings about premodern farming communities.  For that matter, we sometimes have data gathered from preindustrial communities which nonetheless are still in the modern era, e.g. we have sources about rural farming villages from the year 1900 in areas of China or Japan which had not yet industrialized to any real degree, yet they still had access to things like significantly cheaper metal tools than would have been available in previous eras and things like this affect how applicable the data in these sources is to our premodern fictional setting.  We also have sources about Korea or about European farming communities which are helpful in some respects but which are less applicable.  And of course, because Rokugan is a mishmash of China and Japan, it makes sense to distinguish sources about Imperial China from sources about Imperial Japan.  Stuff like that.

So basically, right now I think we display the sources in the order in which they are cited, but I think the sources themselves could be put into sections based on their tags, like `Present day` or `Premodern Japan` or `Premodern China` or `Modern preindustrial`, etc.  I'm not sure what an ideal set of labels / tags would be, but perhaps you can take a look and think through it.

In addition to grouping these sources together in this way, which is nice, if we apply these kinds of labels with tooltips to these sources then that helps too, because it means that someone who is just checking a source can understand the limitations.  And that's probably a better way than trying to write these kinds of explanations into every source writeup.  For example, we could update the "Why it applies, and its limits:" paragraph to say something like "Of course, because this is a contemporary source, the numbers do not necessarily reflect..." etc, but we'd just end up repeating basically the same explanation for every similar source.  Whereas it would be much better and more efficient to have a tagging system where the makefile target which assembles these pages automatically applies the correct labels with labels and tooltips to convey the standardized explanation of the strengths and limitations inherent to the category of source, in addition to the specific explanation.

What do you think about this?  Do you think you could design something sensible here based on the high-level guidance and goals I've conveyed here?

## The session's proposal (summary, for context - not the GM's words)

Three facets per registry entry: the period of the evidence (premodern, modern preindustrial, present day, not
period-bound), the region (Japan, China, Korea, other East Asia, Europe, elsewhere) and the kind of publication
(primary, scholarship, reference, institutional, popular), each value with a standard tooltip; works cited grouped into
sections derived from the tags by a rule file, ordered by weight; the tags checked at the build and judged by
`source-applicability`; the 2,126 entries classified; the category boilerplate trimmed from the write-ups. Two questions
were put to the GM: is the kind facet welcome, and what are the period cut-offs.

## Message 2 (2026-10-02)

I think you can use your judgement about what counts for period cut-offs as long as you explain the logic in the tooltips where it is explained.

## Message 3 (2026-10-02)

and yes, kind facet should be included, so yes please proceed with making the spec-kit feature, then implementing the feature start to finish
