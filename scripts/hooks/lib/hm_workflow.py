"""The Workflow guard's decider (feature 383 amendment 7, FR-045, plan D48). GUARD_EDIT_OK: feature 383 amendment 7 - a NEW
guard, the GM 2026-10-17: "please take a look at that and then implement its recommendations".

WHY. A wave of 4 or more checks of one type goes through a workflow (research R20: every hand-launched agent wakes the main
session when it finishes, 5,544 wakes a month re-reading a median 405k tokens; a workflow wakes it once). But NO PreToolUse or
PostToolUse Agent hook fires for an agent a workflow spawns (R20, a probe) - so a check run in a workflow would skip every guard
a hand launch meets: the model rule, the repeated block, the bundle and owed check, decide-first, the freeze, the round caps,
the review occasions, escalation. This guard closes that:

- a script whose `agent(` call names no `agentType` runs the workflow's default subagent, which loads every CLAUDE.md and every
  tool (~35k written at its first request against ~4k for a typed one): refused unless the script says `GP_OK: <reason>`;
  an untyped or ad-hoc call names its `model` either way, as an ad-hoc Agent call must (`agent-model-hooks.sh`);
- a script that calls a DEFINED agent of this project (`.claude/agents/<type>.md`) is refused with the `check-wave` call: its
  units can be held to the per-dispatch guards only when they are known before the run starts, as `check-wave`'s args are;
  likewise a script that calls `workflow('check-wave', ...)` with arguments computed at run time;
- `check-wave` itself: its `agentType` is one of the authorized wave jobs (WAVE_JOBS, the appended system prompt's list -
  `tests/test_agent_models.py` holds the two equal), and each unit is put through every PreToolUse `Agent` hook of the
  settings, in order, as the Agent payload a hand launch would send (`tool_use_id` `wave:<run>:<n>`, `L7R_WAVE_UNIT=1` so the
  wave count does not count it). The first refusal refuses the whole run, with that hook's message and the unit's label.

The check tracking pairs a wave unit's agent at SubagentStop by its prompt (`hm_checks`), since no PostToolUse gives its id.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

#: the jobs the appended system prompt authorizes a workflow for (FR-044): the GM's draft list, and the two triage agents that
#: replaced general-purpose waves. Not spec-fidelity: its round hook rewrites the prompt, which a workflow cannot carry.
WAVE_JOBS = (
    "source-applicability", "quote-check", "settlement-review", "entry-drift", "modal-depiction", "record-format",
    "impl-drift", "modal-research", "building-review", "source-reader", "glyph-check", "modal-form", "round-arbiter",
    "claims-triage", "modal-triage",
)
WAVE = "check-wave"
GP_ESCAPE = re.compile(r"GP_OK\s*[=:]\s*[\"']?\S+\s+\S+")


def calls(script: str, name: str = "agent") -> list[str]:
    """The text of each `name(...)` call in a script, its parentheses balanced (quotes and template strings skipped)."""
    out = []
    for m in re.finditer(rf"(?<![\w.$]){name}\s*\(", script):
        depth, i, quote = 1, m.end(), ""
        while i < len(script) and depth:
            c = script[i]
            if quote:
                if c == "\\":
                    i += 1
                elif c == quote:
                    quote = ""
            elif c in "'\"`":
                quote = c
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            i += 1
        out.append(script[m.start():i])
    return out


def agent_type(call: str) -> str | None:
    """A call's `agentType`: its literal, '?' when it is an expression, None when the call names none."""
    m = re.search(r"\bagentType\s*:\s*(?:(['\"`])([\w-]+)\1|(\S))", call)
    if not m:
        return None
    return m.group(2) or "?"


def defined(root: pathlib.Path) -> set[str]:
    return {p.stem for p in (root / ".claude" / "agents").glob("*.md")}


def script_verdict(script: str, root: pathlib.Path) -> str:
    """Why an inline or file script is refused, or ''."""
    if calls(script, "workflow") and any(re.search(r"['\"`]check-wave['\"`]", c) for c in calls(script, "workflow")):
        return "SCRIPT check-wave is run by name from the Workflow tool, its args written out, never from inside a script"
    gp, used = bool(GP_ESCAPE.search(script)), False
    ours = defined(root)
    for call in calls(script):
        kind = agent_type(call)
        if kind is None and not gp:
            return "UNTYPED " + call[:120].replace("\n", " ")
        used = used or kind is None
        if kind in ours or kind == "?":
            return f"GUARDED {kind}"
        if not re.search(r"\bmodel\s*:", call):
            return "MODEL " + call[:120].replace("\n", " ")
    return "ESCAPED" if used else ""


