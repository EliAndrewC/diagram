# Editing, checking and reading for the record - the how-to

**Load this file when:** you edit a question or a registry entry, add a term, check a page, run a write session, read a source page for the record, or meet a blocked, banned or uncited source.

(moved VERBATIM from research/CLAUDE.md on 2026-10-17, feature 383 amendment 6, plan D44: the CLAUDE.md keeps one line per rule and an index)

**Editing.** Edit the file, then `make record` (and `make glossary` for a term) at the repository root;
`make record CHECK=1` builds in memory and names every refusal (a link that lands nowhere, an id used twice, a note
nothing cites, a question with no tags or tags no section takes). **A new question**: `make reserve KIND=question
KEY=<heading id>` gives it the next number and a stub; write its heading and FILL ITS TAGS from `research/tags.json` -
subjects (the first is primary and decides its section), settings, one level (foundational, subtype, detail, counts and
measurements); its home is the first section of `contents.json` whose rule takes those tags. Its drawing page is the
same stem's `.drawing.html` and states no tags (it inherits them); a second drawing page of one question is a stem of its
own saying `<!-- about: NNNN-<slug> -->`. **Renaming or renumbering one** - a retitled heading, a new number - is `make
fragment-move FROM=<file> TO=<file>`, which moves every file of the stem and rewrites every pointer to it. **Regrouping
the record** is an edit to `contents.json` alone; no question file moves. **A footnote**: no number anywhere - `<sup
class="fn" data-note="<key>"></sup>` in the prose, `<li data-note="<key>">...</li>` in that page's `.notes.html`; repeats
of one work are `key`, `key-2`, ... A reference resolves in its own page's notes only.
**A link** inside the record is written from `questions/`: another question as `NNNN-<slug>[.drawing].html[#id]`, an id
on the same page as `#id`, the registry as `../SOURCES.html#<key>`.
**A term**: a new file with a free prefix; the prefix order decides which term wins a shared variant. The
assembled `assets/glossary.json` is written by `make glossary`, and the site's `glossary.js` by `make record`; neither
is hand-edited.

**Checking** (feature 250). `make check-bundle Q=<NNNN>` (a question's number - both its pages - or one page's file
name; `KEY=<k>` for a registry entry; `KIND=<class>` for `entry-drift`; `NOTES=<key,key>` to re-check only those)
copies what ONE check reads out of the repository into one `MANIFEST.md`; dispatch the check naming that MANIFEST and
nothing under `/diagram`; four or more of one check go as one `check-wave` workflow, a unit per MANIFEST
([`docs/reviews.md`](../docs/reviews.md)). `make notes Q= KEYS=` prints a few notes and the paragraphs carrying them; `IN=<section or
tag>` runs a prepass over a whole section. A report's findings are applied in ONE turn - every turn re-reads the whole
context. Which checks a change owes: [`record-checks.md`](record-checks.md).

**Write sessions.** Over the cap (four questions, ten new registry keys) the runner names the split (`<g>a-write.md`,
`<g>b-write.md`); at the eleventh key, finish the question in hand, write the unreached items to `$L7R_CONTINUE` as a
brief of the same shape, commit and stop. Escapes, logged: `WRITE_CAP_OK='<reason>'`, `KEY_CAP_OK='<reason>'`.

**Every page read is on the sources-consulted ledger and the attempts log** (features 288, 312). `make source-pages
OUT=<dir> URL=<u> QUESTION=<NNNN, or none> SOUGHT="<what you look for>"` prints each page's earlier reads, its earlier
ATTEMPTS (`research/source-attempts.jsonl`: what each read sought and what came of it) and the filter's verdict on it -
BEFORE it fetches; it refuses a read with no `SOUGHT=`, and a page already judged `not-found` or `not-applicable` for the
same question unless `REREAD="<what changed>"` says why. It caches each page (`REFRESH=1` fetches a copy under seven days
old again). Record every outcome with `make source-outcome URL=<u> OUTCOME=cited:<key>|rejected:<why>|nothing-found|unreadable
[QUESTION=<NNNN>]` (`make reserve KIND=registry KEY=<k> URL=<u>` marks its source `cited:<k>` itself); `make attempts
URL=<u> | KEY=<k> | Q=<NNNN>` and `make sources-consulted URL=<u>` look a page up without fetching it. A WebFetch or a shell
fetch is recorded too, by `scripts/hooks/blocked-fetch-hooks.sh`, which shows its earlier attempts and says when the archive
already holds a copy. A URL cited any other way is archived with `make archive URL=<u>` ([`downloads.md`](downloads.md)).

**Blocked and banned sources** (feature 312, the GM 2026-10-02). A domain on `research/blocked-domains.json` (AI-generated
sites; Grokipedia the first) is refused at every fetch route and every store, and the build refuses a citation of one; a
pattern on `research/banned-citations.json` is refused at the citation only. Only the GM adds an entry, with the approval
recorded in it.

**The uncited sources** (feature 312). A page read and never cited is judged once by the `source-filter` (`make uncited
DO=...`): not kept, with its reasons, as a line of `research/not-kept.jsonl` - never archived; or kept, archived and written
up in `research/sources/040-uncited-works/` exactly as a cited work is (no `Used for:` line), checked by
`source-applicability`, and shown in the record's "Uncited sources". When a footnote first cites one, `make cite-uncited
KEY=<k>` moves it to the works cited; the build refuses a footnote citing it where it stands. A footnote citing a source no
one can wholly read (`paywalled`, `gm-partial`, `never-read`) stands only on a passage `quote-check` confirmed in the
readable part, recorded in `research/partial-confirmations.jsonl` - the push and `make quick` refuse it otherwise
(`scripts/gates/check-partial-citations.py`).

**A check round, as the tooling holds it (feature 375).** A pop-up owed only because a page it names moved is TRIAGED first
(`make modal-triage`, one ad-hoc opus agent, `make modal-triaged`), as claims are (`make claims-triage`). While a check on a
page or pop-up runs, the page is frozen; when the round returns, its EDIT blocks go in (`make apply-edits`) and nothing
else until the checks are answered. Record each answer with `make record-checked ... REPLY=<the reply>`: a finding on a block
the change did not write - the check lists it under `OUTSIDE THE CHANGE` - is filed as an open row of the feature, not fixed in
this change. A check's third round on one page goes to the `round-arbiter`, not the GM; `make check-closed` closes a check
that went silent.
