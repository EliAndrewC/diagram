# Research: feature 312

## R1. The filter's trust bar: 19 verdicts in 20 a leg, three runs a leg

A bar the session set (2026-10-02), not a measurement. Three runs a leg is the project's rule for a judging agent (one run
is not a stable oracle; `CLAUDE.md`, the tier test). 19 in 20 on each leg: what a wrong verdict costs is unequal and small - a
page wrongly kept costs one write-up and one check; a page wrongly rejected keeps its URL, its reasons and usually a
Wayback copy (`request.md`, point 6), so it can be read again. A bar of every verdict would make the calibration chase single
borderline pages (a cited page whose one useful line is a single figure); a bar much below that would let one verdict in
ten be wrong across ~2,700 pages. The controls' sizes and the runs are recorded below once run.

## R2. Calibration runs (T23): passed, three runs a leg

Observed 2026-10-02, method: `measurement/calibrate.py` built four bundles of 80 pages - 40 POSITIVES, a seeded random
sample of cited pages with saved text (800+ characters, under 15,000 estimated tokens), and the 40 NEGATIVES this session
labeled in `measurement/negatives.json` (17 Kotobank ids that resolve to an unrelated entry, 10 error, sign-in, for-sale
or empty pages, 13 blogs, Q&A threads, content farms and commercial posts) - shuffled under opaque ids, the labels kept
outside the bundles. Each bundle judged three times by a fresh agent; scored by `_uncited.score`.

| run | positives kept | negatives not kept |
|---|---|---|
| 1 | 38 of 40 | 40 of 40 |
| 2 | 38 of 40 | 40 of 40 |
| 3 | 38 of 40 | 40 of 40 |

Every run meets the bar of 19 verdicts in 20 a leg (R1). The two misses are the SAME two cited pages in all three runs,
each judged `unreliable-kind`: a funeral company's promotional glossary on household graves
(`ikikata.nishinippon.co.jp/term/6815/`) and a real-estate firm president's blog on persimmon trees in farmyards
(`ameblo.jp/toyoko-housing/entry-11418946119.html`). The filter reads them correctly as kinds of source the threshold
does not admit; that the record CITES them is not a fault of the filter. **Decided 2026-10-02 by a research pass**
(research decides, GM 2026-10-02), not put to the GM: both citations stay. For house-plot graves by region the record's
other sources are a stonemason's blog (`eisi-yashikibaka`) and a personal blog (`yashikibaka-ibaraki-blog`) - nothing
stronger to put in its place - and `ikikata-yashiki-bochi` is quoted only for its hedged "it is also said"; for the
persimmon, `takehara-2004-yashikirin` (scholarship) lists it among the most frequent homestead-grove trees at Tonami but
not "in every dooryard". Both write-ups already state the kind and the limit (a modern writer's impression, never a
measured prevalence), which is what the record owes a weak source it keeps.

