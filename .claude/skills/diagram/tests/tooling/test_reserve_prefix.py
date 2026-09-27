"""`scripts/reserve-prefix.py` (feature 265 FR-010): a prefix reserved under a lock, the file its claim.

WHAT THESE PROVE. The next prefix is 10 past the highest held by the mirror, any clone and the ledger; the file is
written before the lock is released and the ledger records it; two reservations raced in separate processes never
take the same prefix; a key already on file is refused; `--check` answers from the ledger.
"""

from __future__ import annotations

import importlib.util
import json
import multiprocessing
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("reserve_prefix", REPO / "scripts" / "reserve-prefix.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rp = _load()


def _world(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    mirror = tmp / "mirror"
    a = mirror / ".clones" / "a"
    b = mirror / ".clones" / "b"
    for root, n in ((mirror, 100), (a, 120), (b, 150)):
        d = root / rp.DIRS["glossary"]
        d.mkdir(parents=True)
        (d / f"{n:04d}-x{n}.json").write_text("{}", encoding="utf-8")
    return mirror, a


def test_the_next_prefix_passes_every_clone_and_the_ledger(tmp_path) -> None:
    mirror, a = _world(tmp_path)
    path = rp.reserve("glossary", "hitoyado", a)
    assert path.name == "0160-hitoyado.json" and json.loads(path.read_text(encoding="utf-8"))["term"] == "hitoyado"
    assert rp.reserved("glossary", 160, mirror) and not rp.reserved("glossary", 170, mirror)
    assert rp.reserved("glossary", 160, mirror, "hitoyado") and not rp.reserved("glossary", 160, mirror, "another term")
    (a / rp.DIRS["glossary"] / "0160-hitoyado.json").unlink()  # reserved but its file gone: the ledger still holds it
    assert rp.reserve("glossary", "kuchiireya", a).name == "0170-kuchiireya.json"
    reg = rp.reserve("registry", "suzhou-enwiki", a)
    assert reg.name == "0010-suzhou-enwiki.html" and reg.read_text(encoding="utf-8") == ""
    assert rp.main(["registry", "suzhou-enwiki", "--root", str(a), "--check", str(reg)]) == 0
    assert rp.main(["registry", "another-key", "--root", str(a), "--check", str(reg)]) == 1, "the key must match"
    assert rp.main(["registry", "x", "--root", str(a), "--check", "0990-none.html"]) == 1


def test_a_key_already_on_file_is_refused(tmp_path, capsys) -> None:
    _mirror, a = _world(tmp_path)
    assert rp.main(["glossary", "x120", "--root", str(a)]) == 2 and "already holds" in capsys.readouterr().err
    assert rp.main(["glossary", " ", "--root", str(a)]) == 2


def _take(args: tuple[str, str]) -> str:
    root, key = args
    return _load().reserve("glossary", key, pathlib.Path(root)).name


def test_two_reservations_raced_in_processes_never_collide(tmp_path) -> None:
    _mirror, a = _world(tmp_path)
    b = a.parent / "b"
    with multiprocessing.get_context("spawn").Pool(4) as pool:
        names = pool.map(_take, [(str(a if i % 2 else b), f"term{i}") for i in range(8)])
    prefixes = [n.split("-", 1)[0] for n in names]
    assert len(set(prefixes)) == 8, names


def test_a_key_another_clone_holds_is_refused(tmp_path, capsys) -> None:
    """Two of feature 265's queues each reserved `plinth`: the prefixes differed, the term had two homes. A key another
    clone has reserved (the ledger) or already has on file is refused; the clone's own earlier reservation is not."""
    mirror, a = _world(tmp_path)
    b = a.parent / "b"
    rp.reserve("glossary", "plinth", b)
    assert rp.main(["glossary", "plinth", "--root", str(a)]) == 2 and "already being defined in" in capsys.readouterr().err
    assert rp.main(["glossary", "x150", "--root", str(a)]) == 2, "b's file, never reserved through the ledger, is refused too"
    (b / rp.DIRS["glossary"] / next(p.name for p in (b / rp.DIRS["glossary"]).glob("*-plinth.json"))).unlink()
    assert rp.held_elsewhere("glossary", "plinth", b, mirror) == "", "a clone's own reservation never blocks it"
