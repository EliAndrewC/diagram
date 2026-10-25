#!/usr/bin/env python3
"""Which About-form modals owe the modal checks (feature 319, plan D6) - folded into `record_owed.py`, so `make record-owed`,
`make record-checked` and the push's record gate (`entry-gate.sh`) treat them as they treat the record checks.

WHY. The GM, 2026-10-03: the modal guidelines *"should be reviewed by subagents in more or less the same way that our research
is ... certainly for accuracy, and consistency with the research"*. A check is owed where the words it reads changed (feature
311), never on a whole-registry sweep:

- `modal-form:<key>` - the class's About, Guesses or Entry text differs from the merge base (or the class is new to the About
  form). `modal-form` reads only the modal and the guidelines.
- `modal-accuracy:<key>`, `modal-references:<key>`, `modal-gaps:<key>` - the same, OR a research page its `Entry:` names
  changed its words. All three are answered by one `modal-research` dispatch (plan D4: one agent, three verdicts).

An About-form class is no longer owed `entry-drift` (`_record_owed._entry_units` drops it): `modal-accuracy` asks entry-drift's
question and more. An old-form class keeps entry-drift until the rollout converts it.

    modal_owed.py [--root DIR]     the owed units, one a line
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path[1:1] = [str((pathlib.Path(__file__).resolve().parent / _d).resolve()) for _d in ('../reviews',)]  # the moved scripts it imports (2026-10-08)
from moves import moved_only  # noqa: E402  (feature 329: a page the delta only moved changed no word)
import record_cache as rc  # noqa: E402  (feature 375 amendment 3: one git batch per revision)
from collections.abc import Callable, Sequence
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

MODAL_DIRS = (
    "l7r/diagram/interactive/classes",
    "l7r/diagram/interactive/compound_kinds",
)
RESEARCH = "research"
FORM_CHECK = "modal-form"
RESEARCH_CHECKS = ("modal-accuracy", "modal-references", "modal-gaps")
#: the Depiction tab's check (plan D13): owed by the tab's words, its Drawing: list, or a page that list names
DEPICTION_CHECK = "modal-depiction"
#: the defined agent that answers the three research units (plan D4)
RESEARCH_AGENT = "modal-research"
#: A POP-UP'S CHECKS RUN IN THIS ORDER (feature 375 amendment 3, FR-019; the GM 2026-10-11, a speculative fix measured after:
#: "perhaps it's worth trying to make the speculative fix and measuring it afterwards"). Run together, each check's applied
#: edits re-owed the other two, and every second and third round on 374's and 352's pop-ups was owed by the pop-up's own
#: words moving (specs/375-enforced-wave-process/research.md R2). Form first - its edits can carry a fact, so the substance
#: checks read its words; depiction last - it reads the `Entry:` (its candidate drawing pages), which a research round may move. A
#: check's bundle waits for the checks before it (`modal_bundle.order_hold`), and a round's applied edits settle the checks
#: before it (`apply_edits.Round`), never the ones after, which read the edited words next.
ORDER = (FORM_CHECK, RESEARCH_AGENT, DEPICTION_CHECK)
#: the units each check of ORDER answers
AGENT_UNITS = {FORM_CHECK: (FORM_CHECK,), RESEARCH_AGENT: RESEARCH_CHECKS, DEPICTION_CHECK: (DEPICTION_CHECK,)}


def agent_of(unit_check: str) -> str:
    """The check of ORDER that answers a unit's check (`modal-gaps` -> `modal-research`), or ''."""
    return next((a for a, units in AGENT_UNITS.items() if unit_check in units), "")


def earlier_units(unit_checks: Sequence[str]) -> tuple[str, ...]:
    """The unit checks of every check BEFORE the one answering `unit_checks` in ORDER; () unless they are one check's."""
    agents = {agent_of(c) for c in unit_checks}
    if len(agents) != 1 or "" in agents:
        return ()
    return tuple(c for a in ORDER[: ORDER.index(agents.pop())] for c in AGENT_UNITS[a])
