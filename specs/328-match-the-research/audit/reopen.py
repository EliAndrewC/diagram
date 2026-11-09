"""Which closed rows a later found file reopens (feature 374 batch 3's plan review, W120-10).

A row's wave comes from `waves.json` by key, so a finding filed again after the wave that closed its key inherited that
closing mark: `_knobs.py::<module>#kosatsuba_seat forms`, closed at wave 115 and filed DRIFTED by wave 120's check, read
wave 115 and dropped out of the work list and the report alike. Batch 2's own rule: "a row closed at an earlier wave whose
claim drifts again reopened".
"""

from __future__ import annotations

import re


def wave_number(wave: str) -> float:
    """A closing wave's number (`115`, `51b` -> 51.0); one with no number never reopens (inf)."""
    m = re.match(r"\d+", str(wave or ""))
    return float(m.group(0)) if m else float("inf")


def reopened(waves: dict[str, str], filed: dict[str, float]) -> dict[str, str]:
    """`{key: the wave that had closed it}` for each key filed (`found_order`'s place in time) after its closing wave."""
    return {k: waves[k] for k, at in filed.items() if waves.get(k) and at > wave_number(waves[k])}
