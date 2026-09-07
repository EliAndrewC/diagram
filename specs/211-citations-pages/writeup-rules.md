# Writing a source's two write-ups (feature 211)

You are drafting, for each registry key in your batch file, the two paragraphs the GM asked for
(2026-09-07). Read the GM's words first - they are the whole requirement:

> "at the top of the citations page, before we begin listing the number of citations, we should list what this
> paper is, its name and its authors, and then a brief one two three sentence summary of what the paper is. We
> should additionally then have another one to three sentence summary of why we consider this a good and valid
> source. For what we are using it to look up. This explanation should include honest limitations. For example,
> some of our research may be from the year nineteen hundred, which is well within the modern era and well after
> the beginning of the industrial revolution. However, much of the land surveyed in China during that period was
> not yet industrialized. And, therefore, the comparisons to premodern societies are still quite useful. However,
> we should still be honest that there were modern agricultural techniques which would have been employed in the
> year nineteen hundred, which would not have been employed in our fictional setting or in the historical imperial
> Chinese periods and imperial Japanese eras. which we are using as a basis for our fictional setting. Similarly,
> We also cite sources that are about Korean rice farming. This seems fairly valid as Korea is from the same part
> of the world as China and Japan. Therefore, things involving crop yields and village sizes and things of that
> nature should be considered to be largely comparable. But we can still say that we use sources on Korea and
> Korean agriculture because we were not able to find publicly available sources that were more directly
> applicable. That kind of thing."

## The setting these sources serve

Fictional maps of hamlets, villages, towns and cities in a premodern East Asian setting (L7R, a Legend of the
Five Rings homebrew) modeled on imperial China and pre-Meiji (Edo and earlier) Japan. A source is "applicable"
to the degree its era, place, scale and method bear on how such a place was built, farmed, planted, watered,
governed or lived in.

## Your input

A batch file of registry entries copied verbatim from `research/SOURCES.html`. Each entry is:

    <h3 id="key"><code>key</code></h3>
    <!-- cited by: which research pages cite it, and which footnote numbers -->
    <p>the CITATION LINE: the work, its authors, venue, date, URL (HTML comments carry the session's fetch
       records - READ dates and so on; read them for context, never copy them into a write-up)</p>
    <p><em>Used for:</em> what the record took from it</p>

The "cited by" comment tells you what we use the work to look up. Open the research page's footnotes for that
key (`research/<page>.html`, `<li id="fn-N">`) when you need to see the exact passages quoted.

## Your output, per key

Two HTML paragraphs, exactly this shape:

    <h3 id="key"><code>key</code></h3>
    <p><em>What it is:</em> One to three sentences. Name the kind of work (a peer-reviewed article, a
    municipal museum's page, a Japanese Wikipedia article, a 1987 tree survey published by a city archive, a
    tourist board's page, a Ming agricultural treatise...), its authors or publisher when known, its date, and
    what it is about - so a reader who has never seen it knows what they would be opening.</p>
    <p><em>Why it applies, and its limits:</em> One to three sentences. Why it is a good and valid source FOR
    WHAT WE USE IT TO LOOK UP (the "cited by" pages and "Used for"), and its honest limitations: the ERA (a
    modern survey of a premodern form; a 1900s count with some modern technique in it; a twentieth-century
    measurement of a practice that is older), the PLACE (Korea or Okinawa or Taiwan standing in for Japan or
    China; one region for a whole country), the KIND (an encyclopedia is a tertiary summary; a tourist page is
    promotional; a modern how-to describes today's practice), the SCALE (a city's figure applied to a hamlet).
    When a source stands in because nothing closer could be read on a public page, say so in those words.</p>

## Rules

1. Write for the reader of the map - a casual RPG enthusiast, not a session. No feature numbers, task ids,
   fetch verdicts (READ, SUMMARY-ONLY), dates of when WE read it, or how the entry came to be. Plain English.
2. Hyphens only - never an em-dash or en-dash. American spellings. A foreign title may be given in its own
   script with an English gloss.
3. Never invent authors, dates or venues. If the entry does not say and you cannot open the page, say "an
   article on <site>" and leave the author out. Where you CAN open the page (one attempt per host; a refusal
   is recorded, never retried), do, and describe what is actually there.
4. Honest means honest: a Wikipedia article is "a tertiary summary whose figures we take only where its own
   references support them"; a tourist board's page "describes the place for visitors and is used for what the
   place is, not for a number"; a 2021 firewood blog "describes modern practice; the stack height is a modern
   figure we use as an upper bound". A source about the wrong thing is said to be so.
5. Do not repeat the "Used for" paragraph; refer to what we use it for in a few words inside the "why".
6. The GM's own campaign notes (`l7r.md`, `budgets.md`) are canon, not evidence: "What it is" says they are
   the setting's own notes; "Why it applies" says canon decides where history is silent and has no historical
   limit to state.
7. Do not write about what the source does NOT say unless that is the point of the citation.
8. One write-up per key. Return ALL keys of your batch, in the batch's order, as one HTML block, nothing else.
