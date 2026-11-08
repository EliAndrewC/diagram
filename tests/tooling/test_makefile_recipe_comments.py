"""No recipe comment in a Makefile may RUN (feature 212, the GM's ruling relayed 2026-09-07).

This project comments a recipe with a shell no-op, ``: "..."``. Inside that double-quoted string a
backtick or a ``$(`` (written ``$$(`` in a Makefile) is a command substitution. Feature 185 found the
gate's phase loop running lint on every gate because its comment named ``lint`` in backticks; feature
207 wrote a comment naming ``make test-full`` in backticks INTO ``test-full``, which ran itself and
recursed 914 levels until the container hit its 2,048-process limit. Both fixes were a reworded line
and a note, and the GM ruled that a note is not prevention. The edit-time refusal lives in
``rust/guard/src/guards/guard_file_hooks.rs``, its backstop and the proof that the detector fires are that crate's tests (feature 449 T051); this keeps the marker rule, for the routes an edit can arrive by
that the hook never sees - a merge, a scripted sweep - and the proof that the detector FIRES.
"""

from __future__ import annotations

import pathlib

SKILL = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILL
SCRIPTS = REPO / "scripts"


def test_the_root_makefile_holds_no_guard_edit_marker() -> None:
    """Feature 170 amendment 1 (FR-006(e)): the root Makefile takes no `GUARD_EDIT_OK` comment - its reasons go through
    `make guard-edit` into the guard log. guard-file-hooks.sh refuses one on the Edit route; this catches the shell route.
    Two came back within hours of the cleanup that removed 1,300 lines of them (cbf1721ff)."""
    text = (REPO / "Makefile").read_text(encoding="utf-8")
    lines = [n for n, line in enumerate(text.splitlines(), 1) if "GUARD_EDIT_OK" in line]
    assert not lines, (
        f"the root Makefile holds GUARD_EDIT_OK on line(s) {lines}: delete the marker, and give its reason with "
        'make guard-edit FILE=Makefile WHY="<reason>" before the edit, and in the commit message'
    )
