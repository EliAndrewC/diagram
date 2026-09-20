"""The glossary, written one word per file and assembled back (feature 259).

The GM, 2026-09-20, on reading feature 258's report that the glossary "cannot be scoped away": *"why
could we not just do the same thing with the glossary that we are doing with other files and then split
it into individual files within a directory? For example, each word in the glossary could be the name
of the file in the glossary directory."*

They were right, and the claim was wrong by 114,727 bytes. `record-format` judges VOCABULARY by asking
whether a word is ALREADY DEFINED - a question that needs every term's NAME and never a definition. The
names are 5,808 bytes of the 144,524 the check reads today; the definitions are the other 114,727
(`specs/259-glossary-per-term/research.md` R1). So the source is one file per term, a directory listing
answers the membership question without opening anything, and a definition is read only when a check
wants that term - about 154 bytes.

**WHY THE FILENAME CARRIES A PREFIX** (R2), which the GM's own form did not. `research/assets/record.js`
builds its matcher as `defs[variant] = entry.def`, walking the glossary in FILE ORDER, and only then
sorts the variants by length. Where two terms claim one variant the LATER one silently wins, and seven
variants are in that state. Sorting the terms - which a bare `<term>.json` would force - would change
which definition a reader is shown for those words, with nothing to notice it. The prefix keeps the
order, which keeps `glossary.json` byte-identical, which is what makes the split checkable at all.

**WHAT THIS MODULE MAY NOT DO**: reformat. `glossary.json` is exactly
`json.dumps(obj, ensure_ascii=False, indent=1) + "\\n"`, and the engine, the page writer and every test
over the record's visible text read it. The assembly reproduces those bytes or fails.
"""

from __future__ import annotations

import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
#: The assembled file, where it has always been - the engine and the tests are untouched by this feature.
SOURCE = os.path.join(_HERE, "assets", "glossary.json")
#: The term files, relative to `assets/`'s parent, so a test can point the whole thing at a tmp tree.
TERMS = os.path.join("assets", "glossary")
#: The prefix is gapped by ten, as `research/sources/` is: inserting a term between two renames nothing.
GAP = 10
DIGITS = 4
_NAMED = re.compile(r"^(\d{4})-(.+)\.json$")
#: What `json.dumps` was called with. Measured, not guessed: the committed file matches this exactly.
_DUMP = {"ensure_ascii": False, "indent": 1}


class GlossaryError(Exception):
    """A refusal. Its message names the file and the thing, never a count alone."""


def file_name(position: int, term: str) -> str:
    """`0010-girder.json`. The TERM is the name, as the GM asked - percent-encoded only where a
    filename cannot carry a character, which today is one term (`dS/m`) and no others (R3). A macron
    is left alone: a filename carries it, and transliterating would make a term harder to find."""
    return f"{position * GAP:0{DIGITS}d}-{_encode(term)}.json"


def term_of(name: str) -> str:
    """The term a filename claims - for checking against the file's own content, never for the value."""
    found = _NAMED.match(name)
    if not found:
        raise GlossaryError(f"{name}: not a term file. A term file is <prefix>-<term>.json, the prefix four digits counting by ten")
    return _decode(found.group(2))


def position_of(name: str) -> int:
    found = _NAMED.match(name)
    if not found:
        raise GlossaryError(f"{name}: not a term file")
    return int(found.group(1))


def _encode(term: str) -> str:
    """Only what a filename cannot carry, and reversibly. `%` goes first so the mapping is one to one;
    a macron is left exactly as it is, because a filename carries it and a reader looking for `bettō`
    should find `bettō` (R3)."""
    return term.replace("%", "%25").replace("/", "%2F")


def _decode(name: str) -> str:
    return name.replace("%2F", "/").replace("%25", "%")


def split(raw: str) -> list[dict]:
    """The glossary as one entry per term, in the file's own order.

    Each entry carries its own term, so nothing on the way back is read from a filename.
    """
    return [{"term": term, **entry} for term, entry in json.loads(raw).items()]


def assemble(terms: list[dict]) -> str:
    """The terms back into the bytes the engine reads. Reformatting is the one thing forbidden here."""
    out: dict[str, dict] = {}
    for entry in terms:
        term = entry["term"]
        if term in out:
            raise GlossaryError(f"`{term}` is defined by two term files - a term has one home")
        out[term] = {key: value for key, value in entry.items() if key != "term"}
    return json.dumps(out, **_DUMP) + "\n"


