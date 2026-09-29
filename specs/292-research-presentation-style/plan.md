# Plan - feature 292, how a research section is presented

**Spec**: [`spec.md`](spec.md) | **Phase**: pilot

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
