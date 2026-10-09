"""Which code feature 328 fixes (amendment 8, the GM 2026-10-07): the code the kept maps actually EXECUTE - the scripted
hamlets, the magistracies and the country shrines - and the Mode A procedures; code only the legacy hand-authored villages,
towns and cities run is DEFERRED: ranked, never taken by a wave, and shown DEFERRED by `make claims-report`.

    python3 specs/328-match-the-research/audit/scope.py <skill dir> <ranking.json> <claims-index.json> <scope.json> <claims-deferred.json>

THE MEASURE IS THE EXECUTION RECORD, not a name: each KEPT map's own gen-cache entry (`KEPT_MAPS`: the pool hamlets, the
magistracy sheets, the country shrine; taken on today's engine with `make map`) records each function that RAN as
`(path, qualname)`, the record `tools/hamlet_floor` reads. No other entry counts: `.gencache/rolls` holds the gate's tests of
the legacy village roller, unit tests' rolls and stale rolls of older code. A unit is in scope when
  - it is a Mode A procedure (`buildings.md`, `buildings/**`);
  - it is under `hamletgen/` - the scripted hamlet's own code, which only a scripted hamlet (any seed, any form) runs;
  - it is a function or method a recorded run executed;
  - it is a class one of whose methods a recorded run executed;
  - it is a module-level constant an executed function of the engine reads by name, or a knob it registers is in use;
  - it is a class executed code constructs or names;
  - it is a module-level (`<module>`) claim on a knob in use - an executed function resolves the registry's knob by name
    (`RESOLVERS`, `KNOBS[...]`), or its typing rule ran - or, naming no knob, on a module a kept map runs;
  - it is a check the gate runs against the kept maps' finished output (`KEPT_CHECKS`, each with its reason);
  - it renders every kept map's page after the traced roll (`RENDER_PATH`), or it is a page Kind whose `key` a kept map's
    executed code records a feature under (a Kind has no method to run, and the registry finds it without naming it).
Everything else is DEFERRED, and so is a claim whose value no kept map reads though its unit runs (`DEFERRED_ON_MEASURE`,
each with its measured reason). The deferred list (`claims-deferred.json`) is derived over EVERY claimed unit, not only the units
with a finding today, so a legacy-only unit that drifts later reads DEFERRED too; re-run this when a wave lands or the pool
gains a kept map (the cache must hold each kept map's entry - `make map GEN=<gen>`).
"""

from __future__ import annotations

import ast
import glob
import json
import sys
from pathlib import Path


KEPT_MAPS = (
    "pool/hamlets/*/*.gen.py",  # the scripted hamlets
    "pool/magistracies/*/*.gen.py",  # the magistracy sheets
    "pool/country-shrines/*/*.gen.py",  # the country shrine
)


KNOB_NAMES: set[str] = set()
RESOLVERS = {"resolve", "resolve_knob", "pin_knob"}  # the calls that resolve the REGISTRY's knob by name; a hamlet rolling its own
# `hamletgen/` table under the knob's name (`_roll(seed, "settlement_form", SETTLEMENT_FORMS)`) does not put the registry entry in
# use - that table is the kept unit
KNOB_FEEDS: set[str] = set()  # the constants an in-use knob's registration reads (`FOOTBRIDGE_FORMS` in `Knob(..., list(FOOTBRIDGE_FORMS))`)


def all_knob_names(skill: Path) -> set[str]:
    """Every registered knob's name."""
    out: set[str] = set()
    for f in glob.glob(str(skill / "l7r/diagram/**/*.py"), recursive=True):
        try:
            tree = ast.parse(Path(f).read_text())
        except SyntaxError:
            continue
        out |= {str(c.args[0].value) for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id.endswith("Knob") and c.args and isinstance(c.args[0], ast.Constant)}
    return out


def executed(skill: Path) -> set[tuple[str, str]]:
    """Every `(path, qualname)` a kept map's own gen-cache entry records as executed - never a gate test's roll (the legacy
    village roller's), a unit test's, or an entry of the code as it stood weeks ago (`.gencache/rolls`, `h10`, `h20`)."""
    out: set[tuple[str, str]] = set()
    entries = [skill / ".gencache" / Path(g).name[: -len(".gen.py")] / "meta.json" for pat in KEPT_MAPS for g in glob.glob(str(skill / pat))]
    for meta in (str(e) for e in entries if e.is_file()):
        deps = json.loads(Path(meta).read_text()).get("deps") or {}
        out |= {(str(p), str(q)) for p, q, *_ in deps.get("functions", []) if q != "<module>"}
    return out