def write_term_files(root: str | None = None) -> list[str]:
    """The one-time split: `glossary.json` into one file per term. Refuses to leave a split behind
    that does not assemble back to the same bytes."""
    base = root or _HERE
    with open(_source_of(base), encoding="utf-8") as fh:
        raw = fh.read()
    here = os.path.join(base, TERMS)
    os.makedirs(here, exist_ok=True)
    written = []
    for position, entry in enumerate(split(raw), start=1):
        name = file_name(position, entry["term"])
        with open(os.path.join(here, name), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, **_DUMP) + "\n")
        written.append(os.path.join(TERMS, name))
    rebuilt = assemble(term_files(base))
    if rebuilt != raw:
        raise GlossaryError(f"the split does not assemble back to the same bytes ({_first_difference(raw, rebuilt)}) - the term files in {TERMS}/ are wrong and must not be committed")
    return written


def term_files(root: str | None = None) -> list[dict]:
    """Every term file, in prefix order, with every refusal checked.

    A file it does not recognize is a refusal and never a skip: a skipped term is a word that quietly
    stops being defined, and nothing on the page would say so.
    """
    base = root or _HERE
    here = os.path.join(base, TERMS)
    if not os.path.isdir(here):
        raise GlossaryError(f"{TERMS}/: no term files - run `make glossary SPLIT=1`")
    seen: dict[int, str] = {}
    out = []
    for name in sorted(os.listdir(here)):
        term_of(name)  # refuses a stray file by its name
        at = position_of(name)
        if at in seen:
            raise GlossaryError(f"{TERMS}/: {seen[at]} and {name} both claim prefix {at:0{DIGITS}d} - the assembly will not choose between them")
        seen[at] = name
        with open(os.path.join(here, name), encoding="utf-8") as fh:
            entry = json.load(fh)
        # COMPARED IN THE ENCODE DIRECTION (the plan review, 2026-09-20): decoding a filename is not
        # injective the moment a term contains a `%`, while encoding a term is exact forever.
        if name != file_name(at // GAP, str(entry.get("term"))):
            raise GlossaryError(f"{TERMS}/{name}: its filename says `{term_of(name)}` and its content says `{entry.get('term')}` - one of the two is wrong")
        out.append(entry)
    return out


def check(root: str | None = None, index: str | None = None) -> list[str]:
    """The committed files that differ from what the term files assemble, as messages."""
    base = root or _HERE
    if not os.path.isdir(os.path.join(base, TERMS)):
        return []  # not split yet - a stage that has not landed
    with open(_source_of(base), encoding="utf-8") as fh:
        committed = fh.read()
    terms = term_files(base)
    stale = [] if committed == assemble(terms) else [os.path.join("assets", "glossary.json")]
    where = index or index_path(root)
    if _read(where) != variant_index(terms):
        stale.append(os.path.relpath(where, base))
    return stale


def variant_index(terms: list[dict]) -> str:
    """Every variant and the term that owns it, as the one small DERIVED file a check reads.

    This is what answers "is this word already defined, and by which term?" in one lookup. A grep over
    the term files does NOT answer it - measured by the spec review of 2026-09-20, `windlass` matches
    three term files and `water mouth` three, because a definition may mention a word another term
    owns. The directory listing answers the narrower question (is this word itself a term); this file
    answers the one VOCABULARY actually asks.
    """
    out: dict[str, str] = {}
    for entry in terms:
        for variant in entry["variants"]:
            out[variant.lower()] = entry["term"]
    # ONE LINE PER VARIANT, not JSON. Measured: 22,564 bytes against 30,820 for the same content as
    # `indent=1` JSON and 27,282 compact. The whole point of this file is the bytes it costs a check
    # to read, and a tab-separated line is the cheapest form that is still plainly readable.
    return "".join(f"{variant}\t{term}\n" for variant, term in sorted(out.items()))


def index_path(root: str | None = None) -> str:
    """Beside the derived script the record's pages load, which is where a check already looks."""
    base = root or _HERE
    return os.path.normpath(os.path.join(base, "..", "..", "..", "research", "assets", "glossary-variants.txt"))


def write_index(root: str | None = None, index: str | None = None) -> int:
    want = variant_index(term_files(root))
    path = index or index_path(root)
    if _read(path) == want:
        return 0
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(want)
    return 1


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def write_source(root: str | None = None) -> int:
    """Write `glossary.json` from the term files. Returns 1 if it changed, 0 if it was already right."""
    base = root or _HERE
    want = assemble(term_files(base))
    path = _source_of(base)
    with open(path, encoding="utf-8") as fh:
        if fh.read() == want:
            return 0
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(want)
    return 1


def _source_of(base: str) -> str:
    return os.path.join(base, "assets", "glossary.json")


def _first_difference(want: str, got: str) -> str:
    for at, (a, b) in enumerate(zip(want, got, strict=False)):
        if a != b:
            return f"first difference at character {at}: {want[at : at + 40]!r} against {got[at : at + 40]!r}"
    return f"one is {len(want)} characters and the other {len(got)}"
