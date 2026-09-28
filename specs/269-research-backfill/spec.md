# Feature Specification: The research backfill

**Feature Branch**: `269-research-backfill` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: FAITHFUL at round 2; implementing

**Input**: the GM's request, verbatim in [`request.md`](request.md): backfill *"all of the research questions that we
either had not done in the past at all, or ones that we did but have identified as being spotty, or ones that ... are
poorly sourced ... even if they have not come up on any of our scripted maps yet"*, run overnight, resuming by itself
when the five-hour window resets, without duplicating the other research sessions, and checking that they resume too.

## What is owed

[`inventory.md`](inventory.md) numbers every item, B01-B46. They come from an audit on 2026-09-27 of the future-work
files, every research fragment's footnotes against its assertions, and the engine's kinds labeled guess or with no
entry. The items fall into 20 research groups, one record page each. Every item another session owns (features 265,
267 and 268, each confirmed by its session) is listed under "Owned elsewhere" and excluded, and every footnote-less
section the audit passed over is listed with its reason.

**A correction to the request's premise.** The GM believed the Diagram research session was backfilling the
farming-settlement questions. That session confirmed (2026-09-27) that it works only feature 265's record checks on the
town and city pages, which is also where its queues ran. The farming-page research (fields, homesteads, water,
vegetation, archetypes) was unowned, and this feature takes it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A guess on a hamlet becomes a cited finding or a dated search (Priority: P1)

The GM clicks the privy on Inashiro's page. Before, the modal said its seat was a guess. After, "See references" lists
the question the record now asks about where a farmstead's privy stood, and the modal says what the research found:
accurate with a footnote, a knob with each form cited, or a guess with the search behind it.

**Independent Test**: every inventory item has its outcome in [`outcomes.md`](outcomes.md); every kind an item bears
on has an `Entry:` that resolves, or a guess note naming the search and its date.

**Acceptance Scenarios**:

1. **Given** an item the research answers decisively, **When** the feature lands, **Then** the record carries it cited,
   the kinds it bears on follow it, and where it contradicts what a map draws, the generator follows the finding and the
   motivating map is regenerated (constitution XII; the GM, 2026-09-12: research-driven map changes need no ask).
2. **Given** an item the research shows done more than one way, **When** the feature lands, **Then** it is a KNOB with
   per-settlement variance rolled from the seed, never a choice.
3. **Given** a thin section (few footnotes against its claims), **When** the feature lands, **Then** each real-world
   assertion is cited, carries an absence note, or is labeled a guess.

### User Story 2 - The work runs overnight and survives the usage limit (Priority: P1)

The GM leaves the laptop running. The research runs as a detached queue of fresh headless sessions
(`make page-session`). When the five-hour window runs out, the failed session waits for the reset and resumes itself
rather than being skipped. The orchestrating session wakes on an hourly schedule, restarts a stopped queue, and nudges
any peer research session that sits idle with claimed work unfinished.

**Independent Test**: the queue's run log shows a failed session followed by `resuming`, never by the next brief.

### User Story 3 - No two sessions research the same question (Priority: P1)

Before research starts, each peer session names its scope, and the scopes are written in
`/diagram/.clones/RESEARCH-CLAIMS.md` (outside every repository) and in the inventory. No group edits a section another
feature owns.

**Independent Test**: no fragment this feature changes is on 265's derived list, in 267's reserved ranges, or among
268's sections.

## Edge Cases

- **265's unpushed sweeps** have edited fragments on this feature's pages. The groups that edit existing fragments
  run after the new-question groups, and the queue syncs from main between sessions. A conflict stops the sync and the
  queue carries on, but no group that edits an existing fragment starts until the clone has 265's landing.
- **A finding owes a correction to another feature's section**: the handoff names it, and the owning session is sent
  the correction. This feature does not make it.
- **A finding would need a placer change larger than one feature**: the finding lands in the record and the kinds.
  The engine change is recorded in `future-work/` with the measurement, the mechanism and a sketch (constitution XIV,
  the one deferrable fix). It is not dropped.
- **A source only the GM can fetch**: it goes at the end of `TO-DOWNLOAD.md` in their format, and the claim stands with
  an absence note.
- **B33 and B34 are open GM decisions**: the research supports the decision, and the ruling stays the GM's.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every inventory item MUST be researched and end in one of four outcomes: ACCURATE (cited), KNOB (two or
  more attested forms, each cited), SILENT (an absence note with the search and its date), or CONTRADICTION-RESOLVED
  (the record corrected, cited). A contradiction the research cannot resolve goes to the GM.
