"""No recipe comment in a Makefile may RUN (feature 212, the GM's ruling relayed 2026-09-07).

This project comments a recipe with a shell no-op, ``: "..."``. Inside that double-quoted string a
backtick or a ``$(`` (written ``$$(`` in a Makefile) is a command substitution. Feature 185 found the
gate's phase loop running lint on every gate because its comment named ``lint`` in backticks; feature
207 wrote a comment naming ``make test-full`` in backticks INTO ``test-full``, which ran itself and
recursed 914 levels until the container hit its 2,048-process limit. Both fixes were a reworded line
and a note, and the GM ruled that a note is not prevention. The edit-time refusal lives in
``scripts/guard-file-hooks.sh``; this is the gate-phase backstop for the routes an edit can arrive by
that the hook never sees - a merge, a scripted sweep - and the proof that the detector FIRES.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import Any

SKILL = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
SCRIPTS = REPO / "scripts"


def _hm_make() -> Any:
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("hm_make_212", SCRIPTS / "_hm_make.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_recipe_comment_in_the_repository_would_run() -> None:
    """Every Makefile in the repository (the clone's own tree, not the sibling clones)."""
    hm = _hm_make()
    # the CLONE is itself under .clones/, so the filter reads the path relative to the tree it scans
    makefiles = [p for p in REPO.rglob("Makefile") if not {".clones", ".git"} & set(p.relative_to(REPO).parts)]
    assert SKILL / "Makefile" in makefiles
    bad = {str(p.relative_to(REPO)): hm.recipe_comment_hazards(p.read_text()) for p in makefiles}
    bad = {k: v for k, v in bad.items() if v}
    assert not bad, f"a recipe comment would run a command substitution: {bad}"


def test_the_detector_fires_on_each_hazard_and_passes_each_safe_form() -> None:
    hm = _hm_make()
    fires = [
        '\t: "GUARD_EDIT_OK: feature 207 - `make test-full` is the gate\'s test phase" ; \\',
        '\t@: "see `make help`"',
        '\t: "the key is $$(git rev-parse HEAD) here"',
        '\t: "a brace form $${HOME} too"',
    ]
    safe = [
        '\t: "GUARD_EDIT_OK: feature 207 - make test-full is the gate\'s test phase" ; \\',
        '\t: "the target is \\`make done\\`"',
        '\t: "make runs \\$$(MAKE) sub-invocations even under -n" ; \\',
        "\t: 'GUARD_EDIT_OK: `make done` in single quotes is inert'",
        "# `make done` in a hash comment is make's, never the shell's",
        '\t@echo "$$(date) runs on purpose - a command, not a comment"',
        '\t: "a make-level $(VAR) is expanded by make, not the shell"',
    ]
    for line in fires:
        assert hm.recipe_comment_hazards(line) == [(1, line)], line
    for line in safe:
        assert hm.recipe_comment_hazards(line) == [], line
    text = "target:\n" + safe[0] + "\n" + fires[0] + "\n" + fires[2] + "\n"
    assert [n for n, _ in hm.recipe_comment_hazards(text)] == [3, 4]
