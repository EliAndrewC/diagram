"""gate() - the registry driver - plus the twin-detector helpers and the CLI main() (feature 024 package split; bodies verbatim)."""

import atexit
import json
import os
from typing import Any

from l7r.diagram.overlap.taxonomy import Manifest, load
from .common_03_capacity import DEFAULT_MANIFEST, WAIVER_META_CHECKS
from .registry import _SEG_DEPS, GATE_SEGMENTS, META_CHECKS

# ---- THE VERDICT JOURNAL (feature 163) ----------------------------------------------------------
# The census asks which checks anything the engine can produce TODAY still makes fail, and `check()`
# inside gate() is the SINGLE point where every verdict is emitted - so that is where firing is
# observed. The alternative, grepping test files for a check's name, is what FR-002 forbids: a name
# appearing in a test is not evidence that the test makes the check FAIL, and 140 of the 152 live
# names appear in one while only ~95 have a negative fixture of any kind.
#
# The variable changes what is RECORDED, never what a map rolls - the same shape as hamletgen's
# STAGE_PROFILE_ENV, which feature 132 permits for exactly that reason, and it carries the same
# guard: a test asserts the manifest and the failure list are identical with it set and unset.
#
# It names a DIRECTORY and each process writes its own file, because the census drives the whole
# pytest suite under `-n auto`; a shared append from a dozen workers interleaves and loses rows.
VERDICT_JOURNAL_ENV = "DIAGRAM_VERDICT_JOURNAL"
_VERDICTS: set[tuple[str, str, str]] = set()
_FLUSH_REGISTERED = False


def record_verdict(name: str, verdict: str, source: str) -> bool:
    """Note that check `name` emitted `verdict` ("FAIL" or "WAIVE") on map `source`.

    A no-op returning False unless the journal directory is set, so an ordinary gate run pays one
    `os.environ` lookup per non-passing check and nothing else. Returning the bool is what makes the
    off-by-default branch testable without reading a file back."""
    global _FLUSH_REGISTERED
    if not os.environ.get(VERDICT_JOURNAL_ENV):
        return False
    _VERDICTS.add((name, verdict, source))
    if not _FLUSH_REGISTERED:
        atexit.register(flush_verdicts)
        _FLUSH_REGISTERED = True
    return True


def flush_verdicts(directory: str | None = None) -> str | None:
    """Write this process's journal, returning its path - or None when there is nothing to write.

    Registered with atexit on the first record rather than called by the gate, because the interesting
    driver is a whole pytest run and no single point in one knows when the last gate() has finished."""
    d = directory or os.environ.get(VERDICT_JOURNAL_ENV)
    if not d or not _VERDICTS:
        return None
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"verdicts-{os.getpid()}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(sorted(_VERDICTS), fh)
    return path


