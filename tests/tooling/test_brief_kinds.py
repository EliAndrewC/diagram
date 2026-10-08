"""Feature 250's `brief.py` declares a page-load kind on every brief it makes (feature 274 D7, FR-001, SC-001).

WHY. The page-session runner counts the questions a brief assigns and refuses a write brief over four. `brief.py`
makes no group-writing briefs: its page briefs are `assertions`, its 2a/2b check briefs and owed-modal briefs `check`,
its split briefs `split`. Each template is rendered as `brief.py` renders it, and the kind it declares is read back
with the runner's own helper; every `.format` of a template that takes the kind is found in the source and must pass
the right one, so a new call site that forgets it fails here rather than at a launch.
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import string

REPO = pathlib.Path(__file__).resolve().parents[5]
BRIEF = REPO / "specs" / "250-close-the-record-checks" / "measure" / "brief.py"


def _load(name: str, path: pathlib.Path):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


brief = _load("brief_250", BRIEF)
bl = _load("_brief_load", REPO / "scripts" / "_brief_load.py")
WANT = {"WRITE": "assertions", "CHECK": "check", "SPLIT": "split", "OWED": "check"}


def _render(template: str, kind: str) -> str:
    fields = {f for _, f, _, _ in string.Formatter().parse(template) if f}
    return template.format(**{f: 0 if f == "size" else "x" for f in fields} | ({"kind": kind} if "kind" in fields else {}))


def test_every_template_declares_its_kind_and_the_runner_reads_it() -> None:
    for name, kind in WANT.items():
        text = _render(getattr(brief, name), kind)
        assert bl.declared(text) == kind, name
        assert bl.refusal(pathlib.Path(f"{name}.md"), text, REPO / ".claude/skills/diagram/research") == "", name


def test_every_call_site_passes_the_right_kind() -> None:
    calls = [
        n
        for n in ast.walk(ast.parse(BRIEF.read_text(encoding="utf-8")))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "format" and isinstance(n.func.value, ast.Name) and n.func.value.id in WANT
    ]
    assert {c.func.value.id for c in calls} == set(WANT), "every template is written somewhere"  # type: ignore[attr-defined]
    for c in calls:
        name = c.func.value.id  # type: ignore[attr-defined]
        given = {k.arg: k.value.value for k in c.keywords if k.arg == "kind" and isinstance(k.value, ast.Constant)}
        if "{kind}" in getattr(brief, name):
            assert given == {"kind": WANT[name]}, f"{name}.format must pass kind={WANT[name]!r}"
        else:
            assert f"kind={WANT[name]}" in getattr(brief, name), name
