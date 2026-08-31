"""Every `from l7r.diagram... import NAME` in the tree resolves (feature 173).

WHY THIS EXISTS. Splitting a module into a package has to preserve the module's surface, and the
mover derives that surface by GREPPING for importers. A grep is a fine way to build the list and a
bad way to verify it: feature 173's stopped at the first newline, so a parenthesized multi-line
import contributed only its first line, and `_COMMONS_FLOOR_FT` silently left
`hamletgen.hinterland`'s surface. Nothing but a full gate run found it - one test imports that name
and it is in `tests/gate/`, which `make quick` never selects.

So the verification is no longer a grep. This resolves every first-party from-import in the tree
against the live package, which is the method the settlement-review used to audit the same split
(2026-08-31) and the only one that cannot share the derivation's blind spots. It is cheap - one AST
walk plus imports the suite has already paid for - and it generalizes: the ~1,000-line bar is GATED
now, so splits will happen more often than the fourteen in this repository's first year.

NOT IN `tests/tooling/`, deliberately. Anything under that tree is marked `tooling` BY LOCATION by
`tests/conftest.py` and skipped whenever the tooling hash is unchanged - correct for a test that
exercises the Makefile or the scripts, and exactly wrong for this one, which is about the ENGINE's
packages and must run whenever any of them changes. The first draft sat there and collected zero
tests, which is how the placement rule was learned rather than read.
"""

from __future__ import annotations

import ast
import importlib
import pathlib

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[1]
SKIP = {"legacy-hand-authored-pool", "__pycache__", ".git"}


def _from_imports() -> list[tuple[pathlib.Path, str, str]]:
    """(file, module, name) for every `from l7r.diagram... import name` with an absolute module."""
    out: list[tuple[pathlib.Path, str, str]] = []
    for p in sorted(SKILL.rglob("*.py")):
        if SKIP.intersection(p.relative_to(SKILL).parts):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:  # a gen script mid-edit is not this test's business
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
                continue
            if not node.module.startswith("l7r.diagram"):
                continue
            for alias in node.names:
                if alias.name != "*":
                    out.append((p, node.module, alias.name))
    return out


def _resolves(mod: object, module: str, name: str) -> bool:
    """Does `from <module> import <name>` work?

    Two ways it can, and the second is why the first draft of this test reported 37 false positives
    across `l7r.diagram`, `.ci`, `.tools` and `.pipeline`: `from l7r.diagram.tools import
    cache_audit` imports a SUBMODULE, which is not an attribute of the package until something
    imports it. An attribute check alone calls every such import broken.
    """
    if hasattr(mod, name):
        return True
    try:
        importlib.import_module(f"{module}.{name}")
    except ImportError:
        return False
    return True


_IMPORTS = _from_imports()


def test_the_census_found_the_tree() -> None:
    """A zero-result scan would make every assertion below vacuously true."""
    assert len(_IMPORTS) > 300, f"only {len(_IMPORTS)} first-party from-imports found - wrong root?"


@pytest.mark.parametrize("module", sorted({m for _, m, _ in _IMPORTS}))
def test_every_imported_name_resolves_on_its_module(module: str) -> None:
    """The invariant a package split must preserve, checked against the live module.

    Parametrized per module so a failure names the package whose surface narrowed, rather than
    reporting one name out of several hundred.
    """
    mod = importlib.import_module(module)
    missing = sorted({name for _, m, name in _IMPORTS if m == module and not _resolves(mod, module, name)})
    assert not missing, (
        f"{module} does not expose {missing} - if this module recently became a PACKAGE, its "
        f"__init__.py must re-export them (feature 173; the mover derives that list by grep and a "
        f"grep is what missed _COMMONS_FLOOR_FT)"
    )
