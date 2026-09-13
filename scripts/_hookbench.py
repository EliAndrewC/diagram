#!/usr/bin/env python3
"""Replay a frozen window of real commands through a guard's decision, in process (feature 239 B).

    python3 scripts/_hookbench.py --refresh [DAYS]            freeze the window (FR-004)
    python3 scripts/_hookbench.py GUARD                       verdict counts, in process (FR-005)
    python3 scripts/_hookbench.py GUARD --against REF         the verdict diff against REF (FR-006)

`make hookbench GUARD=<name> [AGAINST=<ref>] [REFRESH=1]` is the entry.

WHY IT EXISTS. Measuring a guard over the commands it really sees used to mean spawning the hook per
command - 144 ms each against 7.0 ms called in process, 80 s against 3.9 s over one window
(`specs/239-*/research.md` R3) - and rebuilding the window from the transcripts every time a question
changed. Feature 236's exemption needed nine such passes, and two drafts of it passed their own cases
while changing eleven real verdicts for the worse: the verdict diff over the window is the check it
owed and did not have.

THE GUARD UNDER TEST MUST BE IMPORTABLE (FR-007): a guard whose decision is still a program inside a
shell string is refused by name rather than silently spawned, because a fallback would make the cost
invisible again. A BASELINE at an old ref is different (plan P1): the ref may predate any importable
decision, so it is evaluated in a child - one process for the whole window when the ref has the
function, one spawn per command when it does not - and the output says which, with the time it took.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
DASHES = chr(0x2014) + chr(0x2013)   # by codepoint: literal ones were corrected by the very hook measured

#: guard name -> (module, function). A guard absent from here has no importable decision yet.
DECISIONS = {"house-style": ("_hm_house", "report")}


# ---- the corpus (FR-004) --------------------------------------------------------------------------------

def word_pattern() -> re.Pattern[str]:
    """The decision's own table, imported - never a copy, which the hook would correct as it was saved."""
    sys.path.insert(0, str(HERE))
    from _hm_house import BRIT
    return re.compile(r"\b(" + "|".join(BRIT) + r")\b|[" + DASHES + "]", re.I)


def window_commands(days: float, projects: pathlib.Path | None = None) -> list[str]:
    """Every unique Bash command in the last DAYS days of transcripts carrying a spelling or a dash."""
    cutoff, seen, out = time.time() - days * 86400, set(), []
    pattern = word_pattern()
    for path in (projects or pathlib.Path.home() / ".claude" / "projects").glob("*/**/*.jsonl"):
        try:
            if path.stat().st_mtime < cutoff:
                continue
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if '"Bash"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            for c in (rec.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Bash":
                    cmd = (c.get("input") or {}).get("command") or ""
                    if cmd and cmd not in seen and pattern.search(cmd):
                        seen.add(cmd)
                        out.append(cmd)
    return out


def refresh(days: float, out_dir: pathlib.Path = FIXTURES, projects: pathlib.Path | None = None) -> pathlib.Path:
    today = datetime.date.today().isoformat()
    cmds = window_commands(days, projects)
    out = out_dir / f"command-window-{today}.json"
    out.write_text(json.dumps({"taken": today, "days": days, "built_by": "make hookbench REFRESH=1",
                               "what": "every unique Bash command in the window carrying a British "
                                       "spelling or a forbidden dash", "commands": cmds}, indent=1) + "\n")
    return out


def latest_corpus(fixtures: pathlib.Path = FIXTURES) -> pathlib.Path:
    found = sorted(fixtures.glob("command-window-*.json"))
    if not found:
        raise SystemExit("hookbench: no frozen corpus in scripts/fixtures/ - run `make hookbench REFRESH=1` first")
    return found[-1]


# ---- verdicts (FR-005) ----------------------------------------------------------------------------------

def classify(report: str, blocked: bool = False) -> str:
    """silent | corrected | reported | blocked, from what a decision printed."""
    if blocked:
        return "blocked"
    if not report.strip():
        return "silent"
    if report.lstrip().startswith("{"):
        return "corrected" if '"updatedInput"' in report else "reported"
    return "blocked"


