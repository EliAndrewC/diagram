# Feature 229 - the closing report to the GM

*Draft, assembled as the verification passes land. The three things the GM is owed at the end are
below: the README correction they must apply or decline themselves, the Mode A question, and every
claim this feature left labeled a guess.*

## 1. The README correction, offered and NOT applied

A README is the GM's to write (constitution XVII, NON-NEGOTIABLE). `research/README.md` is now
factually wrong in three places - it calls the deleted `settlements/` rule files "operational" and
tables fifteen of them - and the replacement text is written out in
[`readme-correction-offered.md`](readme-correction-offered.md) for the GM to paste or reject.
`tests/interactive/test_record.py` exempts that one file from the retired-file rule until they do.

## 2. The Mode A question

`buildings.md` is untouched and still operative: the GM's request named the settlement rule files, and
Mode A compound plans are placed by a PERSON rather than by a generator, so the argument that retired
the settlement files - the generator holds the rule now, the record holds the reasoning - does not
carry across on its own. A human drawing a compound needs an operative document to draw from.

What is worth the GM's eye is that `buildings.md` carries four of their own rulings as RULES, and the
research page carries at most the reasoning behind three of them:

| ruling | in `buildings.md` | on `research/buildings.html` |
|---|---|---|
| the 2x point-glyph doctrine retired, everything with a real footprint draws at true size (2026-07-21) | the rule | mentioned |
| structures ABUT a wall, they never stand in it (2026-07-24) | the rule, with its check | the subject is discussed |
| a tub stands OUTSIDE the building and clear of it, tightened from "center outside" to "no overlap at all" (2026-07-25, 2026-07-26) | the rule, with its check | the subject is discussed |
| the threshold stone is a PAIR flanking the road outside the opening, never in the passage (2026-07-25) | the rule, with the two defects that forced it | absent entirely |

So the question is narrow: does Mode A follow the settlement tiers - the rulings and their
specifications onto `research/buildings.html`, `buildings.md` left as the vocabulary a session draws
from - or does a mode a person draws by hand keep one operative document on purpose? This feature did
not decide it, because the GM did not ask about Mode A.

## 3. What the record still does not know

Two numbers are worth naming, because they are different things and the second is the larger one.

**Claims labeled a GUESS: 113 mentions across 18 pages**, and the migration added two of them, both on
the new `ways.html`:

- **How far past the bank a bridge lands.** The reasoning is sound - scour undercuts the bank, the
  footing must sit back from it, the seat needs timber to bear on - but no page a reader can open gives
  either figure for a bridge this size. The band reasoned to is 5 to 15 real feet of deck a side; the
  maps draw 10 ft, the middle of it.
- **The trunk highway's width.** About 9 m, narrowing to 4 to 7 m in the mountains and to 2 ken at the
  Hakone barrier. The figures are widely repeated and no page carrying them could be read.

**Claims with no readable source at all: 108.** This is the bigger number and it is the honest finding
of the whole migration. The rule files named their sources in prose, with no quotation and usually no
link; holding each to the record's contract - quote a passage and link a page where it can be read, or
say plainly that neither was found - turned 108 of the 176 new footnotes into ABSENCE notes. Well over
half of what the rule files asserted about how a place was built rests on nothing a reader can open.

Nothing was deleted for it. The maps draw these features and the record still asserts them; what
changed is that each sentence now says what stands behind it, and each registry entry records what was
searched and when. The per-page census is `research.md` R4.

One source was judged NOT applicable to the use it was put to, and the page was rewritten: two modern
cattle-housing standards agreeing with each other is not independent corroboration of a premodern byre,
because both say what a keeper ought to provide and both may be generous for the same reason.

## 4. What the feature did

- **Nineteen rule files deleted** - `settlements.md`, eleven topic files and six city files.
- **Four research pages created** - `settlements.html`, `ways.html`, `presentation.html` and
  `cities/sizing.html` - and thirteen rewritten.
- **The specification moved onto the page** for every tier no generator draws yet, marked
  `class="spec"` and written in real feet, so it moves into the generator when one is written.
- **Every pointer re-aimed**: 60 engine files, plus docs, agent files, pool and legacy notes, `wip/`
  and test docstrings. A gate rule now fails on any reference to a retired file, by path or by bare
  basename, judged per reference.
- **176 footnotes written** (108 absence notes), **26 sources registered and judged**, **32 glossary
  terms added**.
- **Six defects fixed in passing** (`research.md` R10), the two that matter being a gate that could roll
  the same map twice on a cold cache, and a cited stall measurement that had taken its two numbers from
  two different columns of one table row.
