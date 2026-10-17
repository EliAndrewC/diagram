"""Every subagent check runs on the tier recorded for it: a model AND an effort, pinned in its file.

THE RULING (GM 2026-09-19, feature 251). Judgment stays on Opus; what is purely mechanical is a script and
runs on no model (`make quote-verbatim`, `make record-prepass`, `make size-table`); and a DOWNGRADE stands
only after it is run on artifacts with known findings. The GM-approved proposal put `record-format` and
`source-reader` on Sonnet and the later-round twin at medium effort; all three MISSED findings the recorded
Opus runs had caught and went back up, and `quote-check`, `entry-drift` and `escalation-check` held at medium
(`specs/251-tiered-subagent-checks/research.md` R5). `sonnet` stays a legal value for the day a seeded run
supports it.

WHAT NEVER CHANGES. Nothing is inherited. An agent file with no `model:` runs on the SESSION's model,
which is how nineteen settlement reviews ran on Fable while that file said `inherit` (research R1), and a
file with no `effort:` runs at the session's effort (R6). So both keys are owed by every file, and this
test derives the roster from the directory: a new agent owes its tier here the day it lands.

WHAT A DEFINED AGENT IS NOT HANDED (GM 2026-09-19, feature 256). *"If there's something that a subagent should know,
it should be in the subagent specification."* Every file here carries `omitClaudeMd: true` except the one
`KEEPS_CLAUDE_MD` names below, so the agent launches without the root `CLAUDE.md`, the nested ones and the session's
memory index (measured: a first turn of 55-63 k tokens
fell to 8-12 k and nothing recorded was missed - `specs/256-defined-subagents-without-claude-md/research.md`). The
GM asked for this to be enforced by a test (2026-09-20), and the roster is derived from the directory, so a new agent
owes the field the day it lands - and owes its contract every project rule its job depends on. An
exception is a measured case the GM approved, in `KEEPS_CLAUDE_MD`, never a session's own call.

TO CHANGE A TIER: change the row here and the frontmatter together, and record why - for a downgrade,
the seeded-fault runs that justify it, THREE A LEG (GM 2026-09-21). One run does not settle it: feature
256 measured both legs of most pairs catching what the other missed, so a single MISS may be variance
and a single HIT may be luck. The doctrine, and why three is inherited from 256 rather than measured,
is in `docs/spec-kit-and-reviews.md`.
"""

from __future__ import annotations

import pathlib
import re

AGENTS = pathlib.Path(__file__).resolve().parents[1] / ".claude" / "agents"

MODELS = ("opus", "sonnet")
EFFORTS = ("low", "medium", "high", "xhigh", "max")

#: agent -> (model, effort)
TIERS: dict[str, tuple[str, str]] = {
    "record-format": ("opus", "medium"),  # Sonnet missed at medium (R5) and at high (R7); opus/medium hit everything
    "source-reader": ("opus", "high"),  # Sonnet tried and missed: research R5
    "quote-check": ("opus", "medium"),
    "entry-drift": ("opus", "medium"),
    "record-style": ("opus", "high"),
    "translation-check": ("opus", "medium"),  # feature 292: judgment of meaning; no seeded downgrade run yet
    "intro-check": ("opus", "medium"),  # feature 311: judgment about a reader; seeded runs on Opus only (plan D4)
    "impl-drift": ("opus", "medium"),  # feature 316; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "modal-form": ("opus", "medium"),  # feature 319; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "modal-research": ("opus", "medium"),  # feature 319; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "modal-depiction": ("opus", "medium"),  # feature 319 D13; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "escalation-check": ("opus", "medium"),
    "round-arbiter": ("opus", "high"),  # feature 375 FR-011: judges a process in the GM's place at a round cap; binding
    "spec-fidelity-verify": ("opus", "high"),  # medium tried and missed: research R5
    "spec-fidelity": ("opus", "high"),  # Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "source-applicability": ("opus", "high"),
    "size-audit": ("opus", "high"),
    "building-review": ("opus", "high"),  # Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "settlement-review": ("sonnet", "high"),  # feature 294 T34: Opus + 3/3 Sonnet found the seeded re-skin
    "glyph-check": ("opus", "high"),  # feature 294; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    "fix-check": ("sonnet", "high"),  # feature 294: the GM-complaint fix check; T34: Opus + 3/3 Sonnet found the unfired fix
    "perf-audit": ("opus", "high"),
    "claims-triage": ("opus", "medium"),  # 383 amendment 6: impl-drift's question pre-sorted, a judgment; was ad hoc on opus
    "modal-triage": ("opus", "medium"),  # 383 amendment 6: the pop-up checks' question pre-sorted, a judgment; was ad hoc on opus
    "research-pass": ("opus", "medium"),  # 383 amendment 6: a search pass judges what a source attests; was ad hoc
    "source-filter": ("opus", "medium"),  # feature 312: judges a source with no question in hand; calibrated three runs a leg (R2)
}


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    assert m, "no YAML frontmatter"
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)}


