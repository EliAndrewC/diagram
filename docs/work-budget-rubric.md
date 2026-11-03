# The work-budget rubric - the standards a stage's budget is held to

Load this file when: you write a stage's derivation for feature 444, or you are the `work-budget` agent reading a bundle (the
bundle carries this file as `rubric.md`).

The standards are the design the GM approved on 2026-10-28 (`specs/443-work-budget-tooling/request.md`, section 2), stated here
once. A budget counts BASIC OPERATIONS - a point tested against a shape, a distance taken, an index cell examined, a candidate
scored - the measure that survives a port to Rust (`l7r/diagram/work_counts.py` counts them; `make work-budget` reports them).
Python calls and seconds are recorded beside them, and neither is the budget.

## The standards

- **S1 Indexed neighbors.** A check on a candidate examines a bounded number of neighbors, through an index. The bound is stated
  and does not grow with the number of households.
- **S2 Derived candidates.** The candidates tried per thing placed are a constant derived from the geometry, such as the sites
  within reach at the rule's spacing. They are never a tuned retry count.
- **S3 No all-pairs.** No pass over a growing set runs inside another loop over a growing set, unless the inner set has a stated
  constant bound.
- **S4 Ask before placing.** Feature 417's principle: every rule is asked of a candidate before the thing is placed. Nothing is
  placed and then moved, dropped or repaired. The counters report drops and moves (`placed@`, `dropped@`, `moved@`), and the
  budget for them is zero.
- **S5 Count the work where it happens.** Work in C or numpy is counted per element. An uncounted inner loop is a finding.
- **S6 Linear growth.** A stage's exponent from 20 to 80 households is at most 1.15, which allows n log n. A stage over that limit
  needs a stated reason, such as a bounded n.
- **S7 Show the arithmetic.** A budget is items x candidates x checks x slack, slack at most 2. Each factor names its reason
  (S1-S3).
- **S8 Count the typical case, not the worst.** A budget is what the stage should do on the rolls it is held to: each factor
  at the mean the stage's output shows (things per area, parts per index cell, the candidates the contract's search order
  reaches), never at the densest cell or the last candidate, and never a product of maxima. Slack (at most 2) covers what
  varies around that mean. A cost per thing placed above the reference's 4,000 needs a named reason. WHY (the GM 2026-10-28,
  on a target of 15.3M at 40 households, above what the roll counts today: "I thought the idea was to REDUCE the number of
  operations. Why would we be targeting something HIGHER?"; ask:444-budget-standard): every factor taken at its worst at once
  compounds, and a budget the stage already meets is no target.
- **S9 Touch only what can win.** A stage that picks one thing, or a few, from a set - the busiest seat, the nearest site, the
  best-scored candidate - does work in proportion to the candidates that could win, not to the set they are drawn from: a bound
  read once from an index (a cell's count, an upper bound on any score inside it, its distance) ranks the cells, and the search
  stops when the best exact score found beats the next cell's bound (branch and bound: exact, not a heuristic). A row that
  scores, sorts or paints every member of a set that grows with the map names why no bound prunes it, in the derivation's
  `- pruning:` line. Work only a knob's branch needs (an `entrance` board's ways out) is charged at that branch's share, never on
  every roll. WHY (the GM 2026-10-29, on the notice board: "Why do we think it should take 8,730-11,277 operations to place a
  single notice board?!"): its derivation scored every verge seat on every way and sorted them all to test about 1.3 seats - 97%
  of its count was the search for the winner - and four rounds passed it, because the cheaper-algorithm question asked for data
  structures, never whether the set needed visiting, and a reason that the stage is one thing satisfied the reference's screen.

- **S10 An estimate, held with leeway; growth held hard.** A budget is an estimate, so a rebuilt stage counting more than it, and
  at most twice it at 40 and 80 households, is accepted on MODE AUDIT's LEEWAY: every loop counted (S5), nothing repaired (S4),
  growth within the budget's (S6), and the excess named - the work or the factor the derivation did not price - and judged
  reasonable. Work the stage must do that the derivation never counted (a branch, a write, a rule of its contract) is not
  leeway: the derivation is revised to count it under `## Work the first derivation missed`, judged in MODE BUDGET as any other,
  and on SOUND the budget is raised (`make budget-set RAISE=1`) to at most twice its first figure at 40. Past twice it the raise
  owes the rigorous analysis: each missed item tied to the contract's rule that owes it, and a second SOUND from an independent
  MODE BUDGET dispatch of the same bundle (`SECOND=`). On a budget raised on one SOUND, the accepted count stays within
  twice the first figure, LEEWAY not carrying it past; nothing passes ten times the first figure at 40 - not a raise, not an
  accepted count on a raised budget - without the GM's words. Apart from the twice-the-budget count and growth, a LOOSE or an OVER
  is given for a finding only where it would move the stage's total at 40 by more than half; a tighter bound worth less is a note
  under SOUND, WITHIN or LEEWAY, owing no round. Nothing here loosens S3 or S6. WHY (the GM
  2026-11-03, feature 444 amendment 7): "if we discover that there are things that we didn't take into account, then it makes
  sense to raise the operations budget rather than to fight ... I would frankly be okay with things that are 50% higher or even
  twice as high ... I don't want to just completely relax the performance requirements, because if we end up with some kind of
  n squared algorithm, then even in Rust that will become a problem."

## The reference: a homestead (S7 worked out)

The design's reference point, factor by factor. Its figures are the design's illustration, labeled GUESS until feature 444's
homesteads phase derives each from the stage's contract; what this section fixes is the FORM a derivation takes.

| factor | how it is derived | the design's figure |
|---|---|---|
| items | the houses the stage places: one per household | 1 per household |
| candidates per house (S2) | the seats within the house's reach at the rule's spacing: about (reach / spacing)^2 sites of a grid over the reach, the ones the reach's shape keeps | about 20 |
| neighbors per candidate (S1) | what one index cell and its ring hold at the mean density the stage's output shows (S8): the placed parts a cell the size of the largest clearance holds | about 10 |
| checks per neighbor | the parts of a homestead the program lays (house, yard, kura, sheds, fixtures), each tested once | about 10 |
| slack | at most 2 (S7) | 1-2 |

So about 20 x 10 x 10 = 2,000 basic operations per house, 4,000 at the full slack: the budget for a house is a few thousand
operations, flat in the number of households (S6: the index keeps the neighbors bounded as the hamlet grows).

## The verdicts

- MODE BUDGET (a derivation, before the rebuild; no code and no counts of today's code in the bundle): **SOUND**; **LOOSE**,
  naming the factor and a tighter bound; **UNDERIVED**, naming the factor with no reason.
- MODE AUDIT (the landed code against its counters): **WITHIN**; **LEEWAY**, over the budget and at most twice it, naming the
  excess and why it is reasonable (S10); **OVER**, naming the chain; **UNCOUNTED**, naming the loop.

The agent's contract is `.claude/agents/work-budget.md`; a first budget is set only from a SOUND verdict (`make budget-set`),
raised on a SOUND re-derivation naming the work it missed (`make budget-set RAISE=1`, S10), and otherwise changed only with the
GM's words (`make budget-change`).
