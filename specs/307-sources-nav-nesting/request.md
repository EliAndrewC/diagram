# Feature 307 - the GM's request, verbatim (2026-10-02)

Oh, I really like the idea of having the fiction be its own tag too. Now with that being said, I love how the sources are broken out on any given page that has them. But I would also like to see the "Sources" top level section in the left hand nav bar and in the table of contents broken into subsections for those categories. So while right now we have

```
Sources
Sources
l7r-median-domain
l7r-castes
l7r-budgets
l7r-wagons
...
```
I would like to instead see "Sources" as a top-level section, and then "Setting canon" as a subsection of that, and "Premodern Japan" as another subsection, etc. and then in cases where we have other tags which are not top level ones such as "Reference" vs "Scholarship" then we could have sub subsections for those and then list things underneath that. I think that would make this much more browsable since as of now we have just so many sources that a single list of them is much harder to look through than a nested structure with multiple levels of nesting in some cases.

How does that sound? If that sounds reasonable to you, then can you go ahead and reserve a spec kit feature and then implement this from start to finish? On the other hand, if there's something that I'm missing, then we can talk about it before you begin. Thanks.

## Message 2 (2026-10-02, while the feature was being specified)

Oh, and actually, since we are talking about organization and kind of how we link to things, then here are two more things that I would like to be made part of the feature. First, when we display a URL, it should become a link. And I think this is something that our makefile target can do automatically without us having to go in and edit this manually or whatever. But as an example,

> History of Iron and Steel Making Technology in Japan, Tetsu-to-Hagané 91(1), JStage (https://doi.org/10.2355/tetsutohagane1955.91.1_2)

displays that URL, but it does not make the URL itself a link that is clickable, that would open the source in a new tab. which is what we want.

Second of all, all of my L7R campaign notes currently say URL none, but in fact the correct place to find them is on GitHub at https://github.com/EliAndrewC/l7r/tree/master/setting e.g. https://github.com/EliAndrewC/l7r/blob/master/setting/l7r.md#the-median-domain is what I would expect to be linked to in this paragraph:

> The GM's campaign notes, l7r.md, "The Median Domain", "Place Names" and "Samurai Population of the Largest Cities" (URL: none - the GM's own unpublished writing, at /host-l7r-repo/setting/l7r.md)

## Message 3 (2026-10-02)

Please implement feature 307 from start to finish and then land it on main.
