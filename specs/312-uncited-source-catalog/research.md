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
does not admit; that the record CITES them is a finding for the GM, not a fault of the filter.

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
