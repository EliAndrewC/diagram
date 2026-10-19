# Implementation Plan: the earlier money answers' open leads, written in (feature 403)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: thirteen existing money questions gain the figures two search passes found (`passes/`), or
name in their absence notes the searches that found nothing. Four write page sessions (at most four questions each, the
page-session cap), one check-and-apply session, then a note on EliAndrewC/diagram#9. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-write.md briefs/s3-write.md briefs/s4-write.md
  briefs/s5-check.md"`. The passes are leads: each passage is read on its page before it is cited.
- **Morisada.** 類聚近世風俗志 上 (pid 991466) and 下 (pid 991467): NDL's full-text search with the viewer's full request
  body (mode CONTENT, size 10000, ftInterval 400) answers for both (402's finding), and each hit is read on a viewer
  screenshot; feature 402's `measure/ft.sh` and `shot.py` are reused.
- **高岡史料.** NDL pid 899935 by its IIIF frames (`https://dl.ndl.go.jp/api/iiif/899935/R0000NNN/full/full/0/default.jpg`);
  if NDL refuses them, the viewer; if both refuse, an unread lead, dated.
- **Bochum.** The chapter spreadsheets and the scanned original, for the per-li label.
- **The wages.** Each new figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and
  period where a source gives them; where none does, the question says that wage is SILENT and names the nearest, with its
  class, its place, its unit and its gap in years.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the questions, by write session (FR-001, FR-002)

| session | questions | what changes |
|---|---|---|
| s1 | 0259, 0262, 0264, 0265 | Morisada: inns; sake and soba (the koma 228 handbill transcribed or named); paper and ink SILENT with the search; rent's system and fees |
| s2 | 0250, 0260, 0261, 0266 | Gamble's Beijing series (0250, 0266, and 0265's wage line, which s2 edits after s1); the 1921 survey's gild wages where a craftsman's Beijing wage is needed; Zhili freight after the label is settled; 0261's sewing and used kimono SILENT with Morisada's search, the cotton series soybeans, Koyaizu NDL-only |
| s3 | 0256, 0257, 0268, 0269 | #6's absence notes name the search; Hasegawa 1987 and 「近江の石工たち」 retried; 湯浅隆, 御再建場所日記, KAKEN 19K15191 read if public or named |
| s4 | 0270 | 高岡史料's 関野神社 section and p. 590; Okamoto papers named; the mirror SILENT in Morisada |

How each listed lead is closed, and on what ground (`passes/other-leads.md`, checked 2026-10-19):

- **宿村大概帳 Tokaido tariffs** (s1, 0259; s2, 0260): closed as not publicly readable - the print edition (『近世交通史料集』
  vols 4-6, NDL pids 12064602, 12061440, 12065414) is NDL in-library only, and the Postal Museum's 2020 note says the
  manuscript is the only copy, with no digitized copy found; named in both questions' absence notes. The tariffs the
  record already cites (Yamamoto 1969, Tachibana) stand.
- **Mitsui Bunko's Osaka cotton series** (s2, 0261): nothing is written from it. The pass found that the Mitsui series
  that starts in 1757 is soybeans, not cotton (Bassino and Ma, archived), and that the books holding any cotton series
  (Mitsui 1952, login; 1989, NDL in-library; Miyamoto 1963, login) are not publicly readable: the cotton lead is closed on
  that ground, named in 0261's note. No soybean figure is written.
- **Koyaizu's 『近世賃金物価史史料』** (s2, 0261): closed as not publicly readable - NDL pid 14107062 is NDL in-library only;
  named in 0261's note, which cites it at second hand.
- **The Takaoka donor's records (岡本家文書)** (s4, 0270): read if a public copy is found (the session searches once more);
  the pass found none online, only the Yamagen page's quotation - then named as not found online, dated.

Nothing else in these pages changes.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per changed question.

## D3 - the note (FR-004)

A comment on EliAndrewC/diagram#9 naming the changed fragment FILES, each changed verdict, the closed leads and what is
still open.

## T - the order

1. The page sessions (s1-s4 write, s5 check).
2. The implementation check.
3. The note.
4. Report and land, by the direct route.