def _pinned() -> dict[str, dict[str, str]]:
    return {p.stem: frontmatter(p.read_text(encoding="utf-8")) for p in sorted(AGENTS.glob("*.md"))}


def test_the_agents_directory_was_found() -> None:
    assert len(_pinned()) >= 11, "non-vacuity: the roster is derived from the directory"


def test_every_agent_file_has_a_tier_and_every_tier_has_a_file() -> None:
    files, table = set(_pinned()), set(TIERS)
    assert not files - table, f"agent files with no recorded tier - add a row to TIERS: {sorted(files - table)}"
    assert not table - files, f"tiers recorded for agents that do not exist: {sorted(table - files)}"


def test_no_agent_inherits_its_model() -> None:
    wrong = {a: fm.get("model", "<missing>") for a, fm in _pinned().items() if fm.get("model") not in MODELS}
    assert not wrong, f"a check runs on opus or sonnet, pinned - never inherit, never absent, never fable: {wrong}"


def test_no_agent_inherits_its_effort() -> None:
    wrong = {a: fm.get("effort", "<missing>") for a, fm in _pinned().items() if fm.get("effort") not in EFFORTS}
    assert not wrong, f"a check pins its effort ({', '.join(EFFORTS)}) - an absent one is the session's: {wrong}"


def test_every_agent_file_agrees_with_the_tier_table() -> None:
    pinned = _pinned()
    wrong = {a: (pinned[a].get("model"), pinned[a].get("effort")) for a in TIERS if a in pinned and (pinned[a].get("model"), pinned[a].get("effort")) != TIERS[a]}
    assert not wrong, f"frontmatter disagrees with TIERS (file says -> table says): { {a: (v, TIERS[a]) for a, v in wrong.items()} }"


#: agent -> why it KEEPS the CLAUDE.md files. An entry here is a MEASURED case the GM approved, never a session's
#: convenience: the session shows what the field cost that check on recorded findings and recommends, the GM answers,
#: and the row quotes both. Nothing goes in here on a session's own authority.
KEEPS_CLAUDE_MD: dict[str, str] = {}
# EMPTY since feature 383 amendment 6 (the GM 2026-10-17: what subagents share belongs in their system prompt): `spec-fidelity`
# kept the files from 2026-09-20 until the run its row asked for - feature 251's round-1 spec, three runs a leg with and
# without, scored blind by an independent reader - found every recorded item without them (specs/383 research R14). The files
# cost it ~22k tokens written fresh at every dispatch (research R13).


def test_every_agent_launches_without_the_claude_md_files() -> None:
    pinned = _pinned()
    wrong = sorted(a for a, fm in pinned.items() if a not in KEEPS_CLAUDE_MD and fm.get("omitClaudeMd") != "true")
    stale = sorted(a for a in KEEPS_CLAUDE_MD if a not in pinned or pinned[a].get("omitClaudeMd") == "true")
    assert not stale, f"KEEPS_CLAUDE_MD names an agent that is gone or that carries the field after all - drop the row: {stale}"
    assert not wrong, (
        f"a defined agent carries `omitClaudeMd: true` in its frontmatter (feature 256, GM 2026-09-19: what a subagent "
        f"should know belongs in its own specification, not in CLAUDE.md or the memory index) - missing in: {wrong}. "
        f"Add the field, and write into the contract each project rule the check's job depends on."
    )


def test_the_tier_table_itself_is_well_formed() -> None:
    assert all(m in MODELS and e in EFFORTS for m, e in TIERS.values())


def test_frontmatter_reads_both_keys_and_refuses_a_file_without_any() -> None:
    assert frontmatter("---\nname: x\nmodel: opus\neffort: high\n---\nbody") == {"name": "x", "model": "opus", "effort": "high"}
    try:
        frontmatter("no frontmatter here")
    except AssertionError:
        return
    raise AssertionError("a file with no frontmatter must fail")  # pragma: no cover


#: the settings that would put subagents on the 1-hour prompt cache (feature 383 amendment 6, FR-038): it doubles the price of
#: every write a subagent makes in its whole run to keep a few-thousand-token prefix warm; the default 5 minutes covers a fan-out
_HOUR_TTL = re.compile(r"""(?:cacheTtl|CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL)["']?\s*[:=]\s*["']?(?:1h|60m|3600)""", re.I)


def _ttl_sources(root: pathlib.Path) -> list[pathlib.Path]:
    return [
        p
        for p in [
            root / ".claude" / "settings.json",
            root / ".claude" / "settings.local.json",
            *sorted((root / ".claude" / "agents").glob("*.md")),
            *sorted((root / "scripts" / "container").glob("*")),
        ]
        if p.is_file()
    ]


