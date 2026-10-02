# Request (GM, 2026-10-02, verbatim)

Split out of feature 312 (`specs/312-uncited-source-catalog/request.md`, "Never-read sources and the download list"),
where the GM's full words on the download list are kept; they are repeated here so this feature stands alone. Not
started: filed so it can land before 312, letting the GM begin downloading the high-risk sources
(`specs/312-uncited-source-catalog/high-risk-sources.md`) before 312 is done.

The GM, on where the list lives:

And then to be honest, our list of stuff to be downloaded should also probably be copied and checked in. Somewhere. Now, the copy that I am using should be an actual copy and not the canonical source, but this file is now large enough and it is important enough that it deserves to be in source control somewhere, and I would think that our private repository of diagram research seems like an appropriate place for it. Though, I don't know, maybe it should actually just go into the main diagram repo? What do you think?

The session's answer (summary): the main diagram repository, not the archive - the list holds no copyrighted text,
research sessions write to it like the rest of the record, and the pointer check can hold its "Rests on it" lines; the
high-risk list as its top section; the GM's file in `/host-l7r-repo/academic-sources/` a copy generated from it.

The GM, on the format and the sync:

And yes, your proposal does sound right for how to handle the list of things to download. Though I think I probably do want the format of that file to change slightly, where it would be useful for me to be able to have a space that is already set aside, where I can either check a box (i.e. turning `[ ]` into `[x]`) indicating that the file has now been downloaded, or check another box indicating that it has been found to be paywalled, or check a third box indicating that I was able to download some portion of it. Like, you know, for papers where the abstract is freely available, but the full text of the paper is not. And then maybe a fourth option for me finding something, but that whatever I found, whether it's the full paper or a partial summary, was found elsewhere, like through a Google search or something, that was different than the Google search that you linked, and that this would supplement one of the other checkboxes. So like if I any time I checked this one, then I would have checked one of the other boxes as well. Something like that. And then that is something that I would want to edit. So I don't know. We need some procedure for me to have a file where I am marking my work as I go, because that is helpful for me. But I understand what you're saying about some version of this file being kept in sync where no one edits it. So maybe this is just a case where I make a copy myself, and then I would inform you when it's ready to ingest, and then you would pull down my copy or something, and then you know, you could update the canonical version and then sync that, and then I could sync your version to mine when I am ready to do so or whatever. I don't know, something like that. Um, I don't really care that much about the specifics, except insofar as this system, like coming up with this system should be part of this feature, even if actually going through and then running through this list is something that we do as part of a different feature. But I want implementing this system to be maybe like the first thing that we do as part of this new feature so that I could begin work on this downloading before this feature is complete if I end up having the time to do so. Which I probably won't, but it would be nice to have the option. How does that sound?

The session proposed splitting the system into its own feature so it can land first (a feature with an open task lands
nothing on main). The GM:

Yes, I think I do want you to split the download list system into its own small feature, but what is the access tags thing, and why would we want it done as part of that early feature?

The session's answer: the access tags (a per-source field - open, bot-refused, down, gone, the GM's full copy, the GM's
partial copy, paywalled, never read - with the date last checked) stay in feature 312. This feature records each list
entry's status in the canonical list itself, from the GM's ticks, which is durable; 312 derives the tags for every
source from it.

## What this feature is (settled with the GM, to be specified)

- The canonical download list in the main diagram repository, imported first from the GM's current
  `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` as it stands (the GM's own edits included), with
  `specs/312-uncited-source-catalog/high-risk-sources.md` as its top, highest-priority section.
- Per entry, boxes for the GM: downloaded / partial (abstract or excerpt) / paywalled / not found, and found elsewhere
  (ticked with one of the others, with where). "Not found" is the session's addition, from the GM's earlier "report that
  I have not been able to find some of them".
- The GM works in a COPY. On the GM's word "ingest", the tooling reads the copy's ticks (entries matched by a stable id),
  records each entry's status in the canonical list, and archives the files the GM dropped in `academic-sources/`
  (feature 309's inbox). The GM's copy is replaced from the canonical list only on the GM's word "sync".
- Sessions add to the canonical list, never to the GM's copy; the existing rule "a source only the GM can fetch goes at
  the END of TO-DOWNLOAD.md" moves to the canonical list, enforced by tooling.
- The ACCESS TAGS (moved here from 312 by the GM, below): a per-source field with the date last checked - read by us
  (open); open in a browser but refused to us (bot-refused); timed out or a server error (down); 404 with no copy (gone);
  the GM's full copy; the GM's partial copy (an abstract or excerpt); paywalled (a paid or institutional login); never
  read (referenced only) - set on every source from what the archive (feature 309) and the registry entries already
  record, and updated by each ingest. The GM's words on the states are in 312's request ("saying that something is
  paywalled is probably its own tag ..."). The re-check of paywalled sources for open access stays future work, not
  before 2028.
- Out of scope (feature 312): the usefulness filter and write-ups of uncited sources, the high-risk verification, and
  removing paywalled citations - each of which uses these tags.

The GM:

Gotcha. Okay, yes. Uh, do include the access tags thing as part of uh, feature 313.