def names_read(skill: Path, ran: set[tuple[str, str]]) -> set[str]:
    """Every bare or attribute name the executed functions read."""
    by_file: dict[str, set[str]] = {}
    for p, q in ran:
        by_file.setdefault(p, set()).add(q)
    out: set[str] = set()
    for p, quals in by_file.items():
        try:
            tree = ast.parse((skill / p).read_text())
        except (OSError, SyntaxError):
            continue

        def walk(node: ast.AST, prefix: str, quals: set[str] = quals) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    q = f"{prefix}{child.name}"
                    if not isinstance(child, ast.ClassDef) and q in quals:
                        out.update(n.id for n in ast.walk(child) if isinstance(n, ast.Name))
                        out.update(n.attr for n in ast.walk(child) if isinstance(n, ast.Attribute))
                    walk(child, q + ".")

        walk(tree, "")
    return out


KEPT_CHECKS = {
    # a check the gate and `tools/cohort_audit` run against the scripted hamlets' finished maps (tests/gate/test_farm_groves.py),
    # so no generation record holds it though the kept maps are what it judges
    "l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded",
}


RENDER_PATH = {
    # what renders every kept map's page AFTER the roll the gen cache traces (`render_png` and the page's raster tiles), so no
    # generation record holds it though every kept map runs it (spec-fidelity, amendment 13 round 2)
    "l7r/diagram/settlement/finish.py::FinishMixin.render_png",
    "l7r/diagram/interactive/raster.py",
    # the page vocabulary's own tables, built at import for every kept map's page (the trace records functions, not module code)
    "l7r/diagram/interactive/classes/__init__.py",
    "l7r/diagram/interactive/classes/_base.py",
    "l7r/diagram/interactive/classes/siblings.py",
}


KIND_KEYS: dict[tuple[str, str], str] = {}  # (path, Kind class) -> its `key`, the string a feature is recorded under
STRINGS_USED: set[str] = set()  # every string literal an executed function passes (`add(..., cls="homestead grove")`)


def kind_keys(skill: Path) -> dict[tuple[str, str], str]:
    """Each Kind class's `key` under `interactive/classes/`: a Kind has no methods to run and the registry finds it without naming
    it, so it is in use when executed code records a feature under its key."""
    out: dict[tuple[str, str], str] = {}
    for f in glob.glob(str(skill / "l7r/diagram/interactive/classes/*.py")):
        rel = str(Path(f).relative_to(skill))
        for cls in (n for n in ast.parse(Path(f).read_text()).body if isinstance(n, ast.ClassDef)):
            for a in (n for n in cls.body if isinstance(n, ast.Assign)):
                if any(isinstance(t, ast.Name) and t.id == "key" for t in a.targets) and isinstance(a.value, ast.Constant):
                    out[(rel, cls.name)] = str(a.value.value)
    return out


def strings_used(skill: Path, ran: set[tuple[str, str]], read: set[str] = frozenset()) -> set[str]:
    """Every string literal inside the executed functions, and in a module constant of theirs they read by name (`FIXTURE_CLASS`
    maps each farmstead fixture to the key its feature is recorded under)."""
    out: set[str] = set()
    for p in {p for p, _q in ran}:
        try:
            tree = ast.parse((skill / p).read_text())
        except (OSError, SyntaxError):
            continue
        quals = {q for pp, q in ran if pp == p}
        for a in (n for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))):
            targets = a.targets if isinstance(a, ast.Assign) else [a.target]
            if a.value is not None and any(isinstance(t, ast.Name) and t.id in read for t in targets):
                out.update(str(n.value) for n in ast.walk(a.value) if isinstance(n, ast.Constant) and isinstance(n.value, str))

        def walk(node: ast.AST, prefix: str) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    q = f"{prefix}{child.name}"
                    if not isinstance(child, ast.ClassDef) and q in quals:
                        out.update(str(n.value) for n in ast.walk(child) if isinstance(n, ast.Constant) and isinstance(n.value, str))
                    walk(child, q + ".")

        walk(tree, "")
    return out


