# Request (GM, 2026-10-02, verbatim)

Filed during feature 309 (the source archive), not started: the GM's instruction is to start it only once 309 has landed
on main. Context: 309 archived every cited source; its Amendment 1 had also archived every page a session reads, cited or
not, and its backfill of the ~2,846 uncited pages on the sources-consulted ledger had captured 3 when the GM held it.

The GM:

Actually, can you hold up on the backfill for now? Because I have something that I want to explain about how it should work and what we should do with it before we actually jump into it.

The GM:

Okay, so I think that it would be worth creating a source write-up for each source that we don't use, which is basically just exactly the same as what we have for our existing sources. So, for instance, we tag them with whether they are pre-modern, or contemporary, whether they are reference, or academic, etc. We also have a summary of what they are. And then we talk about why we think it is applicable and what the limitations are. And we have subagent checks that confirm that all of this is accurate to what the source is. Now for sources that we actually use, I think that we also record what it is that we did in fact use the source to tell us. And for sources that we end up not using, then I don't know that it makes sense to have a section like this. Um, it might make sense for efficiency purposes to have a separate file in which we record all of the things that we have tried to use a source for. and found it wanting, or you know, just kind of not applicable to us, or just not having the information that we were looking for at that time. And that would be helpful because if we ever do another pass on a research topic, then we can have a procedure by which we first check to see if we have tried to answer this specific question already using this source, or not. And that wouldn't be part of the main write-up, but would still be information that we capture about our uncited sources. I mean, now that I'm saying this out loud, I wonder whether this is something we should also do for our cited sources. Because the same thing actually does apply to things that we have cited, because we do often cite the same source multiple times for multiple different questions, because many sources are relevant to multiple different topics or features of a farm or things of that nature. So we probably do want to do the same thing, right? Or am I just overthinking this? I mean, I'm kind of just imagining what I as a human researcher would want to do and extrapolating out from this to develop a sensible research procedure for the future as we consult our existing sources going forward. But is this something that we should even care about? I think that it is, but I would like to hear your thoughts before we move forward or make any more changes. So let's talk about this, and then I can settle on what I want this feature to include before I have you do any more work on it.

The session's answer (summary): not overthinking; the sources-consulted ledger (feature 288) is half of this already -
8,535 reads of 4,903 pages, 1,735 pages read twice or more, 7,155 rows naming a question - but 3,314 rows carry no outcome,
only 73 a rejection reason, the question ids predate feature 303's flat stems, the file is host-local, and no step asks
"have we tried this source for this question". For cited sources the "what we used it for" can be DERIVED from the
footnotes (each names its key and sits under a question); what only a session can supply is the misses, which belong in
the per-source attempts log, cited and uncited alike, consulted first by a tool-enforced step. Pushed back on full
write-ups for every uncited page (many are blogs, search pages, dead ends) and offered: every one now, substantive ones now
and the rest on a second consult, or only on a second consult; and asked whether uncited sources show in the built record.

The GM:

Hmm. So that's interesting. Because I feel like anything that we take the time to actually store a copy of should get a write-up. but you are pointing out that there are things like blog posts or things that we sort of determined were not valuable enough that we would not expect to ever actually need them in the future. And those things feel like things that we should have a record of. So that we know not to check them next time. But which we don't bother to store the full copy of. Because there is no reason to. Because we have already ascertained that they are not valuable enough. To store. Does that make sense? So in that case, perhaps part of our looking through the backlog of unsighted sources should be applying a filter and that filter can be its own subagent check which basically assesses whether or not a source is above a certain threshold of usefulness or reliability or whatever else. I mean, we already have a rule that we do not use Grokopedia, for example. So, like, we should certainly not be storing any Grokopedia pages. And that doesn't even need a subagent check. That's just like a general rule. And I don't know if there are other things of this nature where we would blacklist an entire source. Or, I mean, I guess we might if we found that, like, an academic author was known to have plagiarized or fabricated data, then we might want to basically have a rule against ever citing something that they were an author on or something. Although I don't really think that that's a problem that we need to design around because I don't think that a lot of people are going around fabricating data on Edo period farms or whatever. But something like Grokopedia needs to be banned because it is AI generated without the benefit of the kind of rigorous checks that we are doing.

