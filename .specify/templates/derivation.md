# Derivation - <stage> (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.derivation.md` and fill it from the stage's contract alone, before today's
code or counts are read (the phase checklist's box 2). `make work-budget-bundle MODE=budget` refuses a derivation missing any
section or field below, naming it (feature 443 T13, the GM 2026-10-28); the `work-budget` agent then judges the arithmetic against
`docs/work-budget-rubric.md`. No code, no path under `l7r/`, no figure of today's counts.

**A Mode A stage** (feature 449 T201) has no households: it is sized by the pool sheets, and its derivation lives with its feature
(T198's `specs/449-rust-codebase/derivations/T198-placer.md` is the worked one). It opens its Contract with a line
`Sizes: pool sheets: <sheet>, <sheet>, ...` naming each sheet, and, where it gives lengths in px, `Scale: <N> px = <M> ft` once (each
a `- ` bullet); with no `Sizes:` line, or `Sizes: households`, everything below holds as written. Under pool sheets:
- the `items` row's value gives each sheet's count in the `Sizes:` order (`N = <n>, <n>, ...`);
- a scope may also be `per <step>` where another row's factor names that step and is itself counted per item (`per query`, with a
  `queries` row per item), or a standard scope with a qualifier after a comma (`per item, on the search kinds`);
- in `## Indexes` only a bullet naming a grid is read as one; it states its cell size (`cells of <N> ft`, or px at the stated
  scale), and its density is a count row of the entries a cell holds, measured on each sheet, in place of a smallest side;
- `## Totals` holds one line per named sheet, `- at <sheet>: <expression> = <value>`, and one for them all,
  `- all sheets: <expression> = <value>`, holding each sheet's value once and equal to their sum;
- `make budget-set PHASE= DERIVATION= VERDICT=` records those per-sheet Totals as the budget, and `make budget-sheets` compares
  counts per sheet against them.

Each round's verdict is saved beside the derivation as `<its file name>.verdict-<N>.txt` (`T198-placer.md.verdict-1.txt`), or as
`<stage>.verdict-<N>.txt` for a `<stage>.derivation.md`, so the bundle carries it and `## Earlier findings` answers it.

## Contract

- Reads: <the manifest keys and plan fields the stage reads>
- Writes: <what it places, and the manifest keys it writes>
- Keeps: <the cohort properties and the research claims that govern it>
- Bounds: <what the contract fixes: the range of households, the sizes and spacings the stage is given>

## The algorithm

    <pseudocode, from the contract alone>

## The count, factor by factor

One row per factor; every column filled. SCOPE is one of `per item` (per thing placed), `over the run` (a total for the whole
stage) or `once` (setup outside the loop). A bound that holds only over the run is never written per item, and a `once` term
states its own bound. SLACK covers only what varies around a stated bound (at most 2, S7); work you can name - a flag set, a
record written, a jitter drawn - is a factor of its own, never folded into the slack. A factor's value comes from the contract,
never from a figure with no source. WORST CASE names where the bound is tight, at the smallest and the largest n the contract allows.

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | <n> | <from the contract> | <smallest and largest n> |

So: <the total, items x candidates x checks x slack (slack at most 2), plus each once term>.

## Totals

One line per size, the expression in the table's own figures (digits, + - x / and brackets); `make work-budget-bundle` evaluates
each and refuses a missing size or a value more than 1% off its expression. A derivation that uses a grid or spatial index counts
the cells it examines in a row of its own.

- at 20: <expression> = <value>
- at 40: <expression> = <value>
- at 80: <expression> = <value>

## Cheaper algorithms considered

One line each: used, or why not (rubric S1-S3).

- sweep:
- grid or spatial index:
- priority queue:
- incremental update:
- memoizing what a scan does not change:
