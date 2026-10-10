# Research - feature 376: does a research group's cost sit in a fixed part, or per thing?

## R1 - the measurement, before choosing a lever (2026-10-10)

**Method** (observed 2026-10-10; method: `measure/fixed_and_marginal.py`, output `measure/results.txt`, over the
sessions feature 347 collected). For each complete group, its cost is fitted by least squares against the things it
checked: a fixed part per group plus a part per thing. This is done for its write sessions, its check sessions, its
agents and the whole, before 274 (R1's window) and after it (the research groups of features 269, 280, 291 and 317).
Feature 269 ran on both sides of the landing.

| (observed 2026-10-10; method: `measure/fixed_and_marginal.py`) | groups | write | check | agents | total |
|---|---|---|---|---|---|
| before 274 | 48 | 3.14 M + 0.374 M a thing | 1.04 + 0.342 | 1.20 + 0.063 | **5.39 + 0.778** |
| 269 before | 12 | 2.70 + 0.347 | -1.20 + 0.558 | -0.36 + 0.199 | 1.05 + 1.113 |
| 269 after | 11 | 1.03 + 0.407 | -2.38 + 0.927 | -0.50 + 0.256 | -1.85 + 1.590 |
| research groups after | 66 | 2.08 + 0.421 | 0.93 + 0.464 | 0.51 + 0.133 | **3.52 + 1.018** |

**The fixed part fell, and the cost per thing rose** (observed 2026-10-10; method: the table above). The fixed part per
group went from 5.4 M to 3.5 M, which is what 274's cap was for. The cost per thing went from 0.78 M to 1.02 M. Feature
269, which ran on both sides, shows the same: 1.11 M a thing to 1.59 M (its fixed part fits near zero over 11-12 groups
and is noise). So 347's R3, which explained the rise as a fixed part spread over fewer things, had the mechanism
backward. This feature was filed on that explanation.

**Where the per-thing cost went** (observed 2026-10-10; method: the same script, every tool call in the complete
groups, with the tokens its result carries over the later turns). Per thing checked, before 274 against after:
- **Reading and searching doubled.** Read calls went from 1.04 to 2.18 a thing, carrying 27 K to 66 K. Web searches
  went from 0.65 to 1.60, carrying 19 K to 39 K.
- **Agents and edits rose.** Agents went from 1.67 to 2.23 a thing, edits from 2.11 to 3.39.
- **`make lines` carries 33 K a thing**, replacing the whole-file `cat` reads 347 measured gone.

The post-landing groups did more research per item. Feature 280 was a sweep asking of each source whether it was
modern-only, which means searching for premodern evidence, often many searches for one item. 269's second half was its
fixes and splits. Neither is the same work as R1's first-pass write-ups, and a cap on session length cannot change how
much searching an item needs.

**What 376's two levers are worth** (observed 2026-10-10; method: the fits above):
- **One check pass over several write sessions** saves at most the check sessions' fixed part, about 0.9 M a merged
  group. Merging the 66 groups in pairs saves about 30 M of 738 M, about 4%.
- **A claims lookup that answers only the claim** saves part of the 16 M `make lines` carried on the claims file, at
  most about 2%.

## R2 - do sessions look at what we have before searching the web? (FR-005, 2026-10-10)

**Method** (observed 2026-10-10; method: `measure/local_first.py`, output `measure/local-first.txt`). Every session
transcript under `~/.claude/projects/-diagram*/`, each main thread and each subagent its own actor, over the calls made
since the source archive landed (feature 309, 2026-10-02T17:37Z). A LOCAL look is a read or grep of `research/`, `make
notes`, `make canon`, `make archive-find`, a check bundle, or, for a subagent, a dispatch naming one. A fetch is HELD when
the archive's manifest (`research/archive/*/*.json`) has a capture of that URL from before the call. A search is ASKED
ALREADY when at least two of its words, and 60% of them, sit in one question's heading id.

**Main sessions look first** (observed 2026-10-10; method: as above). All 23 main threads that searched the web had
looked locally before their first web call. Their 39 fetches included 12 of held URLs, and none of their 20 searches was
on a subject a record question names.

**Agents re-fetch what the archive holds** (observed 2026-10-10; method: as above). 618 of 625 agents that went to the
web started from a bundle. But of their 1,213 web fetches, 946 were of a URL the archive already held:

| agent (observed 2026-10-10; method: `local_first.py`, by agent type) | web fetches | of a URL already archived |
|---|---|---|
| quote-check | 812 | 773 |
| source-applicability | 206 | 68 |
| source-reader | 129 | 91 |
| general-purpose | 57 | 14 |

**Why** (observed 2026-10-10; method: quote-check's surviving bundles and `scripts/record/quote_verbatim.py`,
`check_bundle.py`, `sources.py`). quote-check is handed a script's verdict per footnote. It fetches only the residue,
the pages the script could not read. Two gaps fill that residue with pages the archive holds:
- **The script cannot read a PDF.** `quote_verbatim.py` marks every PDF `NOT-CHECKED`. 512 of quote-check's 775
  re-fetches of held URLs were PDFs, whose archived capture carries the extracted text (`text.txt`).
- **The page cache never asks the archive.** `CachedPages` (`sources.py`) goes from the cache straight to the web.
  `check_bundle.residue_pages` fills a bundle's `pages/` from the cache alone, so a page the archive holds and the cache
  does not arrives marked NOT-CACHED, "fetch it yourself".

So the agent's own `WebFetch` reads the PDF. That is a model-written summary of the page, not its text, which is a weak
basis for a character-for-character check.

**What it costs** (observed 2026-10-10; method: each re-fetch's result length and the turns it was carried over). In
tokens, little: the quote-check re-fetches of held pages carried about 1.1 M, the three checking agents' together about
1.5 M. The cost is in what the check can see. Of the 946 fetches, 572 were PDFs, read through a summary.

**The other held fetches** (observed 2026-10-10; method: each of the 26 fetches outside the checking agents, its
tool, its result and its URL). 10 were main sessions' `make source-pages` served from the page cache, so they never
reached the web; the count above overcounts them. 2 were a PDF and a full text read through `source-pages`, which the fix
below covers. 14 were ad-hoc agents' own `WebFetch` of pages the archive held (a Gutenberg text, Japanese Wikipedia, two
PDFs). Nothing had told those agents the archive existed: plan D6.

**Searches the record already answers** (observed 2026-10-10; method: as above): none of the agents' 207 searches, and
none of the main sessions' 20, matched a record question's heading by the 60% rule.

**The fix** (FR-006, plan D4 and D6). When the live page cannot be read (a PDF, a refused host), `CachedPages` reads the
archive's text of that URL before giving up. A quotation found VERBATIM there is reported VERBATIM, marked as read from
the archive. One not found there stays NOT-CHECKED for the agent, because PDF text extraction can split words and a miss
proves nothing. READABLE still needs the live link to have answered. Plan D6 adds a hook: an agent's first fetch of
a page the archive holds is refused with the archived text's path, and its second fetch passes. No gap here needs an
overhaul.

**Validation** (observed 2026-10-10; method: `make quote-verbatim` on questions 0059, 0235, 0009, 0080 and 0033, the
five whose notes cite the most PDFs, once at HEAD in a detached worktree and once with plan D4; the reports quote
the sources at length and are not committed - `make quote-verbatim Q=<n> OUT=<json>` at each commit remakes them).

| verdict before -> after (observed 2026-10-10; method: the ten reports) | passages |
|---|---|
| VERBATIM -> VERBATIM | 213 |
| NOT-CHECKED -> NOT-CHECKED | 153 |
| **NOT-CHECKED -> VERBATIM** (confirmed on the archive's text) | **39** |
| **UNFETCHABLE -> VERBATIM** | **2** |
| NOT-ON-PAGE -> NOT-ON-PAGE | 6 |
| NOT-CHECKED -> UNFETCHABLE | 4 |
| UNFETCHABLE -> UNFETCHABLE | 2 |

- **41 passages** that sent quote-check to the web are now settled by the script.
- **11 notes** went from `-` to READABLE. No verdict was sunk: no VERBATIM or READABLE was lost, and nothing new became
  NOT-ON-PAGE or NOT-READABLE.
- **The four NOT-CHECKED -> UNFETCHABLE** are one PDF of maff.go.jp in question 0009. The script used to mark a PDF
  NOT-CHECKED without asking. It now asks, the host answers 403 to an automated fetch, and the archive holds no text of
  it. The new verdict says what happened; quote-check takes either as residue.