- **FR-002**: The finding MUST live in the research record as a question a reader would ask from the map: a new
  fragment in the group's range, or a change to the existing section that makes the claim. It MUST be cited by the
  record's rules (quote, readable public page, translation marked).
- **FR-003**: Each kind an item bears on MUST follow its outcome: `Entry:`, label class and prose. `entry-drift` reads
  each changed kind against its section on a bundle.
- **FR-004**: Where an outcome changes what a map draws, the generator MUST follow it (a KNOB rolled per settlement),
  and the motivating map is regenerated. The exception is the Edge Cases' overhaul case.
- **FR-005**: The work MUST follow the procedure on main (feature 250): page sessions from briefs, checks on bundles,
  `make apply-edits`, `make canon`, the 20,000-byte cap, and registry and glossary prefixes reserved under the
  host-wide lock (`reserve-prefix.py`, feature 265 FR-010).
- **FR-006**: No section owned by 265, 267 or 268 (inventory, "Owned elsewhere") MAY be edited by this feature.
- **FR-007**: The research MUST run unattended through usage-limit resets: a session the limit ends is resumed after
  the reset, not skipped, and the orchestrator re-arms a stopped queue on an hourly schedule.
- **FR-008**: Peer research sessions MUST be checked on every hourly wake, and above all after a reset. A peer idle with
  claimed work unfinished is sent a message to resume; the next wake confirms it resumed (busy, or new commits or
  run-log lines), and a peer still idle is messaged again. Every check (time, peer, state, action) is appended to
  `/diagram/.clones/RESEARCH-PEER-CHECKS.log`.
- **FR-011**: Claims MUST stay current while the run lasts. Each write session re-reads `RESEARCH-CLAIMS.md` before
  starting, skips any item another session has claimed since (naming it in the handoff), and marks its group in 269's
  line. No excluded item is left without an owner: each is in "Owned elsewhere" with its owner's confirmation, or in
  the inventory's list of sections passed over, with the reason.
- **FR-009**: The future-work items this feature answers MUST be closed or rewritten to what remains, each with why.
- **FR-010**: What is the GM's to rule (B33, B34, and any contradiction or KNOB-versus-canon question the research
  raises) MUST go to the GM through `escalation-check`.

### Key Entities

