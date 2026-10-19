"""A task whose change is wording alone owes no plan review; the tick checks that it was (feature 385 T118, D137/D138).

WHY (the GM 2026-10-19, amendment 10: "I would also like to implement all 3 of your suggestions" - the third, "skip the plan
review for wording-only tasks that decide nothing new"). The wording-only tasks of that morning (T31, T103, T105, T110) took 5-12
min tick to tick, each paying a spec-fidelity plan review of 1-3 agent-minutes besides `make decide`, the dispatch and the verdict.

A task's Decisions block holding `**Wording only.** <what is reworded>` and no `**D<n> - ` line declares it (`wording_only`); the
plan gate skips that section's blocks but its part Bs, and `make tick` refuses it when a commit since its `make task-start` changed
anything but the feature's records, a glossary entry, or a `.py` file outside what runs (`refusal`).
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
WORDING = "**Wording only.**"
_DECISIONS = re.compile(r"^#{3,4}\s+T\d+[a-z]?\s+Decisions\s*$", re.M)
_NEXT_HEAD = re.compile(r"^#{2,4}\s", re.M)
_DECISION = re.compile(r"^\*\*D\d+[a-z]?\s+-\s", re.M)
#: what a wording-only task may change beside `.py` comments, docstrings and claims: its feature's records, the run records, and a
#: glossary entry (a word's definition, which the page check reads)
_FREE = re.compile(r"^(specs/|dev/|l7r/diagram/interactive/assets/glossary/[^/]+\.json$)")


def wording_only(section: str) -> bool:
    """Does the task section's Decisions block declare wording only, with no decision beside it (D137)?"""
    m = _DECISIONS.search(section)
    if not m:
        return False
    body = section[m.end() :]
    if nxt := _NEXT_HEAD.search(body):
        body = body[: nxt.start()]
    return WORDING in body and not _DECISION.search(body)


def _semantic():  # noqa: ANN202 - gate-stamp.py by path (its name has a hyphen): the one definition of "changed in what runs"
    spec = importlib.util.spec_from_file_location("gate_stamp", HERE / "gate-stamp.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.semantic_bytes


def _git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True)


def started(root: pathlib.Path, feature: str, task: str) -> str:
    """The UTC of the task's last `make task-start`, from `task-starts.jsonl`; "" when it has none."""
    common = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.decode().strip()
    log = pathlib.Path(common, "task-starts.jsonl") if common else None
    last = ""
    for line in log.read_text(encoding="utf-8").splitlines() if log and log.is_file() else []:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("feature") == feature and row.get("task") == task:
            last = row.get("utc", "")
    return last


def changed_in_what_runs(root: pathlib.Path, since: str) -> list[str]:
    """Every file a commit since `since` (merges skipped: main's work is not the task's) changed beyond wording (D138)."""
    semantic = _semantic()
    out: list[str] = []
    for c in _git(root, "rev-list", "--no-merges", f"--since={since}", "HEAD").stdout.decode().split():
        for f in _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", c).stdout.decode().splitlines():
            if not f or f in out or _FREE.match(f):
                continue
            if f.endswith(".py"):
                before, after = _git(root, "show", f"{c}^:{f}"), _git(root, "show", f"{c}:{f}")
                if before.returncode == 0 and after.returncode == 0 and semantic(before.stdout, f) == semantic(after.stdout, f):
                    continue
            out.append(f)
    return out


def refusal(root: pathlib.Path, spec_dir: pathlib.Path, task: str, section: str | None) -> str:
    """Why a wording-only task may not tick: a commit since its start changed a file beyond wording; "" otherwise (D138)."""
    if section is None or not wording_only(section):
        return ""
    since = started(root, spec_dir.name, task)
    if not since:
        return f"{task}'s section says wording only, but it has no `make task-start` to read its commits from - start it, then tick"
    off = changed_in_what_runs(root, since)
    return f"{task}'s section says wording only, but {off[0]} changed in what runs - write its decision (`**D<n> - `) in place of the `{WORDING}` line and `make decide`" if off else ""
