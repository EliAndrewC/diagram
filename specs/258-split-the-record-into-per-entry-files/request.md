# The GM's request (verbatim, 2026-09-20)

<!-- SOURCE: GM NOTES -->

Sent after the session measured, across 284 transcripts, that a research page is 24-98% of everything
that enters a checking agent's context (`quote-check` 90%, `record-format` 89%, `entry-drift` 82%,
`source-applicability` 98% on `SOURCES.html`), while the main session's own reads of `research/` are
0.56% of all tool output and already 89% partial.

## The first message - the design question

> I've been trying to optimize token usage on this project, specifically with regards to the research that we do. One of my concerns is that our HTML pages, which explain our research, have grown very large. For example, research/archetypes.html is quite long and citations/archetypes.html is also quite long. Now the citations page, I believe, is automatically assembled from a script which reads a couple of JSON files, if I am not mistaken. So that part is probably okay so long as the size of the JSON files that you are editing by hand are fine. But basically, what I'm trying to figure out is whether it makes sense to split up any of these files. In general, if you had to edit files that are hundreds of kilobytes, then that often requires actually ingesting and reading those files in ways that cost tokens. Whereas, if everything is split into smaller files, then you have to read an index to know where to look and then read individual files. Thus, what I'm trying to figure out is whether it makes sense to do things like split our questions into individual files and split our citations into individual files so that they get assembled into documents that are identical to what we have now. through the same scripted process, but where when you have to make an edit, then you are opening a file which is relatively small. So I think this probably does make sense as an approach where instead of having research/archetypes.html we would have research/archetypes/ as a directory. And then each individual question is its own file inside that directory with a prefix like `01-`, `02-`, etc in order to deterministically set the order in which those questions will appear on the assembled page. The question then becomes whether we would have an index or whether the names of the files themselves would be things that you would use a find command or whether you would just grep to figure out which files it is that you need. I suspect that in order to save tokens, then a Claude.md in that directory would specifically instruct you to use find and grep commands rather than trying to read all of the files yourself when you are trying to find something specific. Again, this is just a guess because I'm not sure what the best practices are here, but this seems like something that would help. What do you think?

## The second message - the approval

> Oh, gotcha. So, like, the agents that are having to do the checking are basically consuming a lot of tokens for things that they are not even checking themselves. I get it. I was wondering why that was eating up so many tokens. That's really good context, thanks. Yes, please. Create a spec kit feature for this and then go ahead and implement it start to finish. I agree with all four of your suggestions on the things to decide. So go ahead and do that as part of it.

<!-- /SOURCE -->

## What "all four of your suggestions on the things to decide" names

The GM approved, verbatim from the session's answer they were replying to, the four bullets under
"Things to decide before it's specified":

1. **Ordering prefix.** "Gapped (`010-`, `020-`) so inserting a question doesn't renumber the directory."
2. **Footnote numbers.** "Assembly *could* renumber in document order, which removes a real hazard today
   (numbers are already out of document order on `archetypes.html`). Worth doing, but it's a second
   feature's worth of surface - it moves every `fn-n` anchor in one commit." The GM's "do that as part
   of it" brings the renumbering INTO this feature.
3. **Byte-identity and the gate.** "The assembled pages stay committed (the reader opens them from disk,
   same reason as `glossary.js`), and assembly needs a `--check` staleness test at the gate, exactly like
   `make citations`. First landing should be byte-identical output so the diff proves the split changed
   nothing a reader sees."
4. **Map modal links.** "Map modal links (`research/<page>.html#<section-id>`) are local and relative, and
   the assembled output keeps them, so nothing external breaks."

## The three stages the GM said yes to, in the order the answer ranked them

> If you want it, I'd claim a number and spec it in three stages in the order above, since stage 1 alone
> captures the single biggest measured read.

1. `SOURCES.html` -> `research/sources/<key>.html`, one file per source key (920 entries, median 1.2 KB).
2. Research pages -> `research/<page>/NN-<slug>.html`, one file per question (19-39 sections a page,
   3-9 KB average).
3. The citations pages' hand-authored notes, split by the SAME section as the prose so a question and its
   footnotes are siblings; the works section stays derived.

## The session's two further points the GM accepted with "I get it"

- The savings come from SCOPING the checks: the split makes scoping possible, but `record-prepass`,
  `quote-verbatim` and `_entry_owed` need a per-section mode to collect it.
- The lookup rule is grep and `ls`, with NO hand-maintained index, and it belongs in `research/CLAUDE.md`
  and in each agent's own contract - not in a new per-directory `CLAUDE.md`, because the defined agents
  launch with `omitClaudeMd: true` (feature 256) and would never see one.
