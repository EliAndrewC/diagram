"""The Python callers' one door to the record's owed tools in Rust (feature 449 T87, on the T86 door's pattern): `ro`, `ru`, `mo`, `mt`, the four ported modules' names, each a forwarder and never a fallback, one `l7r-gate owed-door` process a run, its verbs in order so a read follows its own write (FR-006). Deleted with its last caller; named at the phase-3 close if still present.

A `Record` crosses as the key that reproduces it (root, rev, sources), `fingerprint` and `quotation_key` verbs on that key, no cache for the working tree (`ask:449-T87-entry-owed`); a caller taking the pair from one read makes one call (`fingerprint_and_keys`)."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from types import SimpleNamespace
from typing import Any

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"

_door: subprocess.Popen[str] | None = None
_door_env: tuple[str | None, ...] = ()
#: what the door reads from its environment: a changed one is a fresh door
_READ_FROM_ENV = ("RECORD_CHECKS_DIR", "HOME", "L7R_GATE_TREE", "L7R_FEATURE_DIRECTORY", "SPECIFY_FEATURE", "GUARD_LOG_DIR")


def _ask(verb: str, *args: Any) -> Any:  # noqa: ANN401 - the verb's JSON
    global _door, _door_env  # noqa: PLW0603 - one process a run (FR-006), but a changed environment is a new one
    wanted = tuple(os.environ.get(k) for k in _READ_FROM_ENV)
    if _door is not None and wanted != _door_env:
        assert _door.stdin is not None
        _door.stdin.close()
        _door.wait()
        _door = None
    if _door is None:
        _door_env = wanted
        _door = subprocess.Popen([str(GATE), "owed-door"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    assert _door.stdin is not None and _door.stdout is not None
    _door.stdin.write(json.dumps({"verb": verb, "args": list(args)}) + "\n")
    _door.stdin.flush()
    line = _door.stdout.readline()
    if not line:
        raise ValueError(f"owed-door: no answer to {verb}")
    said = json.loads(line)
    if "error" in said:
        raise ValueError(said["error"])
    return said["ok"]


def _strs(values: Iterable[Any] | None) -> list[str] | None:
    return None if values is None else [str(v) for v in values]


def _unit(d: Mapping[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(**d)


class Modal:
    """A modal the door returned: its fields and its derived properties, every one computed in Rust; handed back to a verb whole."""

    def __init__(self, d: dict[str, Any]) -> None:
        self.__dict__.update(d)
        self._raw = d

    def entry_files(self) -> list[str]:
        return self._raw["entry_files"]

    def drawing_files(self) -> list[str]:
        return self._raw["drawing_files"]


def _modal(d: dict[str, Any] | None) -> Modal | None:
    return None if d is None else Modal(d)


class Record:
    """What `read_at` returned: the key that reproduces it, the notes and cites a caller reads; a verb re-reads it by the key."""

    def __init__(self, root: pathlib.Path, rev: str | None, sources: Iterable[str] | None, d: dict[str, Any]) -> None:
        self.root, self.rev, self.sources = str(root), rev, _strs(sources)
        self.notes, self.cites = d["notes"], d["cites"]

    def key(self) -> list[Any]:
        return [self.root, self.rev, self.sources]


class _Consts(type):
    """Each namespace's constants (`QUESTIONS`, `FIXED`, `ORDER`, ...), asked of the door when read."""

    def __getattr__(cls, name: str) -> Any:  # noqa: ANN401, N805 - a constant
        v = _ask(f"const.{name}")
        return tuple(v) if isinstance(v, list) else {k: tuple(u) for k, u in v.items()} if isinstance(v, dict) else v


class ru(metaclass=_Consts):  # noqa: N801 - `record_units`, as its callers name it
    @staticmethod
    def question(subject: str) -> str:
        return _ask("ru.question", subject)

    @staticmethod
    def digest(parts: Iterable[str]) -> str:
        return _ask("ru.digest", list(parts))

    @staticmethod
    def read_page(text: str) -> SimpleNamespace:
        d = _ask("ru.read_page", text)
        d["blocks"] = [SimpleNamespace(**b) for b in d["blocks"]]
        return SimpleNamespace(**d)

    @staticmethod
    def read_notes(notes: str, originals: str = "") -> dict[str, str]:
        return _ask("ru.read_notes", notes, originals)

    @staticmethod
    def stem_matches(name: str) -> bool:
        return _ask("ru.stem_matches", name)

    @staticmethod
    def Unit(slug: str, occasion: str, fingerprint: str = "", reading: str = "") -> SimpleNamespace:  # noqa: N802 - the class's name
        return _unit(_ask("ru.unit", slug, occasion, fingerprint, reading))

    @staticmethod
    def fingerprints_of(rec: Record, slugs: Sequence[str]) -> dict[str, str]:
        return _ask("ru.fingerprints_of", *rec.key(), list(slugs))

    @staticmethod
    def fingerprint_and_keys(rec: Record, slugs: Sequence[str]) -> dict[str, tuple[str, str]]:
        return {k: tuple(v) for k, v in _ask("ru.fingerprint_and_keys", *rec.key(), list(slugs)).items()}


