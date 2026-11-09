"""The Python callers' door to the verification state in the Rust gate (feature 449 T72): `rust/gate/src/state.rs` writes and reads
`.git/verification-state.json` and holds the tooling hash. This module holds the record's type and two constants `decision.py` and
`dispatch.py` take until T064 ports them, and each call is one process."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from l7r.diagram.ci.delta import gate

GREEN = "green-local"
FAILED = "failed-gate"


@dataclass(frozen=True)
class VerificationState:
    event: str
    target: str
    utc: str
    hash: str
    commit: str
    engine_key: str = ""
    tooling: str = ""


def current_hash(root: Path) -> str:
    """The `diagram` area's key, the same hash its green stamp holds."""
    return gate(root, "stamp", "--key", "diagram").strip()


def read(root: Path) -> VerificationState | None:
    data = json.loads(gate(root, "state", "read"))
    return None if data is None else VerificationState(**data)


def write(root: Path, event: str, target: str, reused: bool = False) -> VerificationState:
    gate(root, "state", "write", event, target, *(["reused"] if reused else []))
    st = read(root)
    assert st is not None, "the gate wrote a record"
    return st


def tooling_hash(root: Path) -> str:
    return gate(root, "state", "tooling-hash").strip()


def state_dir(root: Path) -> Path:
    """The directory the record lives in: a worktree's own git directory, a plain clone's `.git`."""
    return Path(gate(root, "state", "dir").strip())


def describe(st: VerificationState | None, now_hash: str) -> str:
    if st is None:
        return "no local check recorded in this clone"
    fresh = "current code" if st.hash == now_hash else "DIFFERENT code (a source edit happened since)"
    return f"{st.event} from `make {st.target}` at {st.utc} ({st.commit}), against {fresh}"