_TAG = re.compile(
    r"^(What|Why|Note|Caveat|About|Guesses|Depiction|Name|Covers|Label|Sources|Entry|Drawing|Form):\s?(.*)$"
)
_PARAGRAPHED = ("About", "Depiction")
_PATH = re.compile(r"research/questions/[^\s,;]+?\.html")


@dataclass(frozen=True)
class Modal:
    """One About-form modal class as its source states it - the parts the checks read."""

    cls: str  # the class name, qualified by module where two modules share it
    key: str  # the class key the page uses
    origin: str  # file:line
    tags: dict[str, str]
    doc: str = ""  # the docstring as written, line for line - what an EDIT block quotes

    @property
    def uid(self) -> str:
        """`<hamlet|sheet>/<slug>` - the modal's file stem under its registry, and the subject of its owed units: two
        registries may share a key (a sheet's `well`, a hamlet's `well`), never a uid."""
        if (
            "/modals/choice/" in self.origin
        ):  # a title-card choice's modal (plan D10): no class, its file is its name
            return f"choice/{pathlib.Path(self.origin).stem}"
        registry = (
            "sheet"
            if ("/modals/sheet/" in self.origin or "compound_kinds" in self.origin)
            else "hamlet"
        )
        return f"{registry}/{re.sub(r'[^a-z0-9-]', '-', self.key.lower())}"

    @property
    def prose(self) -> str:
        return "\n".join(
            self.tags.get(t, "") for t in ("Name", "About", "Guesses", "Form")
        )

    @property
    def entry(self) -> str:
        return self.tags.get("Entry", "")

    @property
    def form(self) -> str:
        return self.tags.get("Form", "standard") or "standard"

    def entry_files(self) -> list[str]:
        return list(dict.fromkeys(_PATH.findall(self.entry)))

    @property
    def depiction(self) -> str:
        """The Depiction tab's words and its drawing pages (plan D13) - what `modal-depiction` reads of the modal."""
        return "\n".join(self.tags.get(t, "") for t in ("Depiction", "Drawing"))

    def drawing_files(self) -> list[str]:
        return list(dict.fromkeys(_PATH.findall(self.tags.get("Drawing", ""))))


def parse_tags(doc: str) -> dict[str, str]:
    """A class docstring's tags, each value its lines - `About:` keeps a blank line between paragraphs as `\\n\\n` and
    `Guesses:` its bullets one to a line, as `classes/_base.py` reads them (this is tooling; it must not import the engine)."""
    out: dict[str, list[str]] = {}
    cur = None
    for raw in doc.splitlines():
        line = raw.strip()
        m = _TAG.match(line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(2)] if m.group(2) else []
        elif cur is not None and (line or cur in _PARAGRAPHED):
            out[cur].append(line)
    joined = {}
    for tag, lines in out.items():
        if tag in _PARAGRAPHED:
            joined[tag] = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
            joined[tag] = "\n\n".join(
                " ".join(p.split()) for p in joined[tag].split("\n\n") if p.strip()
            )
        elif tag == "Guesses":
            bullets: list[list[str]] = []
            for line in lines:
                if line.startswith("- ") or not bullets:
                    bullets.append([line])
                else:
                    bullets[-1].append(line)
            joined[tag] = "\n".join(" ".join(b) for b in bullets)
        else:
            joined[tag] = " ".join(lines).strip()
    return joined


#: one file per modal (plan D12): `<MODALS>/<hamlet|sheet>/<slug of the key>.md`, as `classes/_base.modal_path` places them
MODALS = "l7r/diagram/interactive/assets/modals"


def modal_file(py_path: str, key: str) -> str:
    """The modal file (repository-relative) of the kind `key` defined in the module at `py_path`."""
    registry = "sheet" if "compound_kinds" in py_path else "hamlet"
    return f"{MODALS}/{registry}/{re.sub(r'[^a-z0-9-]', '-', key.lower())}.md"


