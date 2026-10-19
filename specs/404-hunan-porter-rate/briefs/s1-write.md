# Brief - feature 404, the Hunan edition's porter and boat rates. Session 1: write (0260)

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** 0260 "What did hiring a horse or a porter cost?" has Zhili cart rates but no Qing porter rate: the
Bochum transcription of the Zhili edition labels its porter, pack-animal and boat figures per li and per 100 li
inconsistently, and no public scan of the Zhili original exists. The public Hunan edition of the same 1769 compilation
states the unit in each row. The lead is `specs/404-hunan-porter-rate/passes/zhili-ch13.md` (a lead, not a citation:
read each row on its page image). Research only: edit no code, modal, sheet or canon. Change only the 0260 sections this
touches.

## Your item

- **The Hunan rows.** Wikimedia Commons, `https://commons.wikimedia.org/wiki/File:SSID-11354707_欽定物料價值則例_第1卷.pdf`
  (public domain; no text layer): download it, render PDF pp. 38-39 (`pdftoppm`), and read on the images the 長沙/善化
  運價 rows - 「夫運捌拾斤每里銀叁釐」 (porter, 80 jin, per li, 0.003 tael), 「船運壹百斤每拾里銀貳釐」 (boat, 100 jin, per
  10 li, 0.002 tael) - and the note under them. Quote them verbatim with translations. ATTESTED ONLY FOR official
  building-work reimbursement in Hunan; date them as the edition states (Qianlong; 1769 only if read on its pages).
- **Wages beside them.** Render the same volume's pages for 長沙/善化 and look for the craftsman's (匠) and laborer's (夫)
  day wage rows. If found, quote them and set the porter's rate beside them: a porter's 100 li in laborer-days is the
  project's arithmetic. If not, the wage is SILENT, with the pages searched named, and the nearest named with its class,
  place, unit and gap in years (0260 and 0275 already hold the Zhili 1769 wages).
- **The Zhili rows stay out.** Rewrite 0260's absence note on them: no public scan of the Zhili original was found
  (Tsinghua's copy is the one cited; searched in NLC, Internet Archive, Commons and the National Archives of Japan); quote
  the Bochum chapter 13 rows the claim rests on (the spreadsheet `wuliao_jiazhi_zeli_zhili_13.xls`, see the pass) - at
  least 青縣 28b (車運, 船運 labeled 里) against 29a (夫運, 馬騾驢馱運 labeled 百里), the same figures; the Hunan original
  writes its unit row by row (per li for the porter, per 10 li for the boat), so a single unit column cannot be assumed.
  Choose no unit for Zhili.
- **The pack animal** stays without an official rate: Hunan 卷一's 長沙/善化 運價 rows are two items only (以上貳欵), and
  Zhili's are left out; say so.
- **Retry** Moll-Murata, Song and Vogel (eds.), *Chinese Handicraft Regulations of the Qing Dynasty* (2005, Google Books)
  and the HathiTrust search for 物料價值則例, which failed on 2026-10-19 (quota; Cloudflare challenge). Read, use what they
  give (they settle Zhili's unit only if they reproduce the original's rows); still failing, name them with the failure
  and both dates. Name the leads still open: the Jiangsu edition (National Archives of Japan, 内閣文庫), the Hunan scans
  卷2-8 (SSID-11354708 to -10).

New registry key: the Hunan edition (one key, the Commons file URL). Keep 0260 under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`; archive the Commons PDF (`make archive-find`, then archive it as the record's rules say). Then
   `make research-claim Q="0260" FEATURE=404`.
2. `make source-pages` for the page read, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1
   IMAGES=<the rendered pages>`). The new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its
   two write-ups.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `404: `.
4. Write `specs/404-hunan-porter-rate/implementation-check.md`:
   `- 0260: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/404-hunan-porter-rate/briefs/s1-handoff.md`: `- SECTION=0260/<id>`; each changed figure or verdict, old
   and new; the new registry key.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
