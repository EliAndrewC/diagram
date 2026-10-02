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