def kinds_in(source: str) -> list[tuple[str, str, int, str]]:
    """(class name, key, line, docstring) of every class in a module's source that sets a string `key`."""
    out = []
    for node in ast.parse(source).body:
        if not isinstance(node, ast.ClassDef):
            continue
        key = next(
            (
                n.value.value
                for n in node.body
                if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "key" for t in n.targets)
                and isinstance(n.value, ast.Constant)
            ),
            None,
        )
        if isinstance(key, str):
            out.append((node.name, key, node.lineno, ast.get_docstring(node) or ""))
    return out


def modals_in(
    source: str,
    path: str,
    read: Callable[[str], str | None] = lambda _f: None,
    about_only: bool = True,
) -> list[Modal]:
    """The modals of one module's source - each kind's text from its modal file (`read` it, by repository-relative path),
    or its docstring where it has no file (a revision before plan D12). `about_only`: only the About form's."""
    out = []
    for cls, key, line, doc in kinds_in(source):
        f = modal_file(path, key)
        text = read(f)
        origin = f if text is not None else f"{path}:{line}"
        text = doc if text is None else text
        tags = parse_tags(text)
        if about_only and "About" not in tags:
            continue
        if not tags:
            continue
        out.append(Modal(f"{pathlib.Path(path).stem}.{cls}", key, origin, tags, text))
    return out