DEFERRED_ON_MEASURE = {
    # only plain houses keep a byre: every house a scripted hamlet seats is kind 'plain' with no role (the five hamlets 15, 20,
    # 16, 12 and 19 plain), so the filter excludes nothing a kept map draws; only the legacy roller seats a big or headman
    # house (wave 58's measure, 2026-10-08)
    "l7r/diagram/settlement/shrines_wells/byres.py::DraftByresMixin.draft_byres#only plain houses keep a byre",
    # the pond feeder stream: drawn only where a comb's pond source carries `feeder`, and the one hamlet pond source (the
    # polder's reservoir, `hamletgen/water/polder.py`) carries none - no kept map draws it (wave 51's measure, 2026-10-08)
    "l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#pond feeder from the sluice",
    # the lotus draw: `_pick_overlay_plots` runs on Kuwabata for its wholesale dike-pond conversion only; no kept map draws a
    # lotus overlay (no manifest names one), so the lotus branch is never asked of one (wave 51's measure, 2026-10-08)
    "l7r/diagram/settlement/fields/landuse.py::LandUseMixin._pick_overlay_plots#lotus draw",
    # a claim whose value no kept map reads, though its unit runs: `fixture_forms` passes `privy_seat_weights(seed)`, so only
    # `bundle.py`'s fallback reads the class default (spec-fidelity, amendment 8 round 3)
    "l7r/diagram/settlement/homestead_parts/fixture_seats.py::FixtureForms#privy seat weights",
    # the town and city branch of `dwellings_shown` (`kind.excludes_farms`): every kept map is a hamlet, a magistracy sheet or
    # the country shrine, whose page Kind counts `houses` - the town branch never runs on one (wave 49's measure, 2026-10-08)
    "l7r/diagram/interactive/place.py::dwellings_shown#town and city count no farmhouses",
    # the gate complex's and the castle's matrix entries: no kept map draws a city or town gate (`gate_structs`) or a castle
    # (`castle`), so neither pair is ever asked of one (wave 49's measure, 2026-10-08)
    "l7r/diagram/overlap/taxonomy.py::_FIXTURE_MOUNTS#gate complex and inspection post",
    "l7r/diagram/overlap/taxonomy.py::_MATRIX_ALLOWED_KEYS#castle towers on the rampart",
    "l7r/diagram/overlap/taxonomy.py::_MATRIX_ALLOWED_KEYS#castle bridge at its gate tower",
    # the rampart's matrix entries: no kept map draws a town or city wall (`wall`), so no way or watercourse is ever asked
    # through one (wave 49's measure, 2026-10-08)
    "l7r/diagram/overlap/taxonomy.py::_MATRIX_ALLOWED_KEYS#ways and water through the rampart",
    "l7r/diagram/overlap/taxonomy.py::_MATRIX_ALLOWED_KEYS#moat against the rampart",
}


def knobs_in_use(skill: Path, ran: set[tuple[str, str]]) -> set[str]:
    """The knobs a kept map uses: a registered knob (`register_knob(Knob("name", ...))`) an executed function resolves by name
    (`resolve_knob("name", ...)`), or whose typing rule a kept map's run executed."""
    resolved: set[str] = set()
    ran_names = {q.split(".")[-1] for _p, q in ran}
    for p in {p for p, _q in ran}:
        try:
            tree = ast.parse((skill / p).read_text())
        except (OSError, SyntaxError):
            continue
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            f = call.func
            fname = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
            if fname in RESOLVERS and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
                resolved.add(call.args[0].value)  # the registry's knob resolved by name (`resolve`, `resolve_knob`, `pin_knob`)
        for sub in (n for n in ast.walk(tree) if isinstance(n, ast.Subscript)):
            if isinstance(sub.value, ast.Name) and sub.value.id == "KNOBS" and isinstance(sub.slice, ast.Constant) and isinstance(sub.slice.value, str):
                resolved.add(sub.slice.value)  # `KNOBS["name"]`
    for f in glob.glob(str(skill / "l7r/diagram/**/*.py"), recursive=True):
        try:
            tree = ast.parse(Path(f).read_text())
        except SyntaxError:
            continue
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            f_ = call.func
            if not (f_.id if isinstance(f_, ast.Name) else "").endswith("Knob") or not call.args or not isinstance(call.args[0], ast.Constant):
                continue
            rule = next((k.value for k in call.keywords if k.arg == "typing_rule"), None)
            if isinstance(rule, ast.Name) and rule.id in ran_names:
                resolved.add(str(call.args[0].value))
    in_use = resolved & all_knob_names(skill)
    for f in glob.glob(str(skill / "l7r/diagram/**/*.py"), recursive=True):
        try:
            tree = ast.parse(Path(f).read_text())
        except SyntaxError:
            continue
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Name) and call.func.id.endswith("Knob") and call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value in in_use:
                KNOB_FEEDS.update(n.id for n in ast.walk(call) if isinstance(n, ast.Name))
    return in_use