class ro(metaclass=_Consts):  # noqa: N801 - `record_owed`, as its callers name it
    ru = ru

    @staticmethod
    def units(root: pathlib.Path, base: str | None = None, head: str | None = None, families: Sequence[str] | None = None, uid: str = "") -> list[SimpleNamespace]:
        return [_unit(d) for d in _ask("ro.units", str(root), base, head, _strs(families), uid)]

    @staticmethod
    def unanswered(root: pathlib.Path) -> list[SimpleNamespace]:
        return [_unit(d) for d in _ask("ro.unanswered", str(root))]

    @staticmethod
    def merge_base(root: pathlib.Path) -> str:
        return _ask("ro.merge_base", str(root))

    @staticmethod
    def _git(root: pathlib.Path, *args: str) -> str:
        return _ask("ro.git", str(root), list(args))

    @staticmethod
    def store(root: pathlib.Path) -> pathlib.Path:
        return pathlib.Path(_ask("ro.store", str(root)))

    @staticmethod
    def read_at(root: pathlib.Path, rev: str | None, sources: Iterable[str] | None = None) -> Record:
        wanted = _strs(sources)
        return Record(root, rev, wanted, _ask("ro.read_at", str(root), rev, wanted))

    @staticmethod
    def answered(store: pathlib.Path, slug: str, fp: str, reading: str = "") -> bool:
        return _ask("ro.answered", str(store), slug, fp, reading)

    @staticmethod
    def _read(store: pathlib.Path, slug: str) -> dict[str, Any]:
        return _ask("ro._read", str(store), slug)

    @staticmethod
    def write_answer(store: pathlib.Path, slug: str, fp: str, result: str, pages: Mapping[str, str] | None = None) -> None:
        _ask("ro.write_answer", str(store), slug, fp, result, pages)

    @staticmethod
    def settle(store: pathlib.Path, slug: str, before: str, after: str) -> str:
        return _ask("ro.settle", str(store), slug, before, after)

    @staticmethod
    def keep_reading(store: pathlib.Path, slug: str, reading: str, field: str = "readings") -> None:
        _ask("ro.keep_reading", str(store), slug, reading, field)

    @staticmethod
    def reply_checks(reply: str) -> tuple[str, ...]:
        return tuple(_ask("ro.reply_checks", reply))

    @staticmethod
    def fingerprints(root: pathlib.Path, checks: Sequence[str]) -> dict[str, str]:
        return _ask("ro.fingerprints", str(root), list(checks))

    @staticmethod
    def file_outside(root: pathlib.Path, check: str, reply: str) -> list[dict[str, Any]]:
        return _ask("ro.file_outside", str(root), check, reply)


class mo(metaclass=_Consts):  # noqa: N801 - `modal_owed`, as its callers name it
    Modal = Modal

    @staticmethod
    def modals_now(root: pathlib.Path, about_only: bool = True) -> list[Modal]:
        return [Modal(d) for d in _ask("mo.modals_now", str(root), about_only)]

    @staticmethod
    def modals_at(root: pathlib.Path, rev: str, about_only: bool = True) -> dict[str, Modal]:
        return {k: Modal(d) for k, d in _ask("mo.modals_at", str(root), rev, about_only).items()}

    @staticmethod
    def find(root: pathlib.Path, kind: str) -> Modal | None:
        return _modal(_ask("mo.find", str(root), kind))

    @staticmethod
    def fingerprints(root: pathlib.Path, m: Modal) -> tuple[str, str]:
        return tuple(_ask("mo.fingerprints", str(root), m._raw))

    @staticmethod
    def depiction_fingerprint(root: pathlib.Path, m: Modal) -> str:
        return _ask("mo.depiction_fingerprint", str(root), m._raw)

    @staticmethod
    def owed(root: pathlib.Path, base: str, uid: str = "") -> list[tuple[str, str, str]]:
        return [tuple(r) for r in _ask("mo.owed", str(root), base, uid)]

    @staticmethod
    def kinds_in(source: str) -> list[tuple[str, str, int, str]]:
        return [tuple(r) for r in _ask("mo.kinds_in", source)]

    @staticmethod
    def modal_file(py_path: str, key: str) -> str:
        return _ask("mo.modal_file", py_path, key)

    @staticmethod
    def choice_modal(path: str, text: str, about_only: bool = True) -> Modal | None:
        return _modal(_ask("mo.choice_modal", path, text, about_only))

    @staticmethod
    def depiction_owed_by(was: Modal | None, m: Modal) -> bool:
        return _ask("mo.depiction_owed_by", None if was is None else was._raw, m._raw)

    @staticmethod
    def earlier_units(unit_checks: Sequence[str]) -> tuple[str, ...]:
        return tuple(_ask("mo.earlier_units", list(unit_checks)))


class mt:  # noqa: N801 - `modal_triage`, as its callers name it
    @staticmethod
    def keep(root: pathlib.Path, path: str) -> str:
        return _ask("mt.keep", str(root), path)

    @staticmethod
    def triage_only(why: str) -> bool:
        return _ask("mt.triage_only", why)

    @staticmethod
    def refusal(root: pathlib.Path, m: Modal, check: str, owed: Sequence[tuple[str, str, str]] | None = None) -> str:
        return _ask("mt.refusal", str(root), m._raw, check, None if owed is None else [list(r) for r in owed])

    @staticmethod
    def bundle(root: pathlib.Path, out: pathlib.Path, base: str = "") -> tuple[pathlib.Path | None, int]:
        manifest, n = _ask("mt.bundle", str(root), str(out), base)
        return (None if manifest is None else pathlib.Path(manifest)), n
