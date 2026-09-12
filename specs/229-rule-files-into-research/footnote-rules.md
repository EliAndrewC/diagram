# Footnote rules - resolving a page's `FN-PENDING` marks (feature 229, the source pass)

You resolve every `<!-- FN-PENDING: ... -->` comment on ONE research page, using the source-reader verdicts
the session recorded in `research.md` R4 (the tables headed "R4 - source-reader batch 1 / 2 / 3"). The verdicts
are the evidence; you do not fetch anything and you never write a quotation you did not find, verbatim, in an R4
row (the readers' reports are quoted there; where R4 gives only a summary of a passage, the session will paste the
verbatim passage into your page's brief).

## The two footnote forms (research/CLAUDE.md, "A citation LINKS to a page where its quote can be READ")

- **CITATION**, when the verdict is READ and the URL is a public page: on the CITATIONS page, in
  `<section class="footnotes"><ol>`, a new `<li id="fn-N"><a href="URL"><code>key</code></a> - 「passage verbatim」
  (one clause on what it bears on, when not plain) <a class="fnback" href="../<page>.html#fnref-N">back</a></li>`
  (from `citations/cities/`, the back link is `../../cities/<page>.html#fnref-N`). A non-English passage is given
  as `「English translation」 (translated from the Japanese by this project; original: 「原文」)` - the original
  after the note, the translation first. On the RESEARCH page, after the sentence: `<sup class="fn"><a id="fnref-N"
  href="citations/<page>.html#fn-N">N</a></sup>` (from `cities/`: `../citations/cities/<page>.html#fn-N`). N
  continues from the page's current highest footnote number; every `fnref-N` has exactly one `fn-N` and the reverse.
- **ABSENCE**, when the verdict is NOT-FOUND, SUMMARY-ONLY, or READ only on a page this project will not link (an
  unauthorized scan): the same `<li id="fn-N">` carrying `no publicly readable source (searched 2026-09-12: <what
  was tried, from the R4 row>)` and the back link - no key, no URL. The sentence on the research page keeps its
  reference and its honest wording ("rests on general reading", "a guess") - the absence note is what makes the
  label checkable. Do not name a retired rule file by its filename anywhere, not even in a comment.
- **CONTRADICTED**: the research page's sentence is REWRITTEN to say what the page says (the R4 row states the
  correction), with a citation footnote to the page that contradicted it. Nothing says what the sentence used to say.
- **READ in part**: cite the part that is on the page; the rest gets an absence note or is dropped from the
  sentence, as the R4 row says.

Then delete the `FN-PENDING` comment. Every mark on your page is resolved one of these ways; none survives.

## Keys

- A key that already exists in the registry (`/tmp/claude-1000/-diagram/4c101eea-20c6-464f-9359-42d291f0b54f/scratchpad/registry-keys.txt`
  lists them with their citation lines) is linked to the URL its citation line carries, or to `SOURCES.html#key`
  when the line says `URL: none` or `SUMMARY-ONLY` (`../SOURCES.html#key` from `cities/`).
- A NEW key is coined ONLY from the names R4 gives (`daihachiguruma-jawiki`, `stone-routes-enwiki`,
  `lowtech-chinese-wheelbarrow`, `itabashi-kotobank`, `dobashi-jawiki`, `meander-enwiki`, `shakkanho-jawiki`,
  `kateisaien-jawiki`, `fao-farm-structures-cattle`, `tnau-cattle-housing`, `omamori-enwiki`, `monzenmachi-jawiki`,
  `qingming-enwiki`, `kasoba-jawiki`, `kofukuroman-sanmai`, `tokyohakuzen-yoyogi`, `tanigawa-1992`,
  `osaka-umedahaka`, `bochi-jawiki`, `ryobosei-jawiki`, `cssn-citang-panyu`, `chinju-no-mori-jawiki`,
  `tudigong-enwiki`, `hinomi-yagura-jawiki`, `hansho-kotobank`, `machibikeshi-jawiki`,
  `dongjing-menghualu-wikisource`, `watersa-junction-angle`, `pingyao-gucheng-zhwiki`) - never a name of your own,
  so two pages citing one page coin one key. You do NOT edit `SOURCES.html`: for each new key you use, your report
  carries the registry entry in this exact form, which the session lands:

```
<h3 id="key"><code>key</code></h3>
<p>Site or author, title  (URL)<!-- READ 2026-09-12 --></p>
<p><em>What it is:</em> one to three sentences - the kind of work, its author or publisher, its date, what it is about.</p>
<p><em>Why it applies, and its limits:</em> one to three sentences - why it is a good source for what we use it for, and its honest limits (a tertiary summary; a modern standard; a company's own history; a different region or period).</p>
```

- The section's `<p><strong>Sources:</strong> ...</p>` roster lists every key footnoted in that section, as a link, with
  a parenthetical saying what the work contributed (never when or how it was read); a key with no footnote in the
  section is not on the roster.

## The page's form still holds

Comments for bookkeeping; no `feature NNN`, task id, fetch verdict or "used to say" in visible text; hyphens only,
American spelling in your own words, the source's own spelling inside 「」. Run
`python3 /tmp/claude-1000/-diagram/4c101eea-20c6-464f-9359-42d291f0b54f/scratchpad/check_page.py <page>` before you
finish: 0 FN-PENDING, 0 footnote problems, no new visible shape.

## Your report

1. Per `FN-PENDING`: the anchor, the form used (citation / absence / rewritten-and-cited / dropped), the footnote
   number, the key.
2. The registry entries for every NEW key you used (the block above, verbatim HTML).
3. Any sentence you rewrote because the verdict was CONTRADICTED, before and after in one line each (for the
   session's record, not for the page).
4. Anything R4 did not cover that your page needed.
