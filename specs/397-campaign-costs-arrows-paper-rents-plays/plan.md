# Implementation Plan: campaign costs II - arrows, notice boards and paper, rents, plays (feature 397)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature written from the four search passes in `passes/`:
- four new money questions;
- one new comparative question (the English traveling players);
- an extension of 0190, the notice board.

That is more than one write session's cap, so the record is written in two write sessions and then one check-and-apply
session. Then the answer goes on EliAndrewC/diagram#4. The two books the comment on #4 asked for (Takeyasu 1966 and
Uemura 1987) are already on `research/to-download.md` as entries 312 and 313, each naming 0251. No code, map or canon
changes.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-write.md briefs/s1-check.md"`. The passes are
  leads: each passage is read on its page before it is cited. The rendered page images the passes used are named in the
  passes; a scanned page goes into a source-reader bundle with `IMAGES=`.
- **The wages.** Each figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and period
  where a source gives them. Where none does, the question says that wage is SILENT and names the nearest wage, with its
  class (unskilled or craftsman), its place, its unit and its gap in years. A craftsman's wage is always named as a
  craftsman's and is never shown as the unskilled wage. Wages in hand:
  - Kyoto 1802-04, unskilled and craftsman (0250);
  - Edo carpenter, 1804-60 (0256);
  - Qing Beijing and Jiangsu, 1769-95, construction wages (`allen-2009-china-wages`, already registered);
  - Beijing 1736, the official price-and-wage list (Gao Shouxian; registered by 396 if its cloth question cites it first,
    else by this feature).
- **The units.** Mon and silver are not converted, because no copper-to-silver rate is written here (the same rule as
  396). Qing cash and taels are not converted either.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the four money questions (FR-001)

Each is new and tagged `subject=money`, with no drawing page. Its level is `counts-and-measurements`.

| question | setting tag | what it covers |
|---|---|---|
| "What did arrows cost?" | `countryside,city` | the Ming and Qing prices per arrow, ordinary and fine; Japan SILENT; fletcher output SILENT; arrowheads SILENT, with Kawato's guess labeled; recovery NOT ATTESTED, with the Qing write-off |
| "What did paper and ink cost?" | `city` | Qing Beijing 1736 paper by grade per sheet beside its wage; the ink stick SILENT, with ink per jin as the nearest; Edo paper and ink SILENT (the two web figures disagree and neither is citable) |
| "What did it cost to rent a room or a house?" | `city` | the Edo back-tenement rent (one carpenter's 10 monme a month); the Qing government-house and shop-front rents; Li Ciming's house; the rent-to-value ratios (Edo lot with houses, Qing administrative prices); the Japanese silences (shop, small house, samurai residence, storehouse, castle towns, weekly) |
| "What did a play or a show cost to see?" | `city,countryside` | Edo kabuki seats 1803 and the 16-mon single act; kanjin-no; temple-fair shows SILENT; rural troupe hire; donations; troupe composition; Qing seats and the street act |

Each question answers its acceptance scenario: every attested figure, every silence, and each figure beside its wages.
A figure the project computes is labeled as the project's arithmetic.

## D2 - the comparative question (FR-002)

"Did English traveling players gather their money at the door or pass a hat?" It is tagged `subject=comparative,money`,
`setting=city`, with no drawing page, and sits in the `comparative-money` section. Its sources are registered with
`kind=comparative`, and it opens with the category's intro: a yardstick from another society for players, never
Rokugan's own figures. It covers:
- gathering at the door, ATTESTED ONLY FOR that: the 1583 inn-yard depositions and Platter 1599;
- passing a hat mid-play, NOT ATTESTED by a period source; Lawrence 1912 is a modern inference, labeled as one;
- no English wage, SILENT.

## D3 - extending 0190 (FR-001)

0190's research page gains what an Edo notice was made of and who could post on it, ATTESTED ONLY FOR Edo:
- official notices were wooden plaques written in ink;
- pasted paper went only on structures the magistrate permitted;
- the village case is SILENT.

What was posted is already on 0190, and the answer points to it. The drawing page is unchanged.

## D4 - the implementation check (FR-004)

`implementation-check.md` holds one line per new question ("no code implements it - consumed by gm-assistant's money
skill", with the search). It also holds 0190's line: the change checked against the code that draws the notice board. The
added facts (material, who could post) decide nothing that code draws, which the line states with its grep of the board's
code.

## D5 - the answer and the download list (FR-005)

A comment on EliAndrewC/diagram#4 gives:
- each question's fragment FILE, 0190's included;
- the checked verdict for every figure;
- what is still open, per question;
- download entries 312 and 313, the two books.

## T - the order

1. The page sessions: write 1, write 2, check.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