- **Item**: one owed question (B01-B46), with the kinds and maps it bears on.
- **Group**: a research session's worth of items on one page, with a prefix range.
- **Outcome**: ACCURATE / KNOB / SILENT / CONTRADICTION-RESOLVED, per item, in `outcomes.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): every item B01-B46 has an outcome line in `outcomes.md` naming its section.
- **SC-002** (FR-003): every kind named by an item has an `Entry:` that resolves, and an `entry-drift` verdict of
  IN-STEP.
- **SC-003** (FR-005): every new or changed section has quote-check, record-format and (for a new key)
  source-applicability verdicts in its group's checks file.
- **SC-004** (FR-007): the run logs show no brief skipped because of a usage-limit failure.
- **SC-005** (FR-006): `git diff` over the feature touches no section in "Owned elsewhere".
- **SC-007** (FR-008): `RESEARCH-PEER-CHECKS.log` shows each peer checked after each reset, and every nudge followed by
  a check that confirms it resumed or a further nudge.
- **SC-008** (FR-011): every item is in the inventory, in "Owned elsewhere" with an owner's confirmation, or in the
  passed-over list with a reason, and no handoff reports an item it researched that another session had claimed.
- **SC-009** (FR-009): every future-work item an inventory line cites is in `closed.md` or rewritten to what remains.
- **SC-010** (FR-010): B33, B34 and every contradiction a handoff raises reach the GM after an `escalation-check` verdict.
- **SC-006** (FR-004): every map-changing outcome has either a regenerated map or a `future-work/` entry with its measurement.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

One line per outcome that changed what a map draws (from `outcomes.md` section 3 and `briefs/engine/log.md`); the
sizes, odds and weights each names as a guess are recorded as guesses at the point of change.

- **B01 fallow** - historically accurate: a field rests 2-4 whole paddy basins, not a blighted patch; the knob
  settled/unsettled and its 0.8/0.2 weighting a guess (research/fields 250).
- **B04 field paths** - historically accurate: every way reaches the field on its bund; the old floor on a spur's drawn length gone
  (fields 290).
- **B06 dry-hem furrows** - historically accurate: rows set tract by tract, turning at the seams; tract sizes and angles
  guesses (fields 180).
- **B07 fan middle** - historically accurate: a fan's middle rolls wild or cleared, the dry hem kept to a wild fan's
  toe; the 0.75/0.25 odds a guess (fields 160).
- **B10 privy** - historically accurate: four attested seats; the per-hamlet weights a guess (homesteads 260).
- **B11 night-soil pit** - historically accurate: a rolled share of pits at the field edge (homesteads 260).
- **B12 bath** - historically accurate: a share of households rolled per hamlet up to most of them, in the front yard or joined by a corridor (homesteads 214).
- **B13 hen coop** - historically accurate: the band centered on Buck's farm survey share (homesteads 215).
- **B14 persimmon** - historically accurate: the recorded crown, in the dooryard or behind the house, never on the flank
  (homesteads 218).
- **B15 woodpile** - historically accurate: woodshed, kizuma along the windbreak, or eaves stack; the even odds a guess
  (homesteads 212).
- **fc:2261 fixture counts** - historically accurate: each declared share is drawn as its count.
- **B16 byre** - historically accurate: the beast with its household, the inner stable drawn against the farmhouse (a
  map drawing convention) or a yard shed; the shared commons shed a rare guess that homesteads/060 now disagrees with, open in future-work.
- **B17 lane ends** - historically accurate: a lane ends at the last dooryard it serves (ways; homesteads).
- **B18 house bearings** - historically accurate: a common bearing within 11.25 deg of south, each house following
  its lanes' margin, one in ten a quarter turn with its yard (the GM's 2026-09-26 ruling) (homesteads 240).
- **B21 footbridge** - historically accurate: log, earth-decked log or plank; the even odds a guess (water 290).
- **B22 weir and intake** - historically accurate: four weir forms (the fence's thin bar a map drawing convention,
  the frame and crib widths a guess) and a race that opens out of the bank with no gate (water 300, 310).
- **B26 homestead woods** - historically accurate: each homestead keeps a wood in the recorded range, the log-uniform roll a guess;
  PARTIAL on three maps (future-work) (vegetation 210).
- **B27 woodland siting** - historically accurate: beyond the fields and above them; the ridge/stream/path boundary a
  guess (vegetation 140).
- **B28 coppice** - historically accurate: stocked at the recorded coppice density; the crown width a guess (vegetation 230).
- **B29 grove bamboo** - guess: the bamboo's small share of the windbreak mix and the household stand's side weights (vegetation 260, 154).
- **B30 windbreak belt** - historically accurate: conifer-led rows or mixed broadleaf, rolled (vegetation 270).
- **B32 duck pen** - historically accurate: removed as a modern-only form, the GM's ruling of 2026-09-28; the ducks are
  written into the paddy's write-up (archetypes 210).
- **B34 dike crops** - historically accurate: mulberry, fruit or tea, the GM's ruling of 2026-09-28; cane, banana and
  vegetable retired; the 3/2/1 weights a guess (archetypes 230).
- **B40 town alley** - historically accurate: beaten earth under a line of drain boards; the ground beside the boards
  a guess (cities/fabric 160).
- **B42 retirement house** - historically accurate (the form): a rolled share of homesteads keeps one; the share and
  the house size guesses (settlements 035).
- **K1-K5 the kinds** - every changed modal was written from its `Entry:` sections and checked by `entry-drift`; the
  bath, coop and persimmon relabeled from guess to historically accurate.

**The GM's rulings of 2026-09-28** ([`rulings-2026-09-28.md`](rulings-2026-09-28.md), verbatim), carried out by E9
and K5: B33 the premodern mulberry spacing kept (no map change); B34 above; B35 hamlets draw no small shrine, only the
rare household one (no map change; the GM's reading that the modern counts describe a wealthier society); B32 above;
B19 the headman's gate confirmed, owed at the village conversion (`future-work/farming-communities.md`,
`migration-plan.md` step 5), the hand-drawn maps unchanged. General rule, in `docs/research-doctrine.md`: anything
attested only in modern sources is eliminated from the premodern maps.

## Review history

- Round 1 (spec-fidelity, 2026-09-27): CHANGES REQUIRED, four findings. (1) The 265 pages' thin sections were excluded
  unchecked: 265 confirmed that none is its own, so they are group X1, and FR-011 leaves no item without an owner. (2) FR-008
  now confirms a peer resumed, re-nudges, and keeps a log (SC-007). (3) Claims are re-read per group (FR-011, SC-008).
  (4) `settlements/030` is B42, and every footnote-less section passed over is listed with its reason.
- Round 2 (spec-fidelity, 2026-09-27): FAITHFUL. All four findings were confirmed fixed. Notes applied: 269's claims line
  names B01-B46 and X1; the inventory cites 265's confirmation; an X1 section reported as a convention moves to the
  passed-over list and `outcomes.md`.
