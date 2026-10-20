"""`scripts/measure/fix_yield.py` and `hm_arbiter.fix_measure_of` - each tooling fix's yield (feature 385 T119; feature 406 D165).

The GM, 2026-10-19 (amendment 10, change 3): each fix's yield measured, so a fix that saves nothing is retired; then (feature
406): "Whether or not it's doing something for us should be a measurable question" - each fix read by its tools' numbers since
it was made (D165), in D166's order.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "measure"))
sys.path.insert(0, str(REPO / "scripts" / "reviews"))
sys.path.insert(0, str(REPO / "scripts" / "hooks" / "lib"))
import fix_yield as fy  # noqa: E402
import hm_arbiter as ha  # noqa: E402
import tool_yield as ty  # noqa: E402

T0 = datetime.datetime(2026, 10, 19, tzinfo=datetime.UTC).timestamp()


def _iso(t: float) -> str:
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tool(kind: str, name: str, first: float, uses: tuple = (), hits: tuple = (), misses: tuple = (), recorded: bool = True) -> ty.Tally:
    t = ty.Tally(kind, name, outcome_record=recorded)
    for u in uses:
        t.use(u)
    t.first = first
    for h in hits:
        t.hit(h)
    for m in misses:
        t.miss(m)
    return t


DONE = {"trigger": "hour:x@1", "tooling_fix": "f", "fix_minutes": 12, "status": "done", "settled": _iso(T0)}
NOW = T0 + 30 * 86400


def test_each_reading_in_d166_s_order() -> None:
    """D166: too new to say, doing something, no outcome record, record too new, doing nothing - the first that holds."""
    old = T0 - 20 * 86400
    busy = _tool("guard", "g", old, uses=(T0 + 10,), hits=(T0 + 10,))
    idle = _tool("guard", "h", old, uses=(T0 + 10,))
    before = _tool("guard", "b", old, uses=(T0 - 10,), hits=(T0 - 10,))  # interventions before the fix do not count
    misfire = _tool("review", "r", old, uses=(T0 + 10,), hits=(T0 + 10,), misses=(T0 + 20,))
    blind = _tool("check", "c", 0.0, recorded=False)
    fresh = _tool("check", "n", NOW - 86400, uses=(NOW - 86400,))
    assert fy.verdict(DONE, {("guard", "g"): busy}, T0 + 86400)["reading"] == "too new to say"
    assert fy.verdict(DONE, {("guard", "g"): busy, ("check", "c"): blind}, NOW)["reading"] == "doing something"
    assert fy.verdict(DONE, {("guard", "h"): idle, ("check", "c"): blind}, NOW)["reading"] == "no outcome record"
    assert fy.verdict(DONE, {}, NOW)["reading"].startswith("no outcome record (no tool found")
    assert fy.verdict(DONE, {("guard", "h"): idle, ("check", "n"): fresh}, NOW)["reading"] == "record too new"
    assert fy.verdict(DONE, {("guard", "h"): idle, ("guard", "b"): before}, NOW)["reading"] == "doing nothing"
    assert fy.verdict(DONE, {("review", "r"): misfire}, NOW)["reading"] == "doing nothing", "an intervention net of its misfire is none"
    assert fy.verdict({**DONE, "status": "declined"}, {}, NOW)["reading"] == "not made (declined)"


def test_the_table_cites_each_tool_s_numbers_since_the_fix() -> None:
    tools = {
        ("guard", "g"): _tool("guard", "g", T0 - 86400, uses=(T0 - 5, T0 + 5, T0 + 6), hits=(T0 + 5,)),
        ("check", "c"): _tool("check", "c", 0.0, recorded=False),
    }
    out = fy.table([fy.verdict(DONE, tools, NOW)])
    assert "| hour:x@1 | 2026-10-19 | 12 | doing something |" in out
    assert "guard g (first seen 2026-10-18): 2 / 1 / 0" in out and "check c (first seen -): no outcome record" in out


def test_fixes_pairs_each_ruling_with_its_settling() -> None:
    rows = [
        {"trigger": "a", "tooling_fix": "fa", "utc": "u1"},
        {"trigger": "b", "tooling_fix": "fb", "fix_minutes": 3, "utc": "u2"},
        {"trigger": "c", "ruling": "continue"},
        {"fix_of": "a", "status": "done", "utc": "u3", "note": "abc1234: made"},
    ]
    got = {f["trigger"]: f for f in fy.fixes(rows)}
    assert set(got) == {"a", "b"}
    assert got["a"]["status"] == "done" and got["a"]["settled"] == "u3" and got["a"]["note"] == "abc1234: made"
    assert got["b"]["status"] == "open"


def test_a_fix_s_tools_come_from_its_settling_commit(tmp_path: pathlib.Path) -> None:
    root = tmp_path
    (root / ".claude").mkdir()
    hook = "scripts/hooks/" + "foo-hooks.sh"
    (root / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"command": hook + " pretool"}]}]}}))
    (root / "scripts" / "hooks").mkdir(parents=True)
    (root / "scripts" / "gates").mkdir()
    (root / "Makefile").write_text("done:\n\t@true\nquick:\n\t@true\ntick:\n\t@true\nthing:\n\t@python3 scripts/gates/x.py\n")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "base"], check=True)
    (root / hook).write_text("guard_log foo blocked\n")
    (root / "scripts" / "gates" / "x.py").write_text('if __name__ == "__main__":\n    pass\n')
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "the fix for hour:x@1"], check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    want = {("guard", "foo"), ("check", "x"), ("target", "thing")}
    assert fy.tools_of_fix(root, {"trigger": "hour:x@1", "note": ""}) == want, "found by the commit naming its trigger"
    assert fy.tools_of_fix(root, {"trigger": "other", "note": f"{sha}: made"}) == want, "found by the note's leading hash"
    assert fy.tools_of_fix(root, {"trigger": "nowhere", "note": "no hash"}) == set()
    # a landing carrying it and other files, and a later fix whose trigger starts the same, are not its commit
    (root / "scripts" / "gates" / "y.py").write_text('if __name__ == "__main__":\n    pass\n')
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "Tooling from clone, landed alone\n\nhour:x@1 and more"], check=True)
    (root / "scripts" / "gates" / "z.py").write_text('if __name__ == "__main__":\n    pass\n')
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "the fix for hour:x@10"], check=True)
    assert fy.tools_of_fix(root, {"trigger": "hour:x@1", "note": ""}) == want, "not @10, and the clone's commit before its landing"
    assert fy.tools_of_fix(root, {"trigger": "hour:x@10", "note": ""}) == {("check", "z")}
    assert fy.tools_of_fix(root, {"trigger": "hour:x@1", "note": "", "settled": "2000-01-01T00:00:00Z"}) == set(), "nothing after its settling"
    assert fy.tools_of_fix(root, {"trigger": "unnamed", "note": "", "test": "scripts/gates/z.py"}) == {("check", "z")}, "by its test file"


def test_the_report_reads_the_feature_s_record(tmp_path: pathlib.Path) -> None:
    d = tmp_path / "specs" / "385-x"
    d.mkdir(parents=True)
    assert fy.report(tmp_path, d) == "(no tooling fix ruled)\n"


def test_a_ruling_naming_a_fix_is_refused_without_its_cost() -> None:
    """D139 kept by D165: the cost a fix was ruled for stands beside its tools' numbers; the retired measure is not asked."""
    for bad in ({}, {"fix_measure": "make x"}, {"fix_minutes": "ten"}, {"fix_minutes": -1}):
        with pytest.raises(ValueError, match="fix_minutes"):
            ha.fix_measure_of(bad)
    assert ha.fix_measure_of({"fix_minutes": "12"}) == {"fix_minutes": 12.0}
