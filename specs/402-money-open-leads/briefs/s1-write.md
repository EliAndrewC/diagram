# Brief - feature 402, the money answers' open leads. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** Four existing money questions said SILENT where four later search passes found public sources. Write
the found figures into them, each from a passage read on its page, and keep SILENT what stayed silent. Each new figure
sits beside the craftsman's AND the unskilled laborer's day wage of the same place and period; where no source gives one,
say that wage is SILENT and name the nearest, with its class, its place, its unit and its gap in years. Label every figure
the project computes as the project's arithmetic. No price is converted between coins unless its source converts it or
0277's rates are applied and labeled. Research only: edit no code, modal, sheet or canon. Change only the sections the new
figures touch.

## The passes (leads, not citations)

`specs/402-money-open-leads/passes/`: `wage-1600s.md`, `edo-rates.md`, `edo-salt.md`, `sharpener-inui.md`. Each holds
verbatim passages, URLs and where they were read. Read each passage on its page before citing it. NDL scans are read on
their page images (render them; NDL's OCR is checked against the image), and the images go to source-reader with
`IMAGES=`. A PDF whose text layer is garbled (Oishi's table) is read on its rendered pages.

## Morisada, searched first

類聚近世風俗志 (守貞謾稿) is public in NDL's viewer: 上 is pid 991466 and 下 is pid 991467; a separate 1934 one-volume
edition is pid 1444386. NDL's IIIF and lab full-text routes refuse all of them. The viewer's full-text search (`POST
https://dl.ndl.go.jp/api/fulltext/search`, as `passes/sharpener-inui.md` used it) works for 991466 and 1444386 only; 991467
is read page by page in the viewer. Search it for: an Edo retail salt
price (塩), and an Edo carpenter's (大工 手間 / 作料) and day laborer's (日雇 / 日傭 / 手傳) wage. Read each hit on its page
image (a headless-browser screenshot of the viewer, as the sharpener pass did). Full-text search worked for 上 (991466)
and the 1934 edition (1444386); it refused 下 (991467), so search 下 page by page in the viewer (its contents pages first,
for the sections on salt, food and wages), or use 1444386 once its NDL record or contents show it holds the whole text.
What you find is cited as below; what you do not find after searching both volumes makes the verdict SILENT, with the
search named in the absence note. If 下 cannot be searched, the verdict names it as an unread lead, not SILENT.

## Your items (four questions revised)

- B1 **0276 "What did a kitchen knife cost?"**
  - The wage beside Mimasaka 1665 (now "SILENT; nearest 1741/1749"): Kyoto carpenter 1 monme 8 bu with rice allowance,
    1653 (Hirai 2007, 建築史学 49, note 9, from Myoshinji's account; the page has no 一日, so "a day's" is the record's
    reading, and say so); the 1656 bath account's carpenters and day laborers, a per-day rate from its table being the
    project's arithmetic (only if the table reads cleanly on the page; otherwise leave it out); Osaka day laborers, 1620-21
    (Kitano, TUAD bulletin 33, note 26) and 1628 (Kitano, R7 bulletin, Table 1). All in Keicho silver, the coin of 1665;
    state that from a source (ja.wikipedia 三貨制度 is archived) or leave it unsaid. A wage of Mimasaka or Okayama:
    SILENT. Revise the knife-in-days arithmetic to the nearest same-period wage, labeled.
  - The sharpener (now "a sharpener's fee SILENT"): Morisada's 磨師 entry (類聚近世風俗志 上, NDL pid 991466, koma 94;
    the pass's transcription is to be checked on the image) shows the trade sharpened kitchen knives and small knives, with
    no fee: the fee stays SILENT. Uwajima 1662's sword-polishing rate (愛媛県史 近世下, archived) is ATTESTED ONLY FOR
    swords; its 分 unread as to coin, so give it as the page gives it.
  - The Okayama wage: 『藩法集1 岡山藩』's 賃銀雑事 chapter, if a public scan exists (search NDL); read it for a day wage
    of the 1600s. If it cannot be read, the Mimasaka/Okayama verdict stays SILENT and its absence note names it unread.
  - Inui's papers (Takefu 1980, 大阪教育大学紀要; Sakai 1972, 歴史学研究 385): not publicly readable (repository abstract
    only; NDL in-library only), said so in the absence notes; Kawashima's one line on Inui stands.
- B4 **0275 "What did a skilled craftsman earn against a laborer?"**
  - An Edo pair (now SILENT): from the Morisada search above. A pair found there is written in with its verdict, the ratio
    the project's arithmetic; if none, the absence note names the search.
- B2 **0277 "What was copper coin worth in silver?"**
  - The Edo market rate (now SILENT): Oishi Shinzaburo's 第1表 (glim-re repository PDF, pp. 70-73), yearly low and high in
    mon per ryo from 1781 to the 5th month of 1842, from Mitsui's table "centred on Edo" (his method sentence, p. 70);
    that it is Edo's rate is the record's reading, said so. Give decade summaries (the range of the yearly lows and highs,
    or their means, as the project's arithmetic, with the method stated in the note) and a few years verbatim; check every
    figure you use on the page images. The source's 1842-1852 blank (the official 6,500 only) and the 1850s: SILENT.
  - The absence note names the sources of a market series past 1852: 新稿両替年代記関鍵 and 校註両替年代記 (NDL-restricted),
    新保 1978 (not online).
  - Revise the anchor rows (1802-04, 1842) to give Edo's figure beside Osaka's where the table has the year.
  - 読史備要 (NDL pid 1915733, pp. 769-771): the scattered gold-to-copper rows of 1784 and 1787 only if they read cleanly
    on the image; otherwise leave them out.
- B3 **0273 "What did salt cost?"**
  - Edo, Ako salt (now SILENT): the Edo brokers' (下り塩仲買) answer to the city magistrate, 寛政3年8月7日 (1791), in
    『諸問屋再興調』十之二 (NDL pid 2548694, koma 38): a bale of 3斗5升 nominal (3斗2升 or so by season), 9½ bales per
    ryo, now 9.2-9.3 down to 9. Cite only what reads clearly on the image (the 3斗2升 tag only if it does). Per sho is the project's arithmetic. A wage of
    Edo in 1791: SILENT unless the record holds one; name the nearest with its class, place, unit and gap.
  - The wholesalers' commission (koma 71: 3 monme a ryo from the shipper, 1 to the brokers) only if read on the image.
  - Edo retail by the sho, any Edo salt price of 1800-1850s: from the Morisada search above, or SILENT naming it.
    東京市史稿 (print only) and 廣山堯道 (print only) stay named as unread.

New registry keys: Hirai 2007, Kitano (two bulletins), Oishi, 諸問屋再興調 十之二 (pid 2548694), 類聚近世風俗志 上
(pid 991466), 愛媛県史 近世下 if not already registered, 読史備要 if used. Check `make archive-find` for each first.

Keep each question under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0273 0275 0276 0277" FEATURE=402`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `402: `.
4. Write `specs/402-money-open-leads/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/402-money-open-leads/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, each changed figure with its verdict, old and new;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