def gate(M: Manifest, verbose: bool = True, only: set[str] | None = None) -> list[str]:
    """Run every check over a manifest dict M and return the list of FAILED check names.
    verbose prints the PASS/FAIL lines. Pass a synthetic M to unit-test a single check.
    A check named in meta(waivers=...) prints WAIVE and does not enter the failure list; see
    WAIVER_MIN_REASON above for the rules that keep that hatch from rotting."""
    # tolerate sparse synthetic manifests (unit tests build only the keys a check needs)
    M = {**DEFAULT_MANIFEST, **M}
    # pre-2026-08-10 manifests stored ONE stage as a bare dict (and the second stage of a
    # two-stage map clobbered the first - the Shiro Daika review catch); DEFAULT_MANIFEST's
    # placeholder is None. Normalized here so every check and the overlap registry read one shape.
    _ts_norm = M.get("theater_stage")
    M["theater_stage"] = [_ts_norm] if isinstance(_ts_norm, dict) else (_ts_norm or [])
    meta = M.get("meta", {})
    scale = meta.get("scale", "village")
    houses, fields = M["houses"], M["fields"]
    # A CAPITAL IS A CITY PLUS A CASTLE (GM 2026-08-10). Every urban rule used to test
    # `scale == "city"` exactly, so the capital tier - added later - silently skipped 74 of
    # them, the funerary program among them (no cremation ground, no ossuary, no mausoleum on
    # a city of 12,400). URBAN is the "walled town of any size" predicate; the handful of rules
    # that are genuinely about a PROVINCIAL city (its wall budget, its governor's mansion - a
    # capital has a castle and its own budget check) keep testing `scale == "city"`.
    URBAN = scale in ("city", "capital")
    field_by = {f["name"]: f for f in fields}
    Wd, Hd = meta.get("W", 1820), meta.get("H", 1180)
    # the "map edge" is the rendered window: the cropped view if one is set (city maps crop tight
    # to the walls and let the countryside run off), else the full canvas.
    _vw = meta.get("view")
    EX0, EY0, EX1, EY1 = (_vw[0], _vw[1], _vw[0] + _vw[2], _vw[1] + _vw[3]) if _vw else (0, 0, Wd, Hd)
    fails: list[str] = []
    # see WAIVER_MIN_REASON above. _waived records what was actually excused (so a waiver that
    # never fired can be reported as stale); _ran records every check name the gate reached, so a
    # waiver naming a check this map's scale never runs is caught as stale too, not silently kept.
    _waivers: dict[str, Any] = dict(meta.get("waivers") or {})
    _waived: dict[str, Any] = {}
    _ran: set[str] = set()

    def check(name: str, ok: Any, detail: str = "") -> None:
        _ran.add(name)
        _is_waived = not ok and name in _waivers and name not in WAIVER_META_CHECKS
        if not ok:  # feature 163: a WAIVE is a suppressed FAIL, so the journal records both as FIRING
            record_verdict(name, "WAIVE" if _is_waived else "FAIL", str(meta.get("name") or "<unnamed>"))
        if _is_waived:
            _waived[name] = _waivers[name]
            if verbose:
                print(f"WAIVE {name}  -> waived: {_waivers[name]}")
            return
        if verbose:
            print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
        if not ok:
            fails.append(name)

    ns: dict[str, Any] = {k: v for k, v in locals().items()}
    if only is None:
        for _seg in GATE_SEGMENTS:
            if _seg.scales is not None and scale not in _seg.scales:
                continue  # feature 145: a segment whose leading guard excludes this scale is never ENTERED (its file stays off the hamlet path)
            ns.update(_seg.fn(**{n: ns[n] for n in _seg.free if n in ns}))
        return fails
    bases = set(only)
    known = set().union(*(s.checks for s in GATE_SEGMENTS)) if GATE_SEGMENTS else set()
    unknown = bases - known
    if unknown:
        raise ValueError(f"unknown check name(s): {sorted(unknown)}")
    requested_meta = bases & META_CHECKS
    if requested_meta:
        raise ValueError(f"meta-check(s) cannot run targeted (use a full gate run): {sorted(requested_meta)}")
    wanted = {i for i, s in enumerate(GATE_SEGMENTS) if (bases & set(s.checks)) or s.always}
    frontier = set(wanted)
    while frontier:
        deps = set().union(*(_SEG_DEPS[i] for i in frontier)) - wanted
        wanted |= deps
        frontier = deps
    for i in sorted(wanted):
        _seg = GATE_SEGMENTS[i]
        if _seg.scales is not None and scale not in _seg.scales:
            continue
        ns.update(_seg.fn(**{n: ns[n] for n in _seg.free if n in ns}))
    return fails


# ---- Pool-level twin-detector (feature 005) -----------------------------------------------------
# The per-map gate() validates ONE manifest; this is a CROSS-map tool. Two villages that share a water
# direction (down_deg) should still read as different PLACES - the GM's complaint was that Kikuta was a
# near-copy of Hoshigaoka down to the headman's house position. So for every same-down_deg pair we count
# how many of the structural axes a viewer actually reads (SC-001) fall in DIFFERENT coarse buckets, and
# flag the pair when too few differ. Two design choices, both from research.md D6:
#   - Same-down_deg SCOPING: villages that already differ by water direction are trivially distinguishable
#     and are not compared (comparing them would dilute the signal).
#   - COARSE buckets (which side / which type / which octant), never pixel positions, so genuine near-
#     variants are not falsely flagged as twins - the axes answer "different KIND of place?", not "moved a
#     few px?". The 4-of-7 threshold is the tuning target; recorded with its reasoning in settlements.md.
TWIN_AXES = ("cluster_region", "cluster_shape", "headman_side", "lane_skeleton", "water_source", "focal_set", "grain_orient", "settlement_form", "pond_layout")
TWIN_MIN_DIFF = 4  # a same-down_deg pair must differ on >= this many of the 8 axes to read as distinct


def main(path: str) -> int:
    return 1 if gate(load(path)) else 0
