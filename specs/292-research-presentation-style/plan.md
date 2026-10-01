# Plan - feature 292, how a research section is presented

**Spec**: [`spec.md`](spec.md) | **Phase**: sweep (the pilot signed off, 2026-09-30)

## Approach

1. **The guide** is `research/STYLE.md`, one home, read by the writers and handed to the check in its bundle (the check
   judges only rules the guide states, so the guide and the check cannot drift apart). Each rule is marked GM or
   inferred; the pilot's rounds turn inferred rules into GM ones or strike them.
2. **The check** is `.claude/agents/record-style.md` - Opus at high effort, `omitClaudeMd`, reading
   `make check-bundle ... FOR=record-style` (the section, its notes, `STYLE.md`, the glossary variant index; `EXTRA=` the
   old sections of a merge, for the merge audit). `check-bundle-hooks.sh` refuses a dispatch of it into the repository
   and hands back that command.
3. **The pilot topic** is one fragment, `homesteads/010-groves-of-trees-around-farmhouses-yashikirin`, folding 010, 710
   and 715; the notes deduplicated (a passage quoted two or three times is quoted once); every inbound link, the
   Windbreak-grove modal's `Entry:` and the code comments re-aimed.
4. **The hover link**: `citations.to_work_entries` rewrites each key link in the derived `citations/<page>.js` to
   `citations/<page>.html#work-<key>`; the citations page keeps its links to the sources.
5. **Sources without a roster**: `sources.footnote_sources` reads the keys of a section's footnotes from its citations
   page; `research_sources` uses the roster where there is one, else the footnotes.
6. **Glossary**: `knob` redefined in the GM's terms; `canopy-tree` added; `appurtenance` removed (the rewrite retired
   its only use, and an unused term fails the gate).

## Decisions

- **D1 - the guide is handed to the check, not copied into its contract.** A defined agent launches without the
  repository's rules (feature 256), so a rule it needs must reach it; the bundle carries the one copy, and the contract
  carries only the procedure and the verdict form. The alternative - the rules restated in the agent file - is two
  copies of a guide the pilot exists to revise.
- **D2 - the seeded run.** The check is run on the grove section as the GM quoted it (main at 063f6608c) without being
  told the GM's objections, and its findings are compared with them (SC-007); then on the rewrite, with the merge audit.
- **D3 - the size cap is raised with the GM, not worked around.** The merged fragment is 33,479 bytes against the
  20,000 cap (the three it replaced were 42,132); `make quick` fails on it until the GM chooses. The cap's reason is what
  one check reads in a turn; a topic section is the GM's new unit.
- **D4 - built on feature 291's committed work**, merged into this clone; nothing from this clone is pushed until 291
  lands and the pilot is signed off.
- **D5 - failures outside this feature**: 13 Kashikawa and Mizuguchi pool tests fail in this clone - pool-map checks
  in files this feature does not touch, over maps feature 291's work in progress is changing. Not yet measured at 291's
  commit alone; to be ledgered before anything here lands.

## The sweep (after the GM's sign-off, 2026-09-30)

The GM: *"proceed with reorganizing each and every research section, combining similar ones as appropriate, as we
have been doing and then applying our new style guide"* (request.md, the last entry). The record holds 762 fragments
over 12 pages and the `cities/` collection.

- **D6 - a topic plan per page, made from a digest.** An Opus planner reads a digest of its pages (each section's
  title, size, opening and the modals whose `Entry:` names it) and the titles of every section of the record, and
  writes `sweep/plan-<page>.md` (all 21 are committed there, with the two plans for the sections main added during the sweep, `plan-additions-*.md`): the topics, each with the sections it folds, its rendering section, the modals to
  re-aim and its size; the groups a writing session takes (at most four topics and 45,000 bytes of folded sections);
  the folds across pages; the confusable pairs. The session reviews each plan before a brief is written from it. The
  alternative - each writing session deciding its own folds from its slice of a page - cannot see a fold that crosses
  its slice, which is how the sun topic's vegetation section would have been missed.
- **D7 - every group is worked in two fresh headless sessions** (`make page-session`, the record's standing process,
  features 250 and 274): a write session (fold, restyle, split the rendering section off, re-aim links and `Entry:`
  tags, the prepass and the record tests) and a check-and-apply session (`record-style` with the merge audit,
  `quote-check` in its batches, `record-format` on both sections, `entry-drift` on every modal whose section moved,
  `translation-check` on the pairs `make translation-owed` names; each report applied, the record rebuilt and tested).
  These are the checks the three pilot topics ran. The briefs are generated from the plan by `sweep/make_briefs.py` from the two templates beside it, so every group
  gets the same procedure; the generated briefs are not committed (they are the templates filled from the plans).
- **D8 - the order: pages feature 291 is not editing first.** Feature 291's session is still editing homesteads,
  vegetation and ways in its own clone; editing the same fragments here would make every merge of its work a
  conflict. So buildings, religion-and-death, urban-features, towns, archetypes, fields, water, settlements,
  presentation and the cities collection go first, and vegetation, ways and homesteads last, after 291's latest work
  is merged in again.
- **D9 - parallel queues in separate clones, merged back.** First planned as one queue at a time; measured, one queue
  would have taken some 90 hours, and the containers' working set stayed between 3.5 and 6 GB of the cap with two
  and then three queues running, so the sweep ran in three clones (`diagram-reorg`, `-2`, `-3`), each on its own pages,
  pages that fold into each other kept in one clone where they could be. A queue's remaining briefs were moved to an
  idle clone by overwriting them, in place, with a `kind=handover` stub that ends at once (the runner reads a brief only
  when its session starts). The clones were merged back into this one by `sweep/tools/`: `resolve.py` (a modal's
  `Entry:` merged by the clone that owned each page; glossary variants unioned), `entry_union.py` (both clones swept
  one page), `relink.py` (every link to an anchor a fold retired, re-aimed from the handoffs' `SECTION=`/`OLD=` record
  of what each topic absorbed); a section one clone folded away won its modify/delete conflict. Three findings changed
  the briefs mid-run: a headless check session that dispatched its agents in the background never heard back (the
  check template now dispatches in the foreground, two at a time); a PDF over the fetch tool's 10 MB is read with
  `curl` and `pdftotext`, never sent to the GM's download list for its size; and the prompt hook's automatic sync with
  main conflicted with feature 291's work in progress, so an untracked `SYNC-HELD-292.txt` held each clone's merge
  until 291 landed, and main was merged by hand.
- **D9a - the closing pass.** What the checks left "for the GM" (26 items) went through `escalation-check` (1 kept
  for the GM and answered, 24 the session's own), and what they deferred to a topic restyled later, are task T26,
  worked in `sweep/closing/` briefs after the last merge.
- **D10 - landing.** As D4: the sweep commits in this clone and nothing lands until feature 291 has landed; then main
  is merged, the full gate runs, and the feature lands with every page restyled.
