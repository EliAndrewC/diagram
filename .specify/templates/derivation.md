# Derivation - <stage> (feature 444)

Copy to `specs/444-work-budget-program/phases/<stage>.derivation.md` and fill it from the stage's contract alone, before today's
code or counts are read (the phase checklist's box 2). `make work-budget-bundle MODE=budget` refuses a derivation missing any
section or field below, naming it (feature 443 T13, the GM 2026-10-28); the `work-budget` agent then judges the arithmetic against
`docs/work-budget-rubric.md`. No code, no path under `l7r/`, no figure of today's counts.

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

## Cheaper algorithms considered

One line each: used, or why not (rubric S1-S3).

- sweep:
- grid or spatial index:
- priority queue:
- incremental update:
- memoizing what a scan does not change:
