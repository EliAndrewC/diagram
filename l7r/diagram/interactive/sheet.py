"""A Mode A sheet drawn whole by the Rust engine: the pool generators' one call into it (feature 449 T150-T152).

The page it writes is a hand-drawn sheet as an interactive page, the SVG's own `data-kind` tags the class side list (feature 262).

The GM, 2026-09-26, asking for clickable magistracy maps: *"the main important thing is that the labels and the
features on the building diagram for each magistracy have a common source, such that changing that source in one
place is enough to change it downstream."* A hamlet's page gets its (string, class) pairs from the generator that
drew it; a hand-drawn Mode A sheet has no generator, so the pairs are read back out of the drawing itself. Every
element or group carries `data-kind="<key>"` - the nearest one wins - and `data-kind="-"` is the not-highlighted
ruling. The label drawn inside a feature's group is that feature's ink, so relabeling a building is one edit to the
sheet and nothing else; what a KIND is lives once, in `compound/`'s registry.

Look here when: a pool generator's call to the Mode A engine fails. THE SHEET IS RUST: its reader is
`rust/mode_a/src/sheet.rs`, its page `rust/mode_a/src/sheet/page.rs` (feature 449 T150), a hand sheet drawn whole by
`draw_hand_sheet` (`l7r-gate.sh mode-a hand-sheet`, `rust/mode_a/src/sheet/hand.rs`, T151) and a generated one by
`draw_compound_sheet` (`l7r-gate.sh mode-a compound`, T152). This module is only those two calls, which the pool's `.gen.py`
files make; the Python reader (`parse`, `Node`, `element_kinds`) and `write_sheet_page` went with the Python audit, their last
importer (T212). T157 rebuilds the pipeline that runs the generators and drops this module.
"""


from __future__ import annotations

import builtins
import importlib
import json
import os
import subprocess
import sys


#: The tree this module is in: its launcher builds and runs the Mode A engine (`scripts/gates/l7r-gate.sh mode-a`).
_TREE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _raised(kind: str, message: str) -> BaseException:
    """The exception the Python writer raised for the engine's refusal `kind: message` - its class by name (a builtin, or a dotted
    one such as `l7r.diagram._census.RenderedInATest`), so a generator's traceback ends on the line it ended on; a class that cannot
    be built from a message alone is stood in for by one of the same name."""
    module, _, name = kind.rpartition(".")
    try:
        cls = getattr(importlib.import_module(module) if module else builtins, name)
        return cls(message)
    except ImportError, AttributeError, TypeError:
        return type(name, (Exception,), {"__module__": module or "builtins"})(message)


def _engine(argv: list[str], text: str | None = None) -> tuple[dict, int]:
    """`l7r-mode-a <argv>` run, `text` on its stdin: its JSON reply and its exit, its stderr passed on to the generator's. A refusal
    (`{"error": ...}`) is raised as the exception the Python raised (`_raised`), its traceback's last line not printed twice.

    THE READS ARE OPENED HERE (feature 449 T150): the generation cache learns a generator's data files by spying on `open()`
    (`gencache.record`, spec 187 D3), which cannot see the engine's process, so each file the engine read is opened for reading
    here - a sheet, stylesheet or question edit still re-keys the map."""
    full = [os.path.join(_TREE, "scripts", "gates", "l7r-gate.sh"), "mode-a", *argv]
    run = subprocess.run(full, input=(text or "").encode("utf-8"), capture_output=True, check=False)
    said = run.stderr.decode("utf-8", "replace")
    try:
        out = json.loads(run.stdout)
    except ValueError:
        raise RuntimeError(f"l7r-mode-a {argv[0]} exited {run.returncode}: {said}") from None
    # the engine's warnings (resvg absent: the page carries no picture) reach the generator's stderr as the Python writer's did; a
    # refusal's own last line is the exception raised below, not printed twice
    if "error" in out:
        kind = out["error"]["kind"]
        at = said.rfind("\n" + kind) + 1 if not said.startswith(kind) else 0  # the refusal's text, its message of any length
        sys.stderr.write(said[:at])
        raise _raised(kind, out["error"]["message"])
    sys.stderr.write(said)
    for path in out["reads"]:
        with open(path, "rb"):
            pass
    return out, run.returncode


def draw_compound_sheet(spec_path: str) -> int:
    """A generated compound sheet drawn whole by the Mode A engine (`l7r-mode-a compound`, feature 449 T152): its program read from
    `<map>.compound.json`, composed by the compound generator rebuilt in Rust from its derivation, its captions placed by the one placer,
    the placed sheet written beside it as `<map>.svg`, its picture rendered unless `DIAGRAM_SKIP_RENDER=1`, its page written and its
    census judged - the engine prints the sheet's untagged ink and unknown kinds and exits 1. A program the generator refuses (no room on
    a wall, a rule that cannot hold) is raised as the engine's exception. The generator's exit is returned."""
    _, code = _engine(["compound", spec_path])
    return code


def draw_hand_sheet(svg_path: str) -> int:
    """A hand-drawn sheet drawn whole by the Mode A engine (`l7r-mode-a hand-sheet`, feature 449 T151, the engine port's step 3a): its
    captions placed by the one placer (feature 286), its picture rendered from the placed text unless `DIAGRAM_SKIP_RENDER=1`, its page
    written beside it (feature 277), and its census judged - the engine prints the sheet's untagged ink and unknown kinds and exits 1, as
    the generator did. The generator's exit is returned; the tracked sheet is never touched."""
    _, code = _engine(["hand-sheet", svg_path])
    return code
