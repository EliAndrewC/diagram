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

The GM (mid-amendment):

Since we're adding so many thousands of sources, then do we need to organize the diagram research repo in a different way than we are organizing it now? I mean, I know that a directory in Linux can have literally thousands of subdirectories within it, and Linux handles that fairly gracefully, although at a certain point it begins to make sense to start deeply nesting things. And since we are now going from a few thousand to more thousands of things, then since we plan to look up whether a thing already exists, then should we do something where we make that a bit hierarchical, perhaps? You know, to limit the number of directories in any given directory to no more than a few hundred? I mean, I know that there are some fairly typical ways to do that. Like if you're storing by UUID, then you have the first two digits of the UUID be the name of the directory, and then that way you don't have more than 256 entries in a top-level directory, and then you do the same thing for subdirectories, kind of to however many levels of nesting you need given the amount of data that you're storing and the number of files. Again, I'm not suggesting that as the specific choice here. I'm just asking whether this general type of optimization is something that we may as well do now as part of this feature while we are still figuring this out.

The session's answer: yes, now - GitHub's web view lists only the first 1,000 entries of a directory and the archive's top
level already held ~1,700; shard by the URL id's first two hex digits (256 buckets, ~20 entries each at 5,000 URLs), the
GM's copies flat under `gm-copies/` (~40), the manifest sharded the same way; lookups go through the manifest.

## Amendment 2 (GM, 2026-10-02, verbatim)

Actually, can you hold up on the backfill for now? Because I have something that I want to explain about how it should work and what we should do with it before we actually jump into it.

The GM then described source write-ups, a usefulness filter and a log of what each source was tried for (verbatim in
`specs/312-uncited-source-catalog/request.md`). The session proposed landing this feature first, with the uncited pages
left to that new feature, and the GM agreed:

Okay, yeah, I do like the idea of landing what we've done in main prior to starting this as its own separate feature. So how about you do that and finish the feature that we are already in the middle of with this new feature about filtering and cataloging and tagging and doing source write-ups of our uncited works being its own separate feature, which you can also file now. But then we don't actually start that until the previous feature has landed in main.
