# Implementation Plan: Which Automated Checks Still Earn Their Keep (feature 141)

**Date**: 2026-08-28 | **Spec**: [spec.md](spec.md)

## Summary

A census tool (`tools/check_census.py`, `make check-census`) derives per check its manifest inputs (the
registry's dataflow, transitively), the stage those inputs settle at on per-stage snapshots of the
reference and the seed-19 polder, its branching readers, its fixtures by tier - and a mechanical verdict.
A hand pass classifies every mechanical candidate by how its PLACER behaves: a hard guarantee (it drops
or refuses rather than place wrongly) with the placer test that names it - RETIRE; a best-effort placer
(the caption seat, the board, the bridges, the belt) - KEEP, the check is the guarantee; a plausible
guarantee no test names - KEEP, named for the GM; a legacy feature vacuous on hamlets - the GM's choice
with the legacy tiers. Retirement removes the segment, its check-village tests and its fixtures (whole
segments only; a kept check bundled in a segment with a retired one holds both back, named). The
doctrine is rewritten. The GM accepts after the explanation, and may cut more.

## Constitution Check

I-V, VII-IX: N/A. VI: `make done` after every batch; the ledger is the evidence. X: ruff / mypy / the
100% floor where it applies (the census tool is a by-hand tool outside the floor, like its siblings).
XII: no world assertion changes; record-the-why: every verdict carries its reason in the ledger. XIII:
no live map's kept-check verdicts change (the retired checks are removed, not failed). XIV: defects found
are tasks. XVI: spec FAITHFUL after three rounds.

## Design decisions

1. Retire whole segments only; a partial segment is a hand edit that risks the kept check - held and named.
2. FR-002(c) is read strictly: no retirement without an EXISTING placer test that names the invariant;
   "by construction" without a test is KEEP-named (the GM may cut).
3. The legacy tiers' checks and fixtures are untouched until the GM rules (round-1 review).