def payload(cmd: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def decision(guard: str, scripts: pathlib.Path = HERE):
    """The guard's importable decision, or a refusal naming FR-001 (FR-007)."""
    if guard not in DECISIONS:
        raise SystemExit(f"hookbench: `{guard}` has no importable decision - its program still lives inside "
                         f"its shell file, and spawning it per command is exactly the cost this bench exists "
                         f"to remove. Lift the decision into a module first (feature 239 FR-001), then name "
                         f"it in DECISIONS.")
    module, func = DECISIONS[guard]
    sys.path.insert(0, str(scripts))
    return getattr(__import__(module), func)


def verdicts_in_process(guard: str, cmds: list[str], scripts: pathlib.Path = HERE) -> list[str]:
    decide = decision(guard, scripts)
    return [classify(decide(payload(c))) for c in cmds]


# ---- a baseline at a ref (FR-006, plan P1) --------------------------------------------------------------

def verdicts_at(ref: str, guard: str, cmds: list[str]) -> tuple[list[str], str]:
    """Verdicts from the guard as it stood at REF, and how they were obtained."""
    with tempfile.TemporaryDirectory() as td:
        tree = pathlib.Path(td)
        archive = subprocess.run(["git", "-C", str(ROOT), "archive", ref, "scripts"], capture_output=True)
        if archive.returncode:
            raise SystemExit(f"hookbench: cannot read scripts/ at {ref}: {archive.stderr.decode()[:200]}")
        subprocess.run(["tar", "-x", "-C", str(tree)], input=archive.stdout, check=True)
        scripts = tree / "scripts"
        module, func = DECISIONS.get(guard, ("", ""))
        mod_file = scripts / f"{module}.py"
        if module and mod_file.is_file() and re.search(rf"^def {func}\(", mod_file.read_text(), re.M):
            corpus = tree / "corpus.json"
            corpus.write_text(json.dumps(cmds))
            child = subprocess.run([sys.executable, str(HERE / "_hookbench.py"), "_child", guard, str(scripts),
                                    str(corpus)], capture_output=True, text=True)
            if child.returncode:
                raise SystemExit(f"hookbench: the decision at {ref} failed: {child.stderr[-300:]}")
            return json.loads(child.stdout), f"imported in one child process from {ref}"
        hook = scripts / f"{guard}-hooks.sh"
        env = dict(os.environ, GUARD_LOG_DIR=str(tree / "log"))
        began, out = time.time(), []
        for c in cmds:
            p = subprocess.run([str(hook), "pretool"], input=json.dumps(payload(c)), capture_output=True,
                               text=True, env=env)
            out.append(classify(p.stdout, blocked=p.returncode == 2))
        return out, (f"SPAWNED per command from {ref} - its decision is not importable, so this took "
                     f"{time.time() - began:.0f} s where the guard under test took seconds")


def diff(cmds: list[str], before: list[str], after: list[str]) -> list[tuple[str, str, str]]:
    return [(b, a, c) for c, b, a in zip(cmds, before, after) if a != b]


# ---- the command line -----------------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if argv[:1] == ["_child"]:
        guard, scripts, corpus = argv[1], pathlib.Path(argv[2]), pathlib.Path(argv[3])
        print(json.dumps(verdicts_in_process(guard, json.loads(corpus.read_text()), scripts)))
        return 0
    if "--refresh" in argv:
        days = next((float(a) for a in argv if re.fullmatch(r"\d+(\.\d+)?", a)), 14.0)
        out = refresh(days)
        print(f"hookbench: froze {len(json.loads(out.read_text())['commands'])} commands into {out.relative_to(ROOT)}")
        return 0
    guard = next((a for a in argv if not a.startswith("-")), None)
    if not guard:
        raise SystemExit("hookbench: name a GUARD (e.g. house-style), or pass --refresh")
    against = argv[argv.index("--against") + 1] if "--against" in argv else None
    corpus = latest_corpus()
    cmds = json.loads(corpus.read_text())["commands"]
    began = time.time()
    now = verdicts_in_process(guard, cmds)
    took = time.time() - began
    counts = {v: now.count(v) for v in ("corrected", "reported", "silent", "blocked")}
    print(f"hookbench {guard}: {len(cmds)} commands from {corpus.name}, in process in {took:.1f} s")
    print("  " + "  ".join(f"{k} {v}" for k, v in counts.items()))
    if against:
        before, how = verdicts_at(against, guard, cmds)
        changed = diff(cmds, before, now)
        print(f"\nverdict diff against {against} ({how}): {len(changed)} changed")
        moves: dict[str, int] = {}
        for b, a, _ in changed:
            moves[f"{b} -> {a}"] = moves.get(f"{b} -> {a}", 0) + 1
        for move, n in sorted(moves.items(), key=lambda kv: -kv[1]):
            print(f"  {n:4d}  {move}")
        sys.path.insert(0, str(HERE))
        from _hm_house import write_targets
        for b, a, c in changed[:25]:
            print(f"  [{b} -> {a}] targets={write_targets(c)[:3]} :: {c.strip().splitlines()[0][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
