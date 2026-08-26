"""Scaffold a new gate check so its conventions cannot be missed: `make new-check`.

WHY THIS EXISTS (GM 2026-08-26, feature 133 T10). Adding two checks by hand cost four fix cycles
in one sitting, every one a convention rather than a thought: a test builder not imported, an
input (`M`) read but not declared in the signature, the fixture list not kept sorted, a `_kept`
tuple that had to be a literal. Each miss was ten seconds to fix and a full model round trip to
find. The scaffold writes the three pieces a check always has - the segment stub with the next
free key in its file, the sorted fixture entry, the test stub with the builders imported - so the
only thing left to write is the rule itself.

Usage (through make, never bare):

    make new-check NAME=gardens_unshaded_by_neighbors \
        FILE=l7r/diagram/check_village/segments_04c_groves_and_shading.py \
        TEST=tests/check_village/test_segments_04_homesteads.py

Pure text edits; no engine import, so it runs anywhere and its tests run under `make quick`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_KEY = re.compile(r"^def _seg_(\d+)(?:_(\d+))?__", re.MULTILINE)
_FIXTURE = Path("tests/fixtures/gate_check_names.json")


def next_key(segment_source: str) -> str:
    """The next free numeric key in a segments file: the file's highest (major, minor) with minor
    bumped by one, so the new segment runs after everything the file already holds (registry order
    is a numeric sort of the key - `check_village/CLAUDE.md`). A file whose last key has no minor
    gets `_500`, the documented between-keys form."""
    keys = [(int(a), int(b) if b else -1) for a, b in _KEY.findall(segment_source)]
    if not keys:
        raise SystemExit("no _seg_ functions in that file - pick the segments file that covers the check's theme")
    major, minor = max(keys)
    return f"{major:04d}_{(minor + 1) if minor >= 0 else 500:03d}"


def segment_stub(key: str, name: str) -> str:
    bad = f"{name}_bad"
    return f'''

# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


def _seg_{key}__{name}(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    {bad}: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment {key} ({name}) - <what it rules, in one line>."""
    if scale in ("hamlet", "village", "town"):
        {bad} = []
        # measure into {bad}: append (round(x), round(y)) for every offender
        check(
            "{name}",
            not {bad},
            f"<offender>(s) {{{bad}[:3]}} <what is wrong, and the fix direction>",
        )
    return _kept(locals(), ("{bad}",))
'''


def test_stub(name: str) -> str:
    return f'''

def test_{name}_fires_and_passes():
    """<the rule in one line, and the GM's words or the research that fixed it>."""
    bad = manifest(houses=[house(x=400, y=400)])  # TODO: the offending geometry
    assert "{name}" in f(bad), "the motivating defect must fire"
    good = manifest(houses=[house(x=400, y=400)])  # TODO: the same map, fixed
    assert "{name}" not in f(good), "a conforming map must pass"
'''


def add_fixture_name(fixture_path: Path, name: str) -> None:
    names = json.loads(fixture_path.read_text())
    if name in names:
        raise SystemExit(f"{name!r} is already in {fixture_path} - the check exists, or pick another name")
    names.append(name)
    fixture_path.write_text(json.dumps(sorted(names), indent=2) + "\n")


def ensure_test_imports(test_source: str) -> str:
    """The builders the stub uses, imported if the file does not already import them."""
    needed = ["f", "house", "manifest"]
    m = re.search(r"from tests\.check_village\._builders import \(\n(?P<body>(?:    .*\n)+?)\)", test_source)
    if m is None:
        return "from tests.check_village._builders import f, house, manifest  # noqa: F401\n" + test_source
    have = {ln.strip().rstrip(",") for ln in m.group("body").splitlines()}
    missing = [n for n in needed if n not in have]
    if not missing:
        return test_source
    body = sorted(have | set(missing), key=lambda s: (s.lstrip("_"), s))
    new_block = "from tests.check_village._builders import (\n" + "".join(f"    {n},\n" for n in body) + ")"
    return test_source[: m.start()] + new_block + test_source[m.end() :]


def scaffold(name: str, segment_file: Path, test_file: Path, fixture_path: Path = _FIXTURE) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise SystemExit("NAME must be a snake_case identifier")
    src = segment_file.read_text()
    if f"__{name}(" in src:
        raise SystemExit(f"{name!r} already has a segment in {segment_file}")
    key = next_key(src)
    segment_file.write_text(src.rstrip("\n") + "\n" + segment_stub(key, name))
    add_fixture_name(fixture_path, name)
    test_file.write_text(ensure_test_imports(test_file.read_text()).rstrip("\n") + "\n" + test_stub(name))
    return key


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name", required=True)
    ap.add_argument("--file", required=True, help="the check_village/segments_*.py file that covers the theme")
    ap.add_argument("--test", required=True, help="the tests/check_village/test_segments_*.py file that covers it")
    a = ap.parse_args(argv)
    key = scaffold(a.name, Path(a.file), Path(a.test), _FIXTURE)  # the module global, read at call time
    print(f"scaffolded `{a.name}` as _seg_{key}__ in {a.file}; fixture entry added (sorted); test stub in {a.test}")
    print("next: write the rule and its WHY into the stub, fill both TODO manifests in the test, then ONE `make quick`.")
    return 0


if __name__ == "__main__":  # pragma: no cover - the make target's entry
    sys.exit(main())
