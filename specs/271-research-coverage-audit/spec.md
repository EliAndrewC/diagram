# Feature 271 - an audit of open research questions, and the backfill

**Status:** Draft, 2026-09-27. The GM's words are `request.md`.

## What this feature is

An audit of every open research question the maps raise, and as much backfill of those questions as one long
unattended session can do. It covers the maps already made, the hand-drawn ones included, and the settlement tiers
not yet scripted (village, town, city, capital). The GM expects the existing research to be spotty. Some of it
predates the current conventions: a quoted passage behind every claim, and checks by subagents. The work is shared
with the "Diagram supplemental" session (feature 269) and the other research sessions (267, 268), and must not
duplicate theirs.

## Requirements

**FR-001 - the audit.** An inventory of the research the maps need, one row per question. Rows come from four
places:
- (a) every KIND of thing drawn on any map already made: the scripted pool, the legacy hand-drawn pool, the
  building-plan magistracies and `wip/`;
- (b) every modal whose `Entry:` names no research question, or names one that says nothing about the thing;
- (c) every research question whose findings are thin: no quoted, footnoted evidence, or written before the
  citation conventions;
- (d) the questions a map of a tier not yet scripted will need, for example how much larger the village headman's
  house is than the others, the real size of a country shrine where a country monk lives, and in towns and cities
  the inns, dojos, governor's mansions, smiths, tanneries and gate markets.

Each row carries:
- the thing and the question;
- the tier or tiers it serves;
- its status now: NONE, THIN or COVERED;
- its owner: this feature, another session's feature, or nobody yet.

The inventory is `specs/271-research-coverage-audit/inventory.md`.

**FR-002 - no duplicated work.** Before any row is researched, it is checked against
`/diagram/.clones/RESEARCH-CLAIMS.md` and the other sessions' inventories. A row another session owns is left to it.
This feature's claim is added there before the work starts. The "Diagram supplemental" session is told what this
feature takes.

**FR-003 - the backfill.** The rows this feature owns are researched and written into the record by the landed
research process: page briefs, sessions in parallel queues, reserved prefixes, check bundles, `quote-check`,
`record-format` and `source-applicability`, one re-check round, and every owed modal answered. They are worked in
this order:
1. things already drawn on a map;
2. then the next tier to be scripted (the village);
3. then towns;
4. then cities and capitals.

A claim whose only evidence cannot be read is labeled as the record's guess or estimate, with an absence note. It
is never left bare.

**FR-004 - the download list.** Every source found that a person can likely get but a bot cannot fetch is added at
the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, in the GM's format, with both links.

**FR-005 - it survives the context running out.** The inventory records each row's state as the work goes. Each
batch is committed as it finishes. A memory note says where the work stands. A session that restarts after its
context is compacted picks up at the first row not yet done.

## Success criteria

- **SC-001** (FR-001) - `inventory.md` lists every kind drawn on every map in the four sources, and a set of
  next-tier questions for village, town, city and capital, each row with a status and an owner.
- **SC-002** (FR-002) - no row this feature researched is claimed by another session in `RESEARCH-CLAIMS.md`.
- **SC-003** (FR-003) - every row this feature researched is COVERED with quoted, checked evidence, or labeled with
  an absence note. The record checks (`make page-check`, `make done`) are green at the push.
- **SC-004** (FR-004) - the download list grows only at its end, both links on each entry.
- **SC-005** (FR-005) - the inventory's state column and the commit history show where a restarted session
  resumes.

## Decisions Recorded

- The backfill is sized by the time the GM gave (about six hours unattended), not by the inventory. Rows left
  undone stay in the inventory, marked with their status and owner, for the next session.