def hour_ttl(paths: list[pathlib.Path]) -> list[str]:
    return [str(p) for p in paths if _HOUR_TTL.search(p.read_text(encoding="utf-8", errors="replace"))]


def test_no_setting_puts_subagents_on_the_hour_long_cache(tmp_path: pathlib.Path) -> None:
    assert hour_ttl(_ttl_sources(AGENTS.parents[1])) == [], "a 1-hour subagent cache doubles every write a subagent makes - remove it (feature 383 FR-038)"
    seeded = tmp_path / "settings.json"
    seeded.write_text('{"env": {"CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL": "1h"}, "experimental": {"cacheTtl": "1h"}}', encoding="utf-8")
    assert hour_ttl([seeded]) == [str(seeded)], "the check finds a seeded 1-hour setting"


# Feature 383 amendment 7 (FR-044, SC-032; plan D49): the appended system prompt authorizes Workflow for the named wave jobs
# only. Claude Code's default prompt says to call Workflow only on the user's explicit request, and outranks CLAUDE.md - without
# this text a session keeps hand-launching waves, each agent waking the main session once (research R20).
#: the GM's draft list (diagram-fanout-workflows.md, recommendation 2); the authorization may add only agents that replaced
#: general-purpose waves (the two triage agents, amendment 6)
DRAFT_JOBS = {
    "source-applicability",
    "quote-check",
    "settlement-review",
    "entry-drift",
    "modal-depiction",
    "record-format",
    "impl-drift",
    "modal-research",
    "building-review",
    "source-reader",
    "glyph-check",
    "modal-form",
    "round-arbiter",
}
REPLACED_GP = {"claims-triage", "modal-triage"}
ROOT = AGENTS.parents[1]


def wave_jobs(text: str) -> list[str] | None:
    """The jobs the authorization names (its WAVE JOBS list), or None when the authorization is missing."""
    if "Workflow is pre-authorized for recurring waves of typed agents" not in text or "check-wave" not in text:
        return None
    m = re.search(r"WAVE JOBS:(.*?) - run them", text, re.S)
    return re.findall(r"`([\w-]+)`", m.group(1)) if m else None


def wave_problems(text: str, defined: set[str], decider: tuple[str, ...]) -> list[str]:
    jobs = wave_jobs(text)
    if jobs is None:
        return ["the Workflow authorization is missing from scripts/container/append-system-prompt.md"]
    out = [f"{j}: no .claude/agents/{j}.md" for j in jobs if j not in defined]
    out += [f"{j}: not a wave job (the GM's draft list, or an agent that replaced a general-purpose wave)" for j in jobs if j not in DRAFT_JOBS | REPLACED_GP]
    if set(jobs) != set(decider):
        out.append(f"the authorization and hm_workflow.WAVE_JOBS disagree: {sorted(set(jobs) ^ set(decider))}")
    return out


def _wave_decider() -> tuple[str, ...]:
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("hm_workflow", ROOT / "scripts" / "hooks" / "lib" / "hm_workflow.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.WAVE_JOBS


def test_the_workflow_authorization_names_only_defined_wave_jobs() -> None:
    text = (ROOT / "scripts" / "container" / "append-system-prompt.md").read_text(encoding="utf-8")
    defined, decider = set(_pinned()), _wave_decider()
    assert wave_problems(text, defined, decider) == []
    assert set(wave_jobs(text) or []) >= DRAFT_JOBS, "every job of the GM's draft is authorized"
    assert wave_problems("no such text", defined, decider) == ["the Workflow authorization is missing from scripts/container/append-system-prompt.md"]
    seeded = text.replace("`modal-triage`", "`modal-triage`, `no-such-agent`, `escalation-check`")
    found = wave_problems(seeded, defined, decider)
    assert any("no-such-agent: no .claude/agents" in f for f in found), "an agent with no file is caught"
    assert any("escalation-check: not a wave job" in f for f in found), "a job outside the list is caught"


def test_check_wave_types_every_agent_and_carries_its_follow_up() -> None:
    """Plan D47 (FR-043): the saved workflow types every agent() call from its args, returns a schema object, re-launches a
    unit that came back null once, and runs each declared verify step after its unit with the reply appended."""
    js = (ROOT / ".claude" / "workflows" / "check-wave.js").read_text(encoding="utf-8")
    assert "name: 'check-wave'" in js and "args.units" in js and "args.agentType" in js
    assert re.search(r"agent\(prompt, \{ agentType: type, label, phase, schema: REPLY \}\)", js), "every agent() typed, with the schema"
    assert len(re.findall(r"(?<![\w.])agent\(", js)) == 1, "one agent() call, the typed one"
    assert "required: ['label', 'verdict', 'text']" in js
    assert "(got, u) => got || run(args.agentType, u.prompt, u.label, 'Checks')" in js, "a null unit re-launched once"
    assert "u.then" in js and "check before you:" in js, "declared verify steps, the reply appended"
