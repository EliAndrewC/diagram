# Research: how the re-sourcing passes are run (Phase 0)

**Nature of this file**: the method and the source pools, not historical findings. The findings
themselves land in `.claude/skills/diagram/research/` where the rules point; this feature adds no
finding that lives only here.

## R1. What counts as uncited, measured

Scan 2026-08-28 (`## ` entries with a `**Sources:**` line, research tree only):

| file | not recorded | cited |
|---|---|---|
| archetypes.md | 9 | 4 |
| buildings.md | 9 | 14 |
| cities/capitals.md | 20 | 14 |
| cities/defenses.md | 2 | 1 |
| cities/fabric.md | 2 | 0 |
| cities/government.md | 1 | 1 |
| cities/hinterland.md | 1 | 0 |
| cities/river-cities.md | 2 | 0 |
| fields.md | 6 | 3 |
| homesteads.md | 9 | 2 |
| religion-and-death.md | 5 | 2 |
| towns.md | 5 | 0 |
| urban-features.md | 15 | 2 |
| vegetation.md | 8 | 1 |
| water.md | 9 | 9 |
| **total** | **94** | **53** |

A loose grep on `buildings.md` counts 23 "not recorded" lines against the entry parser's 9 - the
file's entries do not all sit under `## ` headings the parser splits on. The batch task re-counts
on entry and records the true figure in the ledger; either way every entry is worked. The
README's own sentence "72 of the 83 entries currently say exactly that" is stale; the batch that
touches README updates it to the final count (zero).

## R2. Source pools by subject (where the passes look first)

- **Japanese rural settlement, farmsteads, fields, water**: JStage (地理学評論, 東北地理, 農業土木学会誌,
  日本建築学会計画系論文集), CiNii, MAFF/MLIT pages, prefectural tameike and irrigation pages (Kagawa,
  Saitama already keyed), the Nihon Minka-en and open-air museum plans (Shirakawa, Hida no Sato),
  ja.wikipedia's references.
- **Chinese agriculture, polders, dike-ponds**: 农政全书 / 王祯农书 via ctext.org, FAO reports (the
  dike-pond FAO/Ruddle & Zhong 1988 monograph), Elvin, Bray *Science and Civilisation in China*
  vol. 6.2 (Agriculture) - SUMMARY-ONLY where paywalled, abstract pages read.
- **Yamen / jin'ya / magistracy (Mode A)**: Takayama Jin'ya official site and plans; 上下代官所
  excavation report (Hiroshima); the Neiqiu/Pingyao yamen museum pages; Ch'ü T'ung-tsu *Local
  Government in China under the Ch'ing*; Botsman *Punishment and Power in the Making of Modern
  Japan* (Tenmachō jail); Edo *machi-bugyōsho* plans (Tokyo Metropolitan Archives).
- **Castle towns, capitals, walls, towers**: jokamachi surveys already keyed; Hikone, Okayama,
  Kitsuki city sites; Pingyao / Xi'an wall documentation; Shen Kuo *Mengxi Bitan* via ctext;
  Needham vol. 5.6 (military technology, walls) SUMMARY-ONLY if needed; Coaldrake *Architecture
  and Authority in Japan*.
- **Fire towers, bell-and-drum, urban institutions**: Edo fire-watch (hinomi-yagura) museum pages
  (Edo-Tokyo Museum, Fukagawa); Beijing Drum Tower documentation; Song *Dongjing Meng Hua Lu*
  via ctext.
- **Religion and death**: the temple-belt literature; Botsman; execution-ground anchors
  (Suzugamori, Kozukappara) municipal pages; Chinese *yizhong* charity graveyards.
- **Vegetation**: satoyama literature (Takeuchi et al. 2003), FAO windbreak manuals, the bamboo
  and mulberry entries already keyed.

## R3. The contradiction protocol

A `source-reader` CONTRADICTED verdict is not by itself a contradiction of the FINDING - it says
that ONE page says otherwise. The session then: (a) reads the quote against the entry's scope;
(b) looks for a second source; (c) classifies as **supplement** (the finding was right but
over-broad - scope added) or **contradiction** (the rule rests on what the sources deny). Only (c)
goes to ledger section E and the GM report, with: entry, what the record said, what the sources
say (quotes), the `Grounds:` rule and checks, the maps that draw it, and the two options.

## R4. The gate test (FR-010)

`tests/test_research_sources.py`: walks `research/**/*.md` except README/SOURCES, requires every
`## ` entry to carry a `**Sources:**` line that is not `not recorded` and whose backticked keys
all appear as `### \`key\`` headings in `SOURCES.md`; a `setting-canon` pointer (`l7r.md`,
`budgets.md`) and an explicit `searched: ... not found` are accepted forms. Data-file test:
gate scope, re-runs under testmon on its own change. Fire-proof: an inline fixture string with a
stripped line returns a violation. It is added to the gate only in the last batch, once the
count is zero - before that it would turn the gate red on every push (its function is tested
from the first batch; the gate assertion is enabled last).

## R5. Why batches are files, not entries

One dispatch of `source-reader` per file keeps the reading in the background with one
notification; one commit per file is a reviewable unit; a file is the unit the operative doc
links to. capitals.md (20 rows) is split in two dispatches but stays one task.