**How the agent was dispatched.** The defined agent file (`.claude/agents/source-filter.md`) is not dispatchable by name
until a session restarts (the harness lists agent types at session start; measured: "Agent type 'source-filter' not
found" on 2026-10-02). So the calibration AND the production run dispatch an ad-hoc Opus agent whose prompt points at
`CONTRACT.md` - the agent file's body, copied into every bundle by `_uncited.write_bundle` - and forbids reading
anything else. The contract is the same text; the difference is that an ad-hoc agent carries the session's CLAUDE.md
files and effort rather than `omitClaudeMd` and medium effort. The calibration measured the agent exactly as the
production run dispatches it, so the trust it earned applies to that run; a later session dispatches `source-filter` by
name.

## R3. What a whole page costs the filter, and how a bundle is sized

Observed 2026-10-02, method: every uncited page with saved text in the page cache (1,200), its text's estimated tokens -
a CJK character counted as one token, any other character as a quarter (`_uncited.tokens`). Total about 4,880,000
tokens; median 1,923 a page; 90th percentile 7,236; largest 343,129; 26 pages over 20,000. Characters alone mislead for
the Japanese and Chinese pages, which are most of the set (ja.wikipedia, kotobank, zh.wikipedia and zh.wikisource are four
of its five largest hosts - `prep.md`): 150,000 characters of Japanese is about 150,000 tokens. So a bundle closes at
about 150,000 characters (plan D5) OR 60,000 estimated tokens, whichever comes first, and a page is cut into parts of
20,000 estimated tokens (a file the agent's Read takes whole). The 1,643 pages without saved text are fetched first
(`make uncited DO=fetch`); at the same mean the whole set is about 11 million tokens, about 190 bundles.

## R4. The eight cited respellings (FR-022)

Observed 2026-10-02, method: each URL the ledger marks `cited:<key>` with no manifest row, matched to its key's manifest
rows (`_archive.row_files`) and the registry. Six are covered - the key's own spelling is archived:
`ndl-crd-shakkogyu` (the same page; the ledger's spelling differs in an entity), `kochi-hantei-jstage` (the `_pdf` the
entry cites, of the `_article` page read), `daozuofang` (`zh.wikipedia.org/wiki/` for the `zh-hans` variant read),
`qimin-yaoshu-zhongzhu` (the `zh-hant` page for the `action=raw` read), `daqing-luli-yejin` (卷十九 for the 兵律 page read),
`guangdong-xinyu-22` (`zh-hant` for `zh-hans`). One mark, `1073shoso.jp/...id=18666):`, was a typo of a cited URL with
`):` stuck to it and is not on the set. One is NOT covered: `minzoku-kinkyu-chosa-jawiki` names a key no registry entry
holds - the mark was made and the entry never written - so `ja.wikipedia.org/wiki/民俗資料緊急調査` is uncited and is judged by
the filter like any other page. `_uncited.cited_marks` keeps the six out of the set by rule.

## R5. The page cache's imported copies: some are another page's text

Found 2026-10-02 by two write-up drafters (a page whose saved text was another article) and confirmed: the page cache's
entry for `https://ja.wikipedia.org/wiki/村` held the article 砂利道 (gravel road), its origin
`import:/tmp/l7r-check/271-w1-pages` - feature 288's one-time import of the saves earlier sessions left under
`/tmp/l7r-check`, which filed some saved files under the wrong pointer. Measured: 1,122 cache entries are imported copies;
of the filter's verdicts, 690 kept and 282 not-kept pages were judged from one. A seeded sample of 40 of those, each read
live and compared by character 4-gram overlap over its first 5,000 characters (`_uncited.same_page`, a third or more =
the same page; method: `make uncited DO=verify`, observed 2026-10-02): 38 the same page, 2 another page's text (5%).

What it cost and what holds the record: a quotation check never read an imported copy (`_quote_verbatim` asks the cache
with `exact=True`, which an import never serves - feature 288's own rule), so no footnote's VERBATIM verdict rests on one;
but a check bundle's saved page, a source-reader's or a source-applicability's, is served from the cache without that
rule, and so was the filter. The fix (constitution XIV, the defect is the cache's): every imported entry is read live and
replaced (`verify --all-imported`), each recorded `same`, `misfiled` or `unread` in `import-check.jsonl`; a page found
misfiled loses its verdict and its write-up and is judged again from the live text.

**The measure over-flags, measured 2026-10-02 on the full run's first 720 pages:** 35 flagged misfiled, and reading
each one's write-up or not-kept note against its URL found 33 of them the right page - 25 entries and 8 notes that
describe exactly the subject their URL names (平遥文庙, 理坑村, 薬医門, the Sohu county-yamen column ...). Two were
another page's text: `ja.wikipedia.org/wiki/村` (砂利道, ruled a duplicate of `jarimichi-gravel-jawiki`) and
`ja.wikipedia.org/wiki/石橋` (ruled a duplicate of `machiwari-jawiki`). Why: a Wikipedia article's first 5,000
characters are mostly the site's navigation, and the skin changed between the saves and the live read, so a short
article's 4-grams overlap under a third with its own live page. The live text replaced each copy either way (a cache
should hold the page as it is), so the fix is in what a flag does, not in the measure: a flagged page's imported copy
is now kept beside it (`imported.txt` in its cache entry), the flag is confirmed by reading, and only a confirmed one
loses its verdict and entry through `make uncited DO=requeue URL=<u>`, which sends it back to the filter. Requeued:
村, 石橋, and two Kotobank URLs whose drafter found another entry's text (`竈-39622` serves 大目付 and `道切り-139424`
serves 三保の松原 live too - Kotobank picks the entry by its number, so the URL itself names that page), and
`kunishitei-kaibara-han-jinya`, whose page saves as a 535-character shell. Not built: a better same-page measure.
Calibrating one needs pairs known to be the same and known to differ, and the imported copies of the 35 were replaced
before this was seen; the kept copies make the next run's flags calibration data.

**Encoding, the second fault the live read surfaced (same day, the run's resumed half):** some imported copies were
mis-decoded - a Shift-JIS student essay and a JUGEM blog saved as mojibake and ruled `unreadable`, a village page saved
as its title and ruled `no-substance` - and read live they are whole pages. And one live read was the mis-decoded one:
`zj.cnr.cn`'s GBK page came back as replacement characters and replaced a good copy. So: a read with more than 1% U+FFFD
(`_uncited.garbled`) never replaces a copy; `make uncited DO=copy-verdicts` lists every filter verdict whose note blames
the saved copy (mojibake, a shell, a title only, a challenge page) on a page the check has since read live into the cache
readable; each is read, then requeued or marked `DO=stands URL= NOTE=`. Of the 10 it listed: 3 requeued (2 kept and
written up, the essay ruled unreliable-kind on its own text), 7 stand (5 Kotobank URLs that serve the entry judged, the
Tonami bulletin still font mojibake past its frame, the Palace Museum page still a viewer shell).

## R6: a long work is read whole by several readers (2026-10-02)

**Found:** the Read tool returns about 60,000 characters of a file, and the drafting parts were cut at 20,000 estimated
tokens - up to 80,000 characters of English. The drafters of two book-length works (Staunton 1797, 11 parts; Esherick and
Rankin 1990, 17 parts) said so: each read only the head of each part, one skipped whole parts. A whole book is also more
than one agent can hold (1.4 MB).

**Decided (deliberate, the contract's "read whole" kept):** parts are capped at 50,000 characters as well
(`PART_CHARS`, tested); a work too long for one agent is read by several readers, each taking three or four parts whole
and writing notes (span, every passage on settlements and buildings with a quotation, limits, and the first and last
line of each part as proof of the whole read), and the drafter writes the entry from all the notes. The partial-read
entries were set aside unwritten (`entries.partial-read.jsonl`). Priced: one drafter told to page through every part
(over its context for a 1.4 MB work); write-ups that state what was read (breaks "read whole").

## R7: SC-007, every ledger row has an attempt line (2026-10-02)

Measured over the host's sources-consulted ledger: 8,541 rows naming 4,905 URLs; every URL has a line in
`research/source-attempts.jsonl`. Three of them did not before a catch-up: feature 315's session read them on main's code,
which writes no attempt line until this feature lands. `make attempts`' seed therefore now writes a line for every
ledger row with none (matched by URL, day and feature), and the push-time re-run of it catches the rows sessions write
between this measurement and the landing.