def agent_hooks(settings: pathlib.Path) -> list[str]:
    """The PreToolUse hook commands an Agent call meets, in order."""
    data = json.loads(settings.read_text(encoding="utf-8"))
    out = []
    for m in data.get("hooks", {}).get("PreToolUse", []):
        matcher = m.get("matcher") or ""
        if matcher and re.fullmatch(matcher, "Agent"):
            out.extend(h["command"] for h in m.get("hooks", []) if h.get("type", "command") == "command")
    return out


def run_id(payload: dict) -> str:
    return str(payload.get("tool_use_id") or hashlib.sha256(json.dumps(payload.get("tool_input"), sort_keys=True).encode()).hexdigest()[:12])


def wave_verdict(payload: dict, settings: pathlib.Path) -> str:
    """Why a `check-wave` run is refused, or '': its args' form, then each unit through the Agent hooks."""
    args = (payload.get("tool_input") or {}).get("args")
    if isinstance(args, str):
        return "ARGS args is a JSON string - pass the object itself: args: {agentType: ..., units: [...]}"
    if not isinstance(args, dict) or not isinstance(args.get("units"), list) or not args["units"]:
        return "ARGS check-wave needs args {agentType: \"<job>\", units: [{label, prompt}, ...]}"
    kind = str(args.get("agentType") or "")
    if kind not in WAVE_JOBS:
        return f"JOB `{kind}` is not an authorized wave job ({', '.join(WAVE_JOBS)})"
    hooks = agent_hooks(settings)
    env = {**os.environ, "L7R_WAVE_UNIT": "1"}
    run = run_id(payload)
    launches = []  # every prompt the run can launch: each unit, and each verify step it declares (FR-043)
    for n, u in enumerate(args["units"]):
        if not isinstance(u, dict) or not isinstance(u.get("prompt"), str) or not u.get("label"):
            return f"ARGS unit {n} needs a label and a prompt"
        launches.append((f"{n}", kind, u["prompt"], str(u["label"])))
        then = u.get("then") or []
        if not isinstance(then, list):
            return f"ARGS unit {u['label']}: then is a list of {{agentType, prompt}}"
        for k, step in enumerate(then):
            if not isinstance(step, dict) or not isinstance(step.get("prompt"), str) or str(step.get("agentType") or "") not in WAVE_JOBS:
                return f"ARGS unit {u['label']}: verify step {k} needs a prompt and an agentType among the wave jobs"
            launches.append((f"{n}.{k}", str(step["agentType"]), step["prompt"], f"{u['label']} / {step['agentType']}"))
    for tag, typ, prompt, label in launches:
        unit = {"session_id": payload.get("session_id"), "transcript_path": payload.get("transcript_path"), "cwd": payload.get("cwd"),
                "hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": f"wave:{run}:{tag}",
                "tool_input": {"subagent_type": typ, "prompt": prompt, "description": label, "run_in_background": True}}
        for cmd in hooks:
            r = subprocess.run(["bash", "-c", cmd], input=json.dumps(unit), capture_output=True, text=True, env=env, cwd=payload.get("cwd") or None, check=False)
            if r.returncode == 2:
                drop(payload, f"wave:{run}:")
                return f"UNIT {label}\n{r.stderr.strip()}"
    return ""


def drop(payload: dict, prefix: str) -> None:
    """A refused run launches nothing: its dispatches the check tracking already recorded go, so none freezes a page."""
    try:
        import hm_checks  # noqa: PLC0415 - a sibling in lib/, imported only when a run is refused

        hm_checks.drop_run(str(payload.get("cwd") or os.getcwd()), prefix)
    except Exception:  # noqa: BLE001, S110 - a stale pending dispatch expires by itself (WAVE_PENDING_S)
        pass


def verdict(payload: dict, root: pathlib.Path, settings: pathlib.Path) -> str:
    ti = payload.get("tool_input") or {}
    name, path = str(ti.get("name") or ""), str(ti.get("scriptPath") or "")
    wave_file = (root / ".claude" / "workflows" / f"{WAVE}.js").resolve()
    if name == WAVE or (path and pathlib.Path(path).resolve() == wave_file):
        return wave_verdict(payload, settings) or "WAVE-PASSED"
    if path:
        try:
            script = pathlib.Path(path).read_text(encoding="utf-8")
        except OSError:
            return ""
    elif name:
        f = root / ".claude" / "workflows" / f"{name}.js"
        script = f.read_text(encoding="utf-8") if f.is_file() else ""
    else:
        script = str(ti.get("script") or "")
    return script_verdict(script, root)


def main() -> int:
    root, settings = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("tool_name") != "Workflow":
        return 0
    got = verdict(payload, root, settings)
    if got:
        print(got)
    return 0


if __name__ == "__main__":
    sys.exit(main())
