#!/usr/bin/env python3
"""Which About-form modals owe the modal checks (feature 319, plan D6) - folded into `_record_owed.py`, so `make record-owed`,
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

    _modal_owed.py [--root DIR]     the owed units, one a line
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import pathlib
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

SKILL = ".claude/skills/diagram"
MODAL_DIRS = (f"{SKILL}/l7r/diagram/interactive/classes", f"{SKILL}/l7r/diagram/interactive/compound_kinds")
RESEARCH = f"{SKILL}/research"
FORM_CHECK = "modal-form"
RESEARCH_CHECKS = ("modal-accuracy", "modal-references", "modal-gaps")
#: the Depiction tab's check (plan D13): owed by the tab's words, its Drawing: list, or a page that list names
DEPICTION_CHECK = "modal-depiction"
#: the defined agent that answers the three research units (plan D4)
RESEARCH_AGENT = "modal-research"
_TAG = re.compile(r"^(What|Why|Note|Caveat|About|Guesses|Depiction|Name|Covers|Label|Sources|Entry|Drawing|Form):\s?(.*)$")
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
        registry = "sheet" if ("/modals/sheet/" in self.origin or "compound_kinds" in self.origin) else "hamlet"
        return f"{registry}/{re.sub(r'[^a-z0-9-]', '-', self.key.lower())}"

    @property
    def prose(self) -> str:
        return "\n".join(self.tags.get(t, "") for t in ("Name", "About", "Guesses", "Form"))

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
            joined[tag] = "\n\n".join(" ".join(p.split()) for p in joined[tag].split("\n\n") if p.strip())
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
MODALS = f"{SKILL}/l7r/diagram/interactive/assets/modals"


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
        key = next((n.value.value for n in node.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "key" for t in n.targets) and isinstance(n.value, ast.Constant)), None)
        if isinstance(key, str):
            out.append((node.name, key, node.lineno, ast.get_docstring(node) or ""))
    return out


def modals_in(source: str, path: str, read: Callable[[str], str | None] = lambda _f: None, about_only: bool = True) -> list[Modal]:
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
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else ""


def _read_now(root: pathlib.Path) -> Callable[[str], str | None]:
    return lambda f: (root / f).read_text(encoding="utf-8") if (root / f).is_file() else None


def _read_at(root: pathlib.Path, rev: str) -> Callable[[str], str | None]:
    def read(f: str) -> str | None:
        p = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{f}"], capture_output=True, text=True, check=False)
        return p.stdout if p.returncode == 0 else None

    return read


def modals_now(root: pathlib.Path, about_only: bool = True) -> list[Modal]:
    out = []
    for d in MODAL_DIRS:
        for p in sorted((root / d).glob("*.py")):
            out += modals_in(p.read_text(encoding="utf-8"), str(p.relative_to(root)), _read_now(root), about_only)
    return out


def modals_at(root: pathlib.Path, rev: str) -> dict[str, Modal]:
    out = {}
    for d in MODAL_DIRS:
        for name in _git(root, "ls-tree", "--name-only", rev, d + "/").split():
            if name.endswith(".py"):
                # keyed by registry and key: a sheet's `well` and a hamlet's `well` are two modals
                for m in modals_in(_git(root, "show", f"{rev}:{name}"), name, _read_at(root, rev)):
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


def digest(parts: Sequence[str]) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def _pages(root: pathlib.Path, files: Sequence[str]) -> list[str]:
    return [page_words((root / SKILL / f).read_text(encoding="utf-8")) if (root / SKILL / f).is_file() else "" for f in files]


def fingerprints(root: pathlib.Path, m: Modal) -> tuple[str, str]:
    """(the form units' fingerprint, the research units' fingerprint): the modal's words, and those plus its Entry pages'."""
    return digest([m.uid, m.prose, m.entry]), digest([m.uid, m.prose, m.entry, *_pages(root, m.entry_files())])


def depiction_fingerprint(root: pathlib.Path, m: Modal) -> str:
    """The Depiction unit's fingerprint (plan D13): the modal's About and Depiction words, its Drawing: list and those pages."""
    return digest([m.uid, m.prose, m.depiction, *_pages(root, m.drawing_files())])


def owed(root: pathlib.Path, base: str) -> list[tuple[str, str, str]]:
    """(slug, occasion, fingerprint) for every unit an About-form modal owes against `base`."""
    before = modals_at(root, base) if base else {}
    changed_pages = set(_git(root, "diff", "--name-only", base, "--", f"{RESEARCH}/questions").split()) if base else set()
    changed_pages |= set(_git(root, "ls-files", "--others", "--exclude-standard", "--", f"{RESEARCH}/questions").split())
    rows = []
    for m in modals_now(root):
        was = before.get(m.uid)
        fp_form, fp_research = fingerprints(root, m)
        moved_text = was is None or was.prose != m.prose or was.entry != m.entry
        moved_pages = [f for f in m.entry_files() if f"{SKILL}/{f}" in changed_pages]
        if moved_text:
            why = "new to the About form" if was is None else "its About, Guesses or Entry changed"
            rows.append((f"{FORM_CHECK}:{m.uid}", why, fp_form))
            rows += [(f"{c}:{m.uid}", why, fp_research) for c in RESEARCH_CHECKS]
        elif moved_pages:
            why = f"a page its Entry names moved ({' '.join(pathlib.Path(f).name for f in moved_pages)})"
            rows += [(f"{c}:{m.uid}", why, fp_research) for c in RESEARCH_CHECKS]
        # THE DEPICTION TAB (plan D13): owed by ANY change to the modal - new to the About form, its About, Guesses, Entry,
        # Depiction or Drawing - and by a page its Drawing: names moving, WHETHER OR NOT the modal has the tab (the plan review,
        # 2026-10-04: a conversion that dropped its drawing pages from Entry: and wrote no Depiction: would otherwise land with
        # its conventions and drawing links silently gone, every check green - the case FR-014 and SC-008 exist to catch)
        moved_drawing = [f for f in m.drawing_files() if f"{SKILL}/{f}" in changed_pages]
        if moved_text or was.depiction != m.depiction:
            rows.append((f"{DEPICTION_CHECK}:{m.uid}", "new to the About form" if was is None else "the modal or its Depiction tab changed", depiction_fingerprint(root, m)))
        elif moved_drawing:
            rows.append((f"{DEPICTION_CHECK}:{m.uid}", f"a page its Drawing: names moved ({' '.join(pathlib.Path(f).name for f in moved_drawing)})", depiction_fingerprint(root, m)))
    return rows


def about_keys(root: pathlib.Path) -> set[str]:
    """The keys of every About-form modal - `_record_owed._entry_units` owes them no entry-drift."""
    return {m.key for m in modals_now(root)}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    import _record_owed as ro  # noqa: PLC0415

    for slug, why, _fp in owed(root, ro.merge_base(root)):
        print(f"{slug}  - {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