def knob_of_constant(skill: Path, path: str, name: str) -> str | None:
    """The knob a module constant registers (`NAME = register_knob(Knob("knob", ...))`), or None."""
    try:
        tree = ast.parse((skill / path).read_text())
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            for call in (n for n in ast.walk(node.value) if isinstance(n, ast.Call)):
                if isinstance(call.func, ast.Name) and call.func.id.endswith("Knob") and call.args and isinstance(call.args[0], ast.Constant):
                    return str(call.args[0].value)
    return None


def scope_of(uid: str, ran: set[tuple[str, str]], read: set[str], knobs: set[str] = frozenset(), skill: Path | None = None, label: str = "") -> str:
    path, unit = uid.split("::", 1)
    path = path.replace(".claude/skills/diagram/", "")
    if path.startswith(("buildings", "docs/buildings")):
        return "mode-a"
    if f"{path}::{unit}#{label}" in DEFERRED_ON_MEASURE:
        return "deferred"
    if f"{path}::{unit}" in KEPT_CHECKS or path.startswith("l7r/diagram/hamletgen/"):
        return "kept"  # hamletgen/ is the scripted hamlet's own code: no legacy map reaches it, whatever seed or form runs it
    if (path, unit) in ran or any(p == path and q.startswith(unit + ".") for p, q in ran):
        return "kept"
    if path in RENDER_PATH or f"{path}::{unit}" in RENDER_PATH:
        return "kept"  # renders every kept map's page after the traced roll
    if (path, unit) in KIND_KEYS:
        return "kept" if KIND_KEYS[(path, unit)] in STRINGS_USED else "deferred"  # a Kind in use: a kept map records a feature under its key
    if unit == "<module>":
        # a module-level claim is judged by the knob it names (`<knob> forms|weights|range`), else by whether the module runs
        first = label.split(" ")[0]
        if first in knobs:
            return "kept"
        return "kept" if label and first not in KNOB_NAMES and any(p == path for p, _q in ran) else "deferred"
    if unit.replace("_", "").isupper():
        if unit in read or unit in KNOB_FEEDS:
            return "kept"
        knob = knob_of_constant(skill, path, unit) if skill else None
        return "kept" if knob and knob in knobs else "deferred"
    if unit[:1].isupper() and "." not in unit and unit in read:
        return "kept"  # a class executed code constructs or names
    return "deferred"


def main(argv: list[str]) -> int:
    skill, ranking, index, out_scope, out_deferred = (Path(a) for a in argv[1:6])
    ran = executed(skill)
    read = names_read(skill, ran)
    knobs = knobs_in_use(skill, ran)
    KNOB_NAMES.update(all_knob_names(skill))
    KIND_KEYS.update(kind_keys(skill))
    STRINGS_USED.update(strings_used(skill, ran, read))

    def judge(key: str) -> str:
        uid, label = key.rsplit("#", 1)
        return scope_of(uid, ran, read, knobs, skill, label)

    rows = json.loads(ranking.read_text())
    scope = {r["key"]: judge(r["key"]) for r in rows}
    out_scope.write_text(json.dumps(scope, indent=1, sort_keys=True) + "\n")
    keys = sorted(k for k in json.loads(index.read_text()) if k.split("::")[0].endswith(".py"))
    deferred_keys = {k for k in keys if judge(k) == "deferred"}
    uids = sorted({k.rsplit("#", 1)[0] for k in keys})
    deferred = [u for u in uids if all(k in deferred_keys for k in keys if k.rsplit("#", 1)[0] == u)]
    lone = sorted(k for k in deferred_keys if k.rsplit("#", 1)[0] not in set(deferred))
    doc = json.loads(out_deferred.read_text()) if out_deferred.is_file() else {}
    doc |= {"why": doc.get("why", "feature 328 amendment 8"), "units": deferred, "keys": lone}
    out_deferred.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(ran)} executed functions, {len(knobs)} knobs in use; open rows by scope:", {s: sum(1 for r in rows if not r["wave"] and scope[r["key"]] == s) for s in ("kept", "mode-a", "deferred")}, f"; {len(deferred)} of {len(uids)} claimed units deferred, {len(lone)} claims more")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
