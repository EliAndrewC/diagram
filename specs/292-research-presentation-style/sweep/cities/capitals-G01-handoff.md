# 292 sweep cities/capitals G01 - handoff (session 1: write)

## Domain capitals: the daimyo's castle town (jokamachi)

- SECTION=cities/capitals/domain-capitals-the-daimyos-castle-town-jokamachi
- RENDERING=rendering/cities/capitals/how-our-maps-size-and-lay-out-a-domain-capital
- OLD=research/cities/capitals/010-at-the-capital-tier-japan-leads-and-china-is-the-tiebreaker.html research/cities/capitals/050-our-capital-is-a-hikone-scale-market-town-carrying-a-quarter-of-hikones-samurai.html research/cities/capitals/380-does-a-scorpion-capital-look-different-from-a-crane-one.html research/cities/capitals/220-dimensional-audit-of-the-drawn-capital.html
- MODALS=
- BASE=6f7daef70

All four sections were folded; no claim held them (269 X1B's 380 claim is marked done). This is the first rendering page for a
`cities/` page, and the record could not hold a rendering page two directories down, so the tooling learned it: `sources.COLLECTIONS`
and `scripts/_hm_record.py` gain `rendering/cities`, `record/xref.py` finds fragments in `rendering/cities/<page>/`, the modal
`Entry:` pattern accepts two levels, a test in `test_xref.py` covers it, and the page count in `test_citations.py` is 23. Later
cities groups reuse `research/rendering/cities/capitals.html` and its scaffold, and a new `rendering/cities/<page>` needs its
`_front`/`_tail`/`_citations-*` fragments, an empty `rendering/cities/<page>.html` and `citations/rendering/cities/` to exist
before the first `make record`. Note keys: on the research page the old keys `jokamachi-jawiki-6`/`-7` are kept (`-2`/`-3` are
taken by other capitals sections), and the new canon note is `l7r-budgets-5`, quoting the budget notes' by-size table row
(~12,400 inhabitants, ~13%, ~1,560 samurai). Cut or moved: 050's "a quarter of Hikone's samurai" is now given as the share it
meant, and its quoted canon phrases ("deliberately restrained echo", "are far more commercial") are gone because the canon
lookup cuts the line before them, so they could not be quoted verbatim. The canon's figures carry the comparison. The audit's
unsourced first-Meirinkan figure and its unfootnoted ~5 ha are replaced by a link to the school-ground section (460). The
aqueduct row's figures from search summaries are moved into the absence note's comment, and the 10 ft cut is now labeled a
GUESS, unverified. The Nisshinkan's area is given as ~2.4 ha from its 120 by 60 ken, not the audit's 2.65. The one inbound
link (capitals 410) is re-aimed. `make quick` stopped on three `tests/hamletgen/test_pool_261.py` failures (map rolls,
mizuguchi and others), which this change does not reach. Its formatter also rewrote three files this session never edited,
and those rewrites were reverted.
