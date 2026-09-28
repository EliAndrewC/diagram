"""`scripts/_coord.py` - `make lines` and `make append` (feature 274 D5, SC-002).

WHAT THESE PROVE. `lines` prints only the matching lines, numbered, with how many were shown of how many, and says
when its cap cut matches off; `append` adds one line without printing the file, keeps quotes and `$` from the
environment, and mends a file that did not end in a newline. Both run through `make`, as a session calls them.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[5]
SKILL = REPO / ".claude" / "skills" / "diagram"


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_coord", REPO / "scripts" / "_coord.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


co = _load()


def test_lines_prints_only_the_matching_lines_numbered_with_the_count(tmp_path: pathlib.Path) -> None:
    f = tmp_path / "claims.md"
    f.write_text("# claims\n- 269: group V2 in progress\n- 271: G1 done\n- 269: group C1 queued\n", encoding="utf-8")
    assert co.lines(f, r"^- 269") == ["2: - 269: group V2 in progress", "4: - 269: group C1 queued", "(2 of 4 lines shown)"]
    f.write_text("".join(f"row {n}\n" for n in range(100)), encoding="utf-8")
    got = co.lines(f, "row")
    assert len(got) == co.MAX + 2 and got[-2:] == ["(80 of 100 lines shown)", "(20 more matched - narrow KEY)"]


def test_append_adds_one_line_and_never_prints_the_file(tmp_path: pathlib.Path, capsys) -> None:
    f = tmp_path / "new" / "report.md"
    assert co.main(["append", str(f)], {"LINE": "- 210: VERBATIM 3/3, \"quoted\" $HOME"}) == 0
    f.write_text(f.read_text(encoding="utf-8") + "no newline", encoding="utf-8")
    assert co.main(["append", str(f)], {"LINE": "- 212: done"}) == 0
    assert f.read_text(encoding="utf-8") == "- 210: VERBATIM 3/3, \"quoted\" $HOME\nno newline\n- 212: done\n"
    assert capsys.readouterr().out == f"appended to {f}\nappended to {f}\n"
    assert co.main(["append", str(f)], {"LINE": " "}) == 2 and co.main(["append", str(f)], {"LINE": "a\nb"}) == 2
    assert co.main(["lines", str(tmp_path / "gone.md"), "x"]) == 2 and co.main(["lines", str(f), "("]) == 2
    assert co.main(["lines", str(f), "212"]) == 0 and "3: - 212: done" in capsys.readouterr().out
    assert co.main([]) == 2


def test_a_relative_file_is_found_from_where_make_ran_or_the_repository_root(tmp_path: pathlib.Path) -> None:
    assert co.resolve("/abs/x.md") == pathlib.Path("/abs/x.md")
    assert co.resolve("x.md", tmp_path) == tmp_path / "x.md", "its directory is here"
    assert co.resolve("specs/274-leaner-research-sessions/spec.md", SKILL) == REPO / "specs/274-leaner-research-sessions/spec.md"
    assert co.resolve("no/such/dir/x.md", tmp_path) == tmp_path / "no/such/dir/x.md", "outside a repository it stays where it was"


def test_both_run_through_make_from_the_clone_root(tmp_path: pathlib.Path) -> None:
    f = tmp_path / "handoff.md"
    env = {k: v for k, v in os.environ.items() if not k.startswith("MAKE")}
    run = lambda *a: subprocess.run(["make", "-s", *a], cwd=REPO, env=env, capture_output=True, text=True, check=False)  # noqa: E731
    got = run("append", f"FILE={f}", "LINE=- 700: IN-STEP, it's \"fine\"")
    assert got.returncode == 0 and got.stdout.strip() == f"appended to {f}", got.stderr
    got = run("lines", f"FILE={f}", "KEY=^- 700: IN-STEP")
    assert got.stdout.splitlines() == ["1: - 700: IN-STEP, it's \"fine\"", "(1 of 1 lines shown)"], got.stderr
    assert run("lines", f"FILE={f}").returncode == 2 and run("append").returncode == 2