it is of course okay in any case to mark that we don't know why something was consulted originally but that you know anytime we do consult it in the future then we record that

So how does that sound? I suspect that we will end up storing far fewer than the nearly 3,000 unsighted sources once we apply this kind of filter, which seems good, though in a sense it will be more work in order to filter things out because we will be rereading those sources, at least the ones that we are able to find and download, and then performing this kind of assessment in a subagent check. And then I guess in order to even develop the subagent check, we kind of need to think through what we want the threshold to be for when something appears to have any relevant information. And then I guess we need to decide whether we want to store specific reasoning for that source about why we are not storing it, or maybe that's just like a categorization thing where we have kind of just a few high-level reasons why we choose not to store something. Like, the source's title was misleading, and the blog post was actually about something else, or if a source about rice yields turned out to be entirely about modern industrialized mechanized farming such that no information that it has should be used because any numbers that we pulled would simply be misleading, etc, and then it becomes a simple matter of tagging. And there could, I suppose, be multiple reasons why a source gets tagged as not being stored. I don't know. Either way, I guess we first have to think about what the subagent check would look like that evaluates a, an unsighted source for suitability for being stored at all, and then we would do the write-up that I had talked about of the source and what it is and how applicable it is for the sources that were deemed to meet that threshold such that we could imagine citing them in the future.

I don't know. What do you think about all of that? Don't actually do any work on this yet. I just want to hear whether you think this is a good thing to incorporate into this feature before we move forward. And if there's any areas where you think I'm missing something, or if anything that I've said sounds like it's not a good idea to you, then I want to talk through all of that before we proceed.

The session's answer (summary), the points the spec starts from:

1. "Not useful for THIS question" (the ledger's outcome) and "not worth keeping" (the filter's verdict) are different;
   the filter judges with no question in hand. Proposed threshold: holds checkable evidence about premodern East Asian
   building, farming, settlement or daily life, from a kind of source we would cite.
2. The filter mostly reads the page cache's saved text (~3,000 earlier reads), batched several pages per dispatch; only
   the keepers are fetched whole and archived.
