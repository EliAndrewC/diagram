"""The VerificationState: the most recent verification event, per clone (FR-012, research R6).

`.git/verification-state.json` - per CLONE and surviving a session restart, because a merge can
happen a day after the local check that vouches for it (which is why `scripts/gate-hooks.sh`'s
per-harness-session state under /tmp was declined). Written by the Makefile: `quick`, `reference`,
`test-file` and a green local `done` record `green-local`; a red local `done` and a failed remote
build record `failed-gate`.

"A source edit resets the state" is not an event to catch. The state carries the content hash of
the diagram area's Python at the time of the run - the SAME hash `scripts/gate-stamp.py` computes
at push, imported rather than reimplemented - and at dispatch time the current hash is recomputed:
a mismatch is "the green run vouched for different code", exactly how `gate-stamp --check`
already reasons.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType

STATE_FILE = ".git/verification-state.json"
GREEN = "green-local"
FAILED = "failed-gate"
GREEN_TARGETS = ("quick", "reference", "test-file", "done")


@dataclass(frozen=True)
class VerificationState:
    event: str
    target: str
    utc: str
    hash: str
    commit: str
    engine_key: str = ""  # delta.engine_key_worktree at the time of the run - what a green local `done` VOUCHES for (GM 2026-08-25)
    scope: str = ""  # the scope switch when written; "reference" = the map-rolling tests were deferred
    tooling: str = ""  # tooling_hash at the last green `done` - `make quick` skips the `tooling` tests while it still matches


def _gate_stamp(root: Path) -> ModuleType:
    """`scripts/gate-stamp.py` is a script, not a package - loaded by path so its hash is THE hash."""
    path = root / "scripts" / "gate-stamp.py"
    spec = importlib.util.spec_from_file_location("gate_stamp", path)
    assert spec is not None and spec.loader is not None, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def current_hash(root: Path) -> str:
    gs = _gate_stamp(root)
    area_path, patterns = gs.AREAS["diagram"]
    files = gs._area_files(root, area_path, patterns)
    return str(gs.hash_files(files, root))


def _commit(root: Path) -> str:
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip()


def read(root: Path) -> VerificationState | None:
    path = root / STATE_FILE
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return VerificationState(
        event=str(data["event"]),
        target=str(data["target"]),
        utc=str(data["utc"]),
        hash=str(data["hash"]),
        commit=str(data.get("commit", "")),
        engine_key=str(data.get("engine_key", "")),
        scope=str(data.get("scope", "")),
        tooling=str(data.get("tooling", "")),
    )


def write(root: Path, event: str, target: str, reused: bool = False) -> VerificationState:
    if event not in (GREEN, FAILED):
        raise ValueError(f"unknown verification event {event!r} (want {GREEN} or {FAILED})")
    from l7r.diagram.ci.delta import engine_key_worktree

    # A GREEN SUBSET NEVER FORGETS A GREEN GATE (GM 2026-08-26, the make quick profile). `quick`,
    # `test-file` and `reference` each record themselves here, and the record is ONE slot - so a
    # `make quick` after a green `make done` on the same content replaced the gate's verdict with a
    # lesser one, and the next `make done` ran its 70 s again for nothing (measured: it did, on the
    # first commit after this rule was noticed). If the standing record is a green `done` against
    # exactly this content, a green run of anything smaller leaves it standing.
    prior = read(root)
    if (
        event == GREEN
        and target != "done"
        and prior is not None
        and prior.event == GREEN
        and prior.target == "done"
        and prior.hash == current_hash(root)
        and prior.engine_key == engine_key_worktree(root)
    ):
        return prior

    st = VerificationState(
        event=event,
        target=target,
        utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        hash=current_hash(root),
        commit=_commit(root),
        engine_key=engine_key_worktree(root),
        scope=_scope(root),
        # only a gate that RAN vouches for the tooling; a short-circuited `done` (`reused`) carries the
        # last real gate's record forward - the first cut re-hashed on the short-circuit and quick then
        # skipped tooling tests no gate had run on a changed Makefile (caught 2026-08-26, T22)
        tooling=tooling_hash(root) if (target == "done" and not reused) else (prior.tooling if prior is not None else ""),
    )
    (root / STATE_FILE).write_text(json.dumps(asdict(st), indent=2) + "\n", encoding="utf-8")
    return st


# The files the `tooling` tests exercise (tests/conftest.py, GM 2026-08-26, T22). Hashed on every green
# `make done`; `make quick` skips the tooling tests while the hash is unchanged.
TOOLING_PATHS = ("Makefile", "pyproject.toml", "l7r/diagram/ci", "l7r/diagram/pipeline", "l7r/diagram/switches.py", "l7r/diagram/_invocation.py", "tests/conftest.py", "tests/_scope.py")


def tooling_hash(root: Path) -> str:
    """A content hash over the tooling the `tooling` tests run: the skill's Makefile/pyproject, the ci
    and pipeline packages, the switches and the invocation guard, the suite's conftest - plus the
    repo's scripts/. Raw bytes, deliberately: a Makefile comment IS a Makefile change worth one run."""
    import hashlib

    skill = root / ".claude" / "skills" / "diagram"
    h = hashlib.sha256()
    files: list[Path] = []
    for rel in TOOLING_PATHS:
        p = skill / rel
        files += sorted(p.rglob("*")) if p.is_dir() else [p]
    files += sorted((root / "scripts").glob("*"))
    for f in files:
        if f.is_file() and "__pycache__" not in f.parts:
            h.update(str(f.relative_to(root)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def _scope(root: Path) -> str:
    """The scope switch's state when a record is written - `reference` means the gate DEFERRED the
    map-rolling tests (Makefile `ROLL_DESELECT`), so the record vouches for less than an unlocked run."""
    from l7r.diagram import switches

    return switches.read(root / ".claude" / "skills" / "diagram").scope.state


def record_tooling(root: Path) -> str:
    """`make tooling` ran every `tooling` test green: vouch for the current tooling in the standing record
    (or a fresh one) without touching the gate verdict. GM 2026-08-26 (T24): *"I don't want to wait until
    we have to make another change to reap the performance benefits of not rerunning those tests."*"""
    prior = read(root)
    h = tooling_hash(root)
    if prior is None:
        st = VerificationState(
            event=GREEN, target="tooling", utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), hash=current_hash(root), commit=_commit(root), engine_key="", scope=_scope(root), tooling=h
        )
    else:
        st = VerificationState(**{**asdict(prior), "tooling": h})
    (root / STATE_FILE).write_text(json.dumps(asdict(st), indent=2) + "\n", encoding="utf-8")
    return h


def already_verified(root: Path) -> tuple[bool, str]:
    """THE LOCAL SHORT-CIRCUIT (feature 132 amendment, GM 2026-08-25: *"apply the same rules that
    decide whether to short circuit and skip AWS tests to these 5 minute tests as well for the
    make done procedure"*). True when the last recorded verification is a green `make done` and
    the two things the DISPATCHER keys on are unchanged: the content hash of every .py under the
    skill (its `green-local-since-edit` condition - gate-stamp's own hash, so a short-circuit can
    never stamp Python no gate ran on) and the engine key over tests and pool data (its
    `tree-not-already-verified` condition). Nothing else - the GM's second amendment: *"I thought
    we were omitting `make done` results for changes to the hooks or scripts or makefile changes,
    etc."* - so a Makefile, pyproject, lockfile or scripts/ edit does not owe the gate, exactly as
    it does not owe a build. A green `quick` or `reference` vouches for less than the gate does
    and never qualifies; a red run never does."""
    from l7r.diagram.ci.delta import engine_key_worktree

    st = read(root)
    if st is None:
        return False, "no local check recorded in this clone"
    if st.event != GREEN or st.target != "done":
        return False, f"the last record is `make {st.target}` ({st.event}) - only a green `make done` can be reused"
    if st.hash != current_hash(root):
        return False, f"`make done` was green at {st.utc} ({st.commit}), but the skill's Python changed since - that run vouched for different code"
    if not st.engine_key or st.engine_key != engine_key_worktree(root):
        return False, f"`make done` was green at {st.utc} ({st.commit}), but a pool gen or manifest changed since - that run vouched for different content"
    if st.scope == "reference" and _scope(root) != "reference":
        return False, f"`make done` was green at {st.utc} ({st.commit}) while scope was LOCKED - the map-rolling tests were deferred; scope is unlocked now, so they are owed (GM 2026-08-26)"
    return (
        True,
        f"already verified: `make done` was green at {st.utc} ({st.commit}) against exactly this engine content - nothing it exercises has changed (docs, the Makefile, config and scripts/ do not count)",
    )


def describe(st: VerificationState | None, now_hash: str) -> str:
    if st is None:
        return "no local check recorded in this clone"
    fresh = "current code" if st.hash == now_hash else "DIFFERENT code (a source edit happened since)"
    return f"{st.event} from `make {st.target}` at {st.utc} ({st.commit}), against {fresh}"
