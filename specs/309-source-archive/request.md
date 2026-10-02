# Request (GM, 2026-10-02, verbatim)

The GM asked:

I have a question about our research section.  We have tons of references to external publicly available sources, but what do you think about the idea of downloading a copy of each external source?  I'm concerned about "bitrot", e.g. in this case websites going offline, failing to be maintained, etc.  With something like wikipedia I'm not terribly concerned about that, but just on general principle I wonder about downloading copies of every webpage we cite and every pdf of every academic paper, etc.  Things like this source:

```
visit-toyama-sankyoson
Present day
Japan
Popular

Visit Toyama, the Tonami dispersed settlement (https://visit-toyama-japan.com/en/travel-inspiration/sankyoson)

What it is: The English page on the Tonami Plain dispersed settlement (散居村, sankyoson) from Visit Toyama, the tourism site for Toyama Prefecture.
```

seems quite at risk of going away or even just changing URLs in a website redesign in a few years.  So I feel like we need backup copies of all of the content we are referencing to hedge against this, and then perhaps we could have backup links to the Github where we check these in, which would probbaly be a different repo than the actual diagram repo - I've just created https://github.com/EliAndrewC/diagram-research and given your Github PAT access to it as a place to store these.  What do you think about this idea?

The session's answer (summarized): agreed - a citation is a verbatim quote from a page the reader can open, so a dead or
edited page breaks the record's verifiability. The feature-288 page cache (~3,000 pages, 148 MB, text extracts, host-local,
gitignored, a 7-day freshness window, rejected pages included) is a seed, not an archive. Proposed: snapshot at cite time (raw
bytes as served + text + URL, time, status, hash) into diagram-research under the source key; quote checks run against the
cite-time snapshot; Wikipedia pinned by `oldid` revision; each cited URL submitted to the Wayback Machine as the public fallback;
a one-time backfill of the 2,126 registry sources. Asked whether diagram-research is public or private (copyright).

The GM:

To be clear, even things which seem at low risk of going away, like wikipedia pages, seem worth storing to me.

The GM:

The repo is private, for exactly the reason you said.  If someone's copyrighted work goes offline then having a private copy allows me to contact the author and ask whether they are okay with me hosting a copy publicly, but for now I just want an archive.

The GM:

And yes, please start on the feature now.

The GM (while the spec was being written):

For webpages which are not PDFs I imagine we should download the whole webpage with images and css and such and not just the html content - do you agree?

The GM (goal set):

Please crate and implement feature 309 from start to finish and land the diagram changes on main - the diagram-research repo does not reqire the same forking/cloning rules so you can just push directly to it without each of our diagram .clones/ having its own copy which needs to be synced.

## Amendment 1 (GM, 2026-10-02, verbatim)

One request that I would make to be added to this feature is that we currently have a directory of academic sources that I have downloaded for you to look at. And this is where we put the files where uh, you are blocked as a bot, but where I as a human just using a regular browser am able to get them. And I think that it would be great now that we are storing this kind of stuff in the diagram research GitHub repository to basically use this directory as a queue of sorts, by which I mean once something has been added to the diagram research repository and then pushed, then we can delete it from the academic sources directory. And in that way, looking at that directory is just a good way to know whether there is something that we have not processed yet.

Now, with this in mind, I guess it also probably makes sense to store sources which we ourselves do not end up citing because we might need to consult them later for a couple of reasons. One reason is that When we check a paper for one fact, it may not have what we need for the question that we are asking, but then we may end up wanting to check the paper later for a different fact. And it will be easier to just look it up where we already have it. I suppose this also means that our research procedure should include a step where we first check to see if we already have something, rather than going out and trying to find it on the internet. I don't know if this is something that we have already done, but honestly, updating our procedures to include this should probably be made part of this very feature that we are working on right now.

The session asked which uncited sources to store - every page a research session reads (cited or not, the ~3,000 earlier
reads archived from their saved text now and re-fetched whole where the page is still up), only the GM's downloaded files,
or every page from now on only. The GM chose: "Every page we read (Recommended)".
