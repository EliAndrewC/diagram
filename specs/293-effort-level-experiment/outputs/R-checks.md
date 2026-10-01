# 293 task R - checks report (session 2: check and apply, 2026-09-30)

Commit `8e8d70f79` in this clone. Re-check: one quote-check on the four moved notes. Record tests (record, footnotes, record-format, sources, citations): 304 passed. `_entry_owed.py`: nothing owed (no modal's `Entry:` names 910).

- SECTION=buildings/910 | quote-check 13 VERBATIM, 11 SUPPORTS, 2 PARTIAL (kochi-hantei-jstage: the fourteen Osaka rooms lie in both residences and only rooms 9-14 have two earth floors - note rebuilt from p. 48, prose rewritten; nagayamon-jawiki-91: "rooms such as", "in the parts on either side"), 2 TRANSLATION-DIFFERS fixed, chugen lead overstated -> narrowed; re-check 4 SUPPORTS, 0 PARTIAL, one more translation restored and the lead narrowed again | record-format 5 VOCABULARY, 0 SESSION NOTE, 0 HISTORY (glossary: batten ceiling, ridge tag, south range; "six tatami mats"; "rope men" framed by the source's "retainers of very low status") | outcome unchanged: KNOB (a door to each dwelling, or a common room); the common-room form's door evidence is now stated as one page naming only one entrance
- KEY=shinke-nagayamon-kanazawa | source-applicability APPLICABLE-WITH-LIMITS; What it is INACCURATE (新家 reads Araie, not Shinke; the house is gone, the gate range stands), limits MISSING (who lived in the room) - all fixed; prose now "the Araie residence"
- KEY=kochi-hantei-jstage | source-applicability APPLICABLE-WITH-LIMITS; limits MISSING (official quarters for posted staff, not family households; no kitchens at Osaka) - fixed; one Fushimi gatekeeper's dwelling has no earth floor (Table 5, read twice from a coarse scan) - write-up and Used for corrected
- KEY=hoppou-shibata-ashigaru | source-applicability APPLICABLE-WITH-LIMITS; What it is INACCURATE (the row stands across the Shibata River from the garden, one of four domain rows), limits MISSING (a visitor page naming no source) - fixed
- KEY=qianggen-siheyuan-layout | source-applicability APPLICABLE-WITH-LIMITS, limits HONEST - nothing to act on

## Left open

- GM question, default taken: the key `shinke-nagayamon-kanazawa` misreads 新家 (the page glosses あらいえ, Araie). Default: kept as an identifier (a rename touches the registry file, the ledger's `cited:` outcome and the derived pages), noted in the entry's READ comment; the visible prose and write-up say Araie.
- "rope men" (御綱方): what they did is on no page read; left as the source's term, not searched.
- The kochi notes' vertical punctuation (︑︒) is the text layer's and was checked against page images only; `quote-verbatim` cannot check a PDF.
- The `batten ceiling` glossary definition is the checker's own (trimmed to the term's meaning), not drawn from the record's text.
- Not cited, a pointer: Bunka Isan Online gives the Shibata row as 43.6 by 7.3 m (about 24 by 4 ken) against the page's 3.5 ken deep; no finding rests on the depth.
- 910 sits at 19,998 bytes after trimming its session comments; a further note would push it over. `urban-features/560` (20,273) is over the cap too - not this brief's.
