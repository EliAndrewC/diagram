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
    (a / rp.DIRS["glossary"] / "0130-kuji-x.json").write_text("{}", encoding="utf-8")
    (a.parent / "b" / rp.DIRS["glossary"] / "0160-long-y.json").write_text("{}", encoding="utf-8")
    assert rp.main(["glossary", "x", "--root", str(a)]) == 0, "`0130-kuji-x.json` holds kuji-x, not a key it merely ends in"
    assert rp.main(["glossary", "y", "--root", str(a)]) == 0, "nor does another clone's `0160-long-y.json` hold `y`"


def test_a_key_that_ends_another_key_is_not_refused(tmp_path) -> None:
    """`honjin-jawiki` was refused because `kusatsu-honjin-jawiki` was on file: the glob matched the longer key."""
    mirror, a = _world(tmp_path)
    b = a.parent / "b"
    rp.reserve("registry", "kusatsu-honjin-jawiki", a)
    rp.reserve("registry", "tall-honjin-jawiki", b)
    assert rp.reserve("registry", "honjin-jawiki", a).name.endswith("0-honjin-jawiki.html")
    assert rp.held_elsewhere("registry", "honjin-jawiki", a, mirror) == ""


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


def test_a_write_session_s_eleventh_registry_key_is_refused_with_the_continuation(tmp_path, monkeypatch, capsys) -> None:
    """Feature 274 D4 (SC-001): the runner tells a WRITE session its id and the cap; the eleventh registry key is refused
    with the continuation instructions, a glossary term is not, `KEY_CAP_OK` with a reason passes (logged), and a session
    without the cap - a check session - is never refused."""
    mirror, a = _world(tmp_path)
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "log"))
    monkeypatch.setenv("L7R_PAGE_SESSION", "sid-w")
    monkeypatch.setenv("L7R_KEY_CAP", "10")
    monkeypatch.setenv("L7R_CONTINUE", "/x/continue.md")
    monkeypatch.delenv("KEY_CAP_OK", raising=False)
    for n in range(10):
        rp.reserve("registry", f"key-{n}", a)
    rows = [json.loads(ln) for ln in (mirror / ".specify" / rp.LEDGER).read_text(encoding="utf-8").splitlines()]
    assert {r["session"] for r in rows} == {"sid-w"} and rp.session_keys(mirror, "sid-w") == 10
    assert rp.main(["registry", "key-10", "--root", str(a)]) == 2
    err = capsys.readouterr().err
    assert "reserved 10 new registry keys" in err and "/x/continue.md" in err and "## Your items" in err and "KEY_CAP_OK" in err
    assert rp.reserve("glossary", "a term", a).name.endswith("-a term.json"), "glossary terms are not capped"
    monkeypatch.setenv("KEY_CAP_OK", "x")
    assert rp.main(["registry", "key-10", "--root", str(a)]) == 2 and "needs a REASON" in capsys.readouterr().err
    monkeypatch.setenv("KEY_CAP_OK", "one source per shrine is the question")
    assert rp.main(["registry", "key-10", "--root", str(a)]) == 0
    logged = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((tmp_path / "log").glob("*.json"))]
    assert [(e["guard"], e["event"], e["rule"]) for e in logged][-1] == ("reserve", "escaped", "key-cap")
    monkeypatch.delenv("KEY_CAP_OK")
    monkeypatch.setenv("L7R_PAGE_SESSION", "sid-other")
    assert rp.main(["registry", "key-11", "--root", str(a)]) == 0, "the cap is per session"
    monkeypatch.setenv("L7R_PAGE_SESSION", "sid-w")
    monkeypatch.delenv("L7R_KEY_CAP")
    assert rp.main(["registry", "key-12", "--root", str(a)]) == 0, "a session the runner did not cap (a check session) is not refused"
    (mirror / ".specify" / rp.LEDGER).write_text("not json\n", encoding="utf-8")
    assert rp.session_keys(mirror, "sid-w") == 0