3. Cited sources are exempt (they back a footnote); running the filter on them is its positive control, known junk its
   negative, three runs a leg before it is trusted (the project's rule for a judging agent).
4. Not-kept reasons as a small fixed tag set, several allowed, an optional one-line note: off-topic (the title misled),
   modern-only (industrial or mechanized practice; its numbers would mislead), unreliable kind (AI-generated, content
   farm, unsourced aggregator), no substance (search, listing, index or stub page), duplicate (a mirror of a kept copy),
   unreadable.
5. Banned sources (Grokipedia) are a domain blocklist enforced by tooling at fetch, archive and citation; the filter may
   propose additions, the GM approves. An author blocklist is not designed for.
6. What a wrong rejection costs: the URL, its reasons and usually a Wayback copy remain.
7. Kept uncited sources get the same write-up as a cited one (tags, summary, applicability, limitations) with the same
   checks; the attempts log (question, what was looked for, what came of it) covers cited and uncited sources alike, and a
   research pass consults it first. Old reads with no known reason stay marked unknown (the GM: "it is of course okay in
   any case to mark that we don't know why something was consulted originally"); every future consult records its reason.
8. Land 309 first, this as its own feature.

The GM:

Okay, yeah, I do like the idea of landing what we've done in main prior to starting this as its own separate feature. So how about you do that and finish the feature that we are already in the middle of with this new feature about filtering and cataloging and tagging and doing source write-ups of our uncited works being its own separate feature, which you can also file now. But then we don't actually start that until the previous feature has landed in main.

## The open questions (GM, 2026-10-02, after 309 landed; still not to start)

The GM (verbatim; "unsighted" is voice-to-text for "uncited"):

Uh, let's resolve those two open questions on feature 312, even though I do not actually want to start on it yet.

I think I do want unsighted pages ( Side note, you should update your memory of words that speech to text tends to get wrong by saying that unsighted should generally be read as uncited ) to appear in a separate section. Like maybe under sources, then in addition to all of the categories we have, we have a uncited section which just then has the same structure where there will be like a pre-modern Japan or pre-modern China sub-subsection under the uncited sub-subsection. Or maybe it could just be its own top level section underneath Sourtces called Uncited Sources. if that makes more sense. I don't know whether it would end up making sense to include my own L7R setting notes in the unsighted section. So we should probably never do that, just as a general rule. Uh, however, I do think it makes sense that if we ever have any original L5R setting notes from like the L5R wiki, which we actually do cite in a few places, then that could go there.

Now, can you remind me what the three pages are that you're talking about that we have an open question about? I'm guessing they are three pages that we are no longer able to find or something?

Settled: kept uncited sources appear in the built record, in their own "Uncited sources" part of Sources, grouped by the
same sections as the cited works (Premodern Japan, Premodern China, ...). The GM's L7R setting notes never go there; L5R
setting-wiki pages may.

The three pages (answered by the session): not lost - all three were captured whole and are archived. They are the
consulted backfill's first three captures before the GM held it, all from the Chinese Academy of Sciences agricultural
history site (agri-history.ihns.ac.cn): a short history of Chinese fish farming by Hu Hsing-hua, the classical
fish-farming text 養魚經 (attributed to Fan Li), and an essay on the Song agricultural treatise 陳旉農書. The question was
only what happens to them if the filter rejects them. The session's proposal, for the GM to confirm: they go through the
filter like every other uncited page; a rejected one loses its manifest row and gets a not-kept line, and its copy stays
in the archive's git history, since the project never rewrites history.

The GM (verbatim):

Yes, I agree that they should go through the filter like any other unsighted page, and then their disposition should just be whatever the filter ends up saying.

Settled: the three pages go through the filter like every other uncited page, and the filter's verdict is their disposition.

## Banned sources (GM, 2026-10-02, verbatim; still not to start)

The session reported that the Grokipedia ban is a written rule only (`docs/research-doctrine.md`; three citations were
dropped by hand in feature 143) with no tooling behind it, and that no Grokipedia page is on the sources-consulted ledger.

The GM:

Oh yeah, we should definitely make sure that our citation rules are enforced by tooling and not just remembering to do the correct thing. Like if we can literally block ourselves from even checking Grokopedia, that's good. In my view, though, that kind of block might not be appropriate for other things that we end up forbidding from being cited. things that we forbid might be hosted on the same domains or whatever as things that we do not forbid. And I mean, I guess I'm not opposed to Grokopedia being checked if it was in order to find other sources that we could cite, but we should never ever even so much as list it as a potential source of information. Like it doesn't even get a write-up as something that we considered and rejected. It is just blacklisted across the board. And to be honest, I don't know that it is worth checking because it has so many hallucinations that maybe it is better to just blacklist the domain. I don't know. Either way, it should be tool enforced. And if that's not already part of that, then we should make sure that feature 312 adds the tooling support for whatever we deem is appropriate. Thanks.

Settled for the spec: every citation rule is enforced by tooling. Grokipedia is banned across the board: never cited,
never written up, never on the ledger or in the archive, never listed as a source considered and rejected. Whether it
may still be opened to find other sources is the spec's to decide; the session's recommendation is to block the domain
at every fetch route too, given its hallucinations - a page found through it can be found another way. Other forbidden
sources are banned at the CITATION, by URL or pattern, not by domain, since they may share a domain with sources that
are allowed.

The GM (verbatim):

I accept your recommendation about blocking Grokopedia entirely. And that may end up applying to other domains as well if we, for example, determine that another domain is similarly AI generated. Then we would treat it the same as Grokopedia. So like, it's not that we are putting Grokopedia into its own special category that could only ever apply to it. It's just that Grokopedia is in a category for which I do not personally know of other things that are in that category. but other things may join it in time, and that should be made part of feature 312.

Settled: a BLOCKED-DOMAIN category - AI-generated sites, Grokipedia its first member - blocked at every fetch route as
well as at citation, write-up, ledger and archive. It is a list other domains can join (for example, one the filter or
a session finds to be similarly AI-generated, added with the GM's approval), not a rule for Grokipedia alone. Sources
forbidden for other reasons are banned at the citation, by URL or pattern.

## High-risk sources (GM, 2026-10-02, verbatim; still not to start)

The session reported that 15 cited sources still refuse an automated fetch after a retry (`prep.md`), 10 of them not on
the GM's download list, and offered to add those 10 to it.

The GM:

I actually don't think that we should just add those 10 to the list of things for me to download because if we are not able to access them now, then we must at least consider the possibility that we never actually did and what we think those sources said is hallucinated. So I think that we actually need those 10 to be in their own special separate category, which is a much higher priority than the regular to download list. So I would like those to be part of their own special section in which you prepare a separate list of what they are in the same format as our regular to download list. And then save that in the spec kit feature directory. And then before this feature can be complete, then I must download those 10 items or report that I have not been able to find some of them. And then we must confirm that they say what we think they said. because we have definitely encountered situations in the past where what a source actually says differed from our summary of it. And that is why we implemented the subagent checks that we now have. But these 10 sources that we cannot find right now should be treated as being at an unusually high risk. of this being the case. Because all of our other sources were checked, to my knowledge, by our current subagents. But if we can't find these 10 now, then that implies that they might not have been. So our feature should be updated to include that. Thanks.

Settled for the spec: `high-risk-sources.md` in this directory lists them in the download list's format, ahead of the
regular list. Feature 312 is not complete until the GM has downloaded each (or reported one cannot be found) and a
`source-reader` and `quote-check` have confirmed each says what the record says. The session put all 15 on it, not only
the 10: the GM's reasoning applies to the 5 already on the download list as well, since they too are cited and cannot be
fetched now. The list is in two tiers (7 a footnote rests on, 8 that back no claim); whether tier 2 is required for completion was put to the GM (answered below).

## Never-read sources and the download list (GM, 2026-10-02, verbatim; still not to start)

The GM:

I suppose that we might also want to update this feature to include a categorization of sources that we have seen referenced but were unreachable. I mean, I don't know what that would imply about what we do in the future, but um, I don't know, just that does seem like its own category that is worthy of its own type of tagging, right? And then to be honest, our list of stuff to be downloaded should also probably be copied and checked in. Somewhere. Now, the copy that I am using should be an actual copy and not the canonical source, but this file is now large enough and it is important enough that it deserves to be in source control somewhere, and I would think that our private repository of diagram research seems like an appropriate place for it. Though, I don't know, maybe it should actually just go into the main diagram repo? What do you think?

The session's answer (summary): a never-read state as a tag (today only free text in entries' comments), which makes
the high-risk list a query rather than a hand-made file; three states kept apart - read, never read but referenced,
unreachable now though once read. The download list in the MAIN diagram repository, not the archive: it holds no
copyrighted text, sessions write to it like the rest of the record and the pointer check can hold its "Rests on it"
lines; the high-risk list its top section; the GM's file in `academic-sources/` a copy generated from it.

The GM:

to answer your question about the decision for me, then yes, tier two should be required before feature 312 closes. And moreover, if we cannot find these sources because we cited something that is paywalled, then we must, as part of this feature, update our research findings to remove those as sources. And we could move them into our list of things that we kind of know are unavailable, which actually, now that I think about it, then saying that something is paywalled is probably its own tag, because it is useful for us to record what things in the past you were able to get versus things that timed out versus things that I was able to get, which would then be stored, versus things that I was able to get only a like partial summary of, like in cases where I'm able to copy the abstract but not anything else, versus things that I found require a paid login like through a university system thing or, you know, paying for the paper itself or whatever. Um, like those, you know, kind of are all different cases and we should make sure that the tagging system that we are implementing in feature 312 accounts for all of these so that in the future when we are doing other research and then we say, hey, I just saw this paper that came up, we can check and then we will see if, for example, we know to rule it out because it is restricted access. And of course, perhaps a later feature could go and check whether restricted access papers have opened up, because that does happen eventually. I mean, sometimes things start off paywalled, and then after a certain number of years, they become open. But that wouldn't be something that we would check anytime soon, like I wouldn't bother checking that for the remainder of this year and probably not even bother checking it next year either. But, you know, maybe in a few years we would do another pass just to see if anything that was paywalled is now uh, open access. And that is the kind of future work that this kind of extra tagging would do for us. So we should make sure that that is part of the system.

And yes, your proposal does sound right for how to handle the list of things to download. Though I think I probably do want the format of that file to change slightly, where it would be useful for me to be able to have a space that is already set aside, where I can either check a box (i.e. turning `[ ]` into `[x]`) indicating that the file has now been downloaded, or check another box indicating that it has been found to be paywalled, or check a third box indicating that I was able to download some portion of it. Like, you know, for papers where the abstract is freely available, but the full text of the paper is not. And then maybe a fourth option for me finding something, but that whatever I found, whether it's the full paper or a partial summary, was found elsewhere, like through a Google search or something, that was different than the Google search that you linked, and that this would supplement one of the other checkboxes. So like if I any time I checked this one, then I would have checked one of the other boxes as well. Something like that. And then that is something that I would want to edit. So I don't know. We need some procedure for me to have a file where I am marking my work as I go, because that is helpful for me. But I understand what you're saying about some version of this file being kept in sync where no one edits it. So maybe this is just a case where I make a copy myself, and then I would inform you when it's ready to ingest, and then you would pull down my copy or something, and then you know, you could update the canonical version and then sync that, and then I could sync your version to mine when I am ready to do so or whatever. I don't know, something like that. Um, I don't really care that much about the specifics, except insofar as this system, like coming up with this system should be part of this feature, even if actually going through and then running through this list is something that we do as part of a different feature. But I want implementing this system to be maybe like the first thing that we do as part of this new feature so that I could begin work on this downloading before this feature is complete if I end up having the time to do so. Which I probably won't, but it would be nice to have the option. How does that sound?

Settled:
- Tier 2 of `high-risk-sources.md` is required before 312 closes, as tier 1 is.
- A cited source that cannot be got because it is paywalled is removed as a source from the research findings in this
  feature, and recorded as known-unavailable. (The session's refinement, offered to the GM: a citation is removed where
  the passage it quotes cannot be confirmed from what IS readable - a footnote quoting a freely readable abstract stands;
  the claim keeps an absence note where that source was its only support.)
- An ACCESS tag on every source, with the date last checked - the states the GM named and the session's: read by us
  (open); open in a browser but refused to us (bot-refused); timed out or a server error (down); 404 with no copy
  (gone); the GM's full copy; the GM's partial copy (an abstract or excerpt); paywalled (a paid or institutional login);
  never read (referenced only). A later feature re-checks paywalled sources for open access - future work, not before
  2028 by the GM's estimate.
- The download list in the main diagram repository, canonical; the GM keeps a COPY to mark as the GM works, with per
  entry the boxes downloaded / partial (abstract or excerpt) / paywalled / not found, and found elsewhere (ticked with
  one of the others, with where) - "not found" the session's addition, from the GM's earlier "report that I have not been
  able to find some of them". On the GM's word "ingest", the tooling reads the ticks (entries matched by key), updates
  the canonical list and the tags, and archives the files dropped in `academic-sources/`; the GM's copy is replaced only
  on the GM's "sync".
- This system is built FIRST, so the GM can begin downloading before the rest is done. The session's proposal, put to
  the GM: split it into its own small feature (313: the access tags and the download-list system) that lands on main
  first, since a feature with an open task lands nothing - the system built as 312's first task would not reach main
  until all of 312 was done.

`high-risk-sources.md` also lists the 7 cited URLs still unreachable after a retry on 2026-10-02 (the other 7 of 14
came back: 6 archived, two of them the GM's own notes on GitHub, and 1 partial).

