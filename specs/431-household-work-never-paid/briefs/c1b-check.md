<!-- page-load: kind=check -->
# Brief - feature 431, session C1b: what C1 left owed on 0312 and 0313

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-money-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session S1 wrote 0312 (the farm household's unpaid work), 0313 (how long it took to make cloth) and 0314 (modern
hand weaving, comparative); session C1 checked them. Its report is `specs/431-household-work-never-paid/briefs/c1-checks.md`
(read it with `make lines`); its last line, `STILL OWED:`, is your work. Since then the record-format rounds on 0312-0314 and the
Pomeranz source-reader round were answered, and "Shen-shi nongshu" was respelled "Shen shi nongshu" (its glossary term), which
re-owes quote-check on the notes it touched.

**Not yours:** any unit outside 0312, 0313, 0314 and their registry keys. 0312's pointer to the question on why women's household
work was rarely recorded is NOT yours (that question is written in another clone; it is added later). 0312's prose is at 19,972
bytes against the 20,000 cap: a footnote marker costs bytes, so trim words elsewhere in the same section if you need room, never
cut a finding.

## The procedure

1. Each unfootnoted assertion C1 named - in 0312: Kanazawa (the Tomioku village), Buck 1921-1925, Fei 1936, Huzhou about 1640
   (the Shen shi nongshu's date and place), 1658 (the Bu nongshu), the rainy silkworm month, and the Sukumo line-40 passage on
   women's work at home; in 0313: the Tiangong kaiwu's 1637 and "reeled from fewer cocoons", the Bu nongshu's 1658 and the Ming
   date of Shen's manual, Nagashima's endnote 3 for Nagahara - gets a footnote to a passage that states it (a passage already
   cited, or a new one read on its page, translated with its original stored), or the words are cut or reworded to what the cited
   passages say. Then 0313's PARTIALs: make each claim say no more than its passage.
2. `make record-owed` names what this owes. In the background, in one message, dispatch one agent per owed unit of yours, each from
   its own bundle (quote-check after `make quote-verbatim Q=<n>`, `make check-bundle Q=<n> FOR=quote-check`; source-reader, record-format,
   translation-check as owed). A check's third round on one subject goes to the round arbiter first (`make arbiter-bundle
   TRIGGER=...` - the trigger the guard names). Four or more of one check go as ONE `check-wave` workflow.
3. `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses. Then `make record && make citations` and the record
   tests, answer each check with `make record-checked`, write the ledger rows (`make ledger-owed WRITE=...`). Commit with
   messages opening `431: `. Do not push.
4. Append one line per check to `specs/431-household-work-never-paid/briefs/c1-checks.md` with `make append`, then a last line
   `STILL OWED (C1b):` naming anything left. Your last message is one paragraph.