def _git(root: pathlib.Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    return p.stdout if p.returncode == 0 else ""


def _read_now(root: pathlib.Path) -> Callable[[str], str | None]:
    return lambda f: (
        (root / f).read_text(encoding="utf-8") if (root / f).is_file() else None
    )


def _read_at(root: pathlib.Path, rev: str) -> Callable[[str], str | None]:
    """The files at `rev`: the modals' directories by one listing and one `git cat-file --batch` (feature 375 amendment 3,
    plan D28 - one `git show` per file was 299 processes at the base of 374's delta), any other path by its own `git show`."""
    return rc.RevReader(root, rev, (*MODAL_DIRS, MODALS))


def choice_modal(path: str, text: str, about_only: bool = True) -> Modal | None:
    """A title-card choice's modal (plan D10) from its file: no class defines it, so its file stem is its key."""
    tags = parse_tags(text)
    if not tags or (about_only and "About" not in tags):
        return None
    stem = pathlib.Path(path).stem
    return Modal(f"choice.{stem}", stem, path, tags, text)


def modals_now(root: pathlib.Path, about_only: bool = True) -> list[Modal]:
    out = []
    for d in MODAL_DIRS:
        for p in sorted((root / d).glob("*.py")):
            out += modals_in(
                p.read_text(encoding="utf-8"),
                str(p.relative_to(root)),
                _read_now(root),
                about_only,
            )
    for p in sorted((root / MODALS / "choice").glob("*.md")):
        m = choice_modal(
            str(p.relative_to(root)), p.read_text(encoding="utf-8"), about_only
        )
        if m is not None:
            out.append(m)
    return out


def modals_at(
    root: pathlib.Path, rev: str, about_only: bool = True
) -> dict[str, Modal]:
    """The modals at `rev`, keyed by uid; `about_only=False` takes the old form's too (the drawing pages a docstring listed)."""
    out = {}
    read = _read_at(root, rev)
    for d in MODAL_DIRS:
        for name in read.names(d):
            if name.endswith(".py"):
                # keyed by registry and key: a sheet's `well` and a hamlet's `well` are two modals
                for m in modals_in(read(name) or "", name, read, about_only):
                    out[m.uid] = m
    for name in read.names(MODALS + "/choice"):
        if name.endswith(".md"):
            m = choice_modal(name, read(name) or "", about_only)
            if m is not None:
                out[m.uid] = m
    return out


def find(root: pathlib.Path, kind: str) -> Modal | None:
    """An About-form modal by class name (`Farmhouse`, or `homestead.Farmhouse`) or key (`farmhouse`)."""
    for m in modals_now(root):
        if kind in (m.uid, m.key, m.cls, m.cls.split(".", 1)[1]):
            return m
    return None


def page_words(text: str) -> str:
    """A research page's words for a fingerprint: comments out, whitespace folded."""
    return " ".join(re.sub(r"<!--.*?-->", "", text, flags=re.S).split())


#: A money mark (feature 413's tooltip, `record/money.py`) around an amount's own words: markup, never a word.
_MONEY_MARK = re.compile(r'<span class="money"[^>]*>(.*?)</span>', re.S)


def page_words_unmarked(text: str) -> str:
    """`page_words` with every money mark unwrapped to the words inside it: a page whose amounts were only marked did not
    move (feature 412's marks pass, 2026-10-24: marking 0185's lodging fees made six pop-ups owe a triage of words that
    had not changed)."""
    return page_words(_MONEY_MARK.sub(r"\1", text))


def digest(parts: Sequence[str]) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def _pages(root: pathlib.Path, files: Sequence[str]) -> list[str]:
    return [
        page_words((root / f).read_text(encoding="utf-8"))
        if (root / f).is_file()
        else ""
        for f in files
    ]


def fingerprints(root: pathlib.Path, m: Modal) -> tuple[str, str]:
    """(the form units' fingerprint, the research units' fingerprint): the modal's words, and those plus its Entry pages'."""
    return digest([m.uid, m.prose, m.entry]), digest(
        [m.uid, m.prose, m.entry, *_pages(root, m.entry_files())]
    )


def depiction_fingerprint(root: pathlib.Path, m: Modal) -> str:
    """The Depiction unit's fingerprint: what `modal-depiction` judges (feature 375 amendment 6, FR-028) - the Entry: list (its
    drawing candidates), the Depiction tab, the Drawing: list and those pages. Not Guesses, Name or Form (amendment 1: with them
    in it, a Guesses edit after the check had answered re-owed it in full), and not About since amendment 6: a drawing statement
    in About is `modal-form`'s finding (M13), and 43 of 221 pop-up edits since 2026-10-05 changed About alone, each re-owing an
    Opus depiction round (specs/375-enforced-wave-process/research.md R6)."""
    return digest([m.uid, m.entry, m.depiction, *_pages(root, m.drawing_files())])


def amendment1_depiction_fingerprint(root: pathlib.Path, m: Modal) -> str:
    """The depiction fingerprint as amendment 1 computed it, About in it: what every depiction answer recorded from 2026-10-10 to
    amendment 6 holds. Read by `record_owed.amendment1_depiction_answered`, so dropping About re-owed no answer by itself."""
    return digest([m.uid, m.tags.get("About", ""), m.entry, m.depiction, *_pages(root, m.drawing_files())])


def depiction_owed_by(was: Modal | None, m: Modal) -> bool:
    """Whether an edit from `was` to `m` owes `modal-depiction` (feature 375 amendment 6, FR-028): the pop-up new to the About
    form, or its Depiction tab or `Drawing:` list (`Modal.depiction`), or its `Entry:` changed - not its About."""
    return was is None or was.depiction != m.depiction or was.entry != m.entry


def legacy_depiction_fingerprint(root: pathlib.Path, m: Modal) -> str:
    """The depiction fingerprint as it was computed before feature 375 amendment 1 (the modal's prose - Name, About, Guesses,
    Form - its Depiction and its Drawing: pages): what every depiction answer recorded before that change holds. Read by
    `record_owed.legacy_depiction_answered`, so the formula change did not re-owe answers to words that had not moved."""
    return digest([m.uid, m.prose, m.depiction, *_pages(root, m.drawing_files())])


def owed(root: pathlib.Path, base: str, uid: str = "") -> list[tuple[str, str, str]]:
    """(slug, occasion, fingerprint) for every unit an About-form modal owes against `base`; `uid` scopes it to one pop-up."""
    before = modals_at(root, base) if base else {}
    changed_pages = (
        set(
            _git(
                root, "diff", "--name-only", base, "--", f"{RESEARCH}/questions"
            ).split()
        )
        if base
        else set()
    )
    changed_pages |= set(
        _git(
            root,
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            f"{RESEARCH}/questions",
        ).split()
    )
    # A PAGE MOVED WHEN ITS WORDS DID (2026-10-05): the units' fingerprints read `page_words`, but a page counted as moved on any
    # byte - a comment or a re-wrap made every modal naming it owed, and `test-entry-gate.sh`'s "a comment and a re-wrap owe
    # nothing" went red on main. A page changed in git is moved only if its words differ from the base's.
    if base:
        changed_pages -= moved_only(root, base, sorted(changed_pages))
        listed = sorted(changed_pages)
        old = dict(zip(listed, rc.cat_blobs(root, [f"{base}:{f}" for f in listed]), strict=True))  # one batch (plan D28)
        changed_pages = {
            f
            for f in changed_pages
            if page_words_unmarked(old.get(f, ""))
            != page_words_unmarked(
                (root / f).read_text(encoding="utf-8") if (root / f).is_file() else ""
            )
        }
    rows = []
    for m in modals_now(root):
        if uid and m.uid != uid:
            continue
        was = before.get(m.uid)
        fp_form, fp_research = fingerprints(root, m)
        moved_text = was is None or was.prose != m.prose or was.entry != m.entry
        moved_pages = [f for f in m.entry_files() if f in changed_pages]
        if moved_text:
            why = (
                "new to the About form"
                if was is None
                else "its About, Guesses or Entry changed"
            )
            rows.append((f"{FORM_CHECK}:{m.uid}", why, fp_form))
            rows += [(f"{c}:{m.uid}", why, fp_research) for c in RESEARCH_CHECKS]
        elif moved_pages:
            why = f"a page its Entry names moved ({' '.join(pathlib.Path(f).name for f in moved_pages)})"
            rows += [(f"{c}:{m.uid}", why, fp_research) for c in RESEARCH_CHECKS]
        # THE DEPICTION TAB (plan D13): owed by ANY change to the modal - new to the About form, its About, Guesses, Entry,
        # Depiction or Drawing - and by a page its Drawing: names moving, WHETHER OR NOT the modal has the tab (the plan review,
        # 2026-10-04: a conversion that dropped its drawing pages from Entry: and wrote no Depiction: would otherwise land with
        # its conventions and drawing links silently gone, every check green - the case FR-014 and SC-008 exist to catch)
        # FEATURE 375 AMENDMENT 1 (FR-015; the GM 2026-10-10): owed by the words the check READS - new to the About form, its
        # Depiction tab or Drawing: list, its About (drawing statements that belong in Depiction) or its Entry: (the candidate
        # drawing pages `modal_bundle.drawing_candidates` builds from it, the case above). A Guesses, Name or Form edit alone owes
        # `modal-form` and the research checks, not this one: 343's run re-checked depiction on such edits.
        # FEATURE 375 AMENDMENT 6 (FR-028; the GM 2026-10-12): and not About - its drawing statements are `modal-form`'s (M13).
        # An edit that does not owe the check is not dispatched, so it adds no round to the check's count on the pop-up.
        moved_drawing = [
            f for f in m.drawing_files() if f in changed_pages
        ]
        if depiction_owed_by(was, m):
            rows.append(
                (
                    f"{DEPICTION_CHECK}:{m.uid}",
                    "new to the About form"
                    if was is None
                    else "its Depiction, Drawing: or Entry: changed",
                    depiction_fingerprint(root, m),
                )
            )
        elif moved_drawing:
            rows.append(
                (
                    f"{DEPICTION_CHECK}:{m.uid}",
                    f"a page its Drawing: names moved ({' '.join(pathlib.Path(f).name for f in moved_drawing)})",
                    depiction_fingerprint(root, m),
                )
            )
    return rows


def about_keys(root: pathlib.Path) -> set[str]:
    """The keys of every About-form modal - `_record_owed._entry_units` owes them no entry-drift."""
    return {m.key for m in modals_now(root)}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    import record_owed as ro  # noqa: PLC0415

    for slug, why, _fp in owed(root, ro.merge_base(root)):
        print(f"{slug}  - {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
