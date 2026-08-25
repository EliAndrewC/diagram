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
    return str(gs.hash_files(files))


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
    )


def write(root: Path, event: str, target: str) -> VerificationState:
    if event not in (GREEN, FAILED):
        raise ValueError(f"unknown verification event {event!r} (want {GREEN} or {FAILED})")
    from l7r.diagram.ci.delta import engine_key_worktree

    st = VerificationState(
        event=event,
        target=target,
        utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        hash=current_hash(root),
        commit=_commit(root),
        engine_key=engine_key_worktree(root),
    )
    (root / STATE_FILE).write_text(json.dumps(asdict(st), indent=2) + "\n", encoding="utf-8")
    return st


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
        return False, f"`make done` was green at {st.utc} ({st.commit}), but a test or pool gen/manifest changed since - that run vouched for different content"
    return (
        True,
        f"already verified: `make done` was green at {st.utc} ({st.commit}) against exactly this engine content - nothing it exercises has changed (docs, the Makefile, config and scripts/ do not count)",
    )


def describe(st: VerificationState | None, now_hash: str) -> str:
    if st is None:
        return "no local check recorded in this clone"
    fresh = "current code" if st.hash == now_hash else "DIFFERENT code (a source edit happened since)"
    return f"{st.event} from `make {st.target}` at {st.utc} ({st.commit}), against {fresh}"
