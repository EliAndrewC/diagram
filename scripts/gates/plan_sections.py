#!/usr/bin/env python3
"""A plan read for its review (split from `plan_gate.py` at the 1,000-line bar, 2026-10-24, when 405 T26's fix to
`task_sections` took it to 1,028 lines): each task's section and each block of a plan, their digests and the history that
holds a block's earlier text, a typo told from a change, and which blocks a review still owes. `plan_gate` re-exports every
name, so `plan_gate.task_sections` and the rest still resolve."""

from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan_seen  # noqa: E402 - the reviewed blocks' texts (405 T102)
import wording  # noqa: E402 - the module beside this one (feature 385 T118)

#: Words a "typo" may never touch (feature 375 FR-005(b), plan D6): a number, a quantity, a negation or a quantifier changes a
#: decision however few letters it moves - "two" -> "ten", "all" -> "any", "must" -> "may".
GUARDED = frozenset(
    [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "hundred",
        "thousand",
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
        "ninth",
        "tenth",
        "half",
        "twice",
        "once",
        "double",
        "triple",
        "not",
        "no",
        "never",
        "none",
        "except",
        "unless",
        "only",
        "all",
        "any",
        "each",
        "every",
        "some",
        "few",
        "many",
        "most",
        "more",
        "less",
        "fewer",
        "may",
        "must",
        "should",
        "shall",
        "can",
        "cannot",
        "before",
        "after",
        "above",
        "below",
        "over",
        "under",
        "min",
        "max",
        "least",
    ]
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


#: How many words a typo-scale edit may change in the whole plan
TYPO_WORDS = 3
_WORD = re.compile(r"[A-Za-z0-9]+")


def _distance(a: str, b: str) -> int:
    """The Damerau-Levenshtein distance of two short words (a transposition is one edit)."""
    prev2: list[int] = []
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            if i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[-1]


def typo_only(old: str, new: str) -> bool:
    """Whether `new` differs from `old` by typos alone (FR-005(b), plan D6): whitespace, re-wrapping, case and punctuation; at
    most TYPO_WORDS words replaced, each by a near spelling (one letter for a word of four or fewer, two beyond), none of them a
    digit or a GUARDED word; no word added or removed. Anything else adds or changes a decision, and voids the verdict - the
    conservative side, since a missed decision is the incident this gate exists for (feature 239)."""
    a, b = _WORD.findall(old.lower()), _WORD.findall(new.lower())
    if len(a) != len(b):
        return False
    changed = [(x, y) for x, y in zip(a, b, strict=True) if x != y]
    if len(changed) > TYPO_WORDS:
        return False
    for x, y in changed:
        if x in GUARDED or y in GUARDED or any(c.isdigit() for c in x + y):
            return False
        if _distance(x, y) > (1 if min(len(x), len(y)) <= 4 else 2):
            return False
    return True


_HEAD = re.compile(r"^(#{2,4})\s+(.*)$", re.M)
_TASK_ID = re.compile(r"\b(T\d+[a-z]?)\b")


def task_sections(plan_text: str) -> dict[str, str]:
    """`{task id: its section}` - every `##`-`####` heading of the plan naming a task id, to the next heading at its level or
    above (feature 375, FR-003(a), plan D3): the decisions of that task, which a decision preflight rules on alone."""
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in _HEAD.finditer(plan_text)]
    own: dict[str, list[tuple[int, int]]] = {}
    mentioned: dict[str, str] = {}
    for i, (at, level, title) in enumerate(heads):
        ids = _TASK_ID.findall(title)
        if not ids:
            continue
        end = next((a for a, lv, _t in heads[i + 1 :] if lv <= level), len(plan_text))
        # A TASK'S OWN HEADING WINS (feature 385 T56): a title that BEGINS with the id is that task's section; one that only
        # names it - the umbrella "T04 to T10 - T48, T47's patch, five ranking rows" - took T10's, T47's and T48's preflights
        lead = _TASK_ID.match(title.strip())
        for t in ids:
            if lead and lead.group(0) == t:
                # ...AND EVERY ONE OF ITS OWN HEADINGS COUNTS (the GM 2026-10-24, 405 T26): T26's five `### T26 ...` blocks
                # stand under no `## T26` heading, and only the first - its 10-21 part A - was ever bundled for review, so
                # its re-answered Approaches and its Decisions (D131) reached no reviewer. A block inside one already kept
                # (a `### T07 ...` under `## T07 - ...`) is not counted twice.
                spans = own.setdefault(t, [])
                if not any(a <= at and end <= b for a, b in spans):
                    spans.append((at, end))
            else:
                mentioned.setdefault(t, plan_text[at:end])
    return {**mentioned, **{t: "".join(plan_text[a:b] for a, b in spans) for t, spans in own.items()}}


def task_current(review: dict, plan_text: str, task: str, history: History | None = None) -> bool:
    """Whether the task's section carries a CLEAR decision verdict that still matches it (a typo aside, as D6) - its earlier
    text from the record where an old record kept it, else from the plan's history (amendment 11, D63)."""
    section = task_sections(plan_text).get(task)
    entry = (review.get("tasks") or {}).get(task) or {}
    if section is None or entry.get("verdict") != "CLEAR":
        return False
    if entry.get("section_sha256") == digest(section.encode()):
        return True
    section = ARCHIVE_LINE.sub("", section)  # T82 (plan D102): the archive's generated line owes no review, in a section too
    earlier = entry.get("section_text") or (history.section(task, str(entry.get("section_sha256"))) if history else None)
    # A QUIET PART B LEAVES THE SECTION REVIEWED (feature 385 T80, plan D99): T75 skips the part B itself, but adding it moved the
    # section's digest and T78's other three blocks fell back to block reviews. Both texts are read without their quiet part Bs.
    if earlier is None:
        return False
    was, now = _quiet_out(ARCHIVE_LINE.sub("", str(earlier)), plan_text), _quiet_out(section, plan_text)
    archive = history.path.parent / "plan-done.md" if history and history.path else None
    done = archive.read_text(encoding="utf-8") if archive and archive.is_file() else ""
    return typo_only(was, now) or typo_only(repointed(was, now, task, plan_text + done), now)


def repointed(old: str, new: str, task: str, plan_text: str) -> str:
    """`old` with one task id renamed to the task a recorded split moved its work to, where that rename is the whole edit (the
    round arbiter's fix on hour:385-approach-checklist@28: T31 said "row 841 is T32" after the review moved the row to T95, and
    correcting the pointer would have owed T31 a third review). A split is RECORDED when the new id's own heading says it was
    "found working <task>" (`make task-add`'s found work), in the plan or its archive (`plan_text` with plan-done.md after it: a
    ticked split is archived); any other rename is returned unchanged, so it still owes a review."""
    splits = [t for t, sec in task_sections(plan_text).items() if t != task and re.search(rf"found working {re.escape(task)}\b", sec.split("\n", 1)[0])]
    for b in splits:
        for a in sorted(set(_TASK_ID.findall(old)) - {b, task}):
            cand = re.sub(rf"\b{re.escape(a)}\b", b, old)
            if typo_only(cand, new):
                return cand
    return old


def _quiet_out(section: str, plan_text: str) -> str:
    """The section without its part B blocks that decide nothing (`decides_nothing`)."""
    for key, body, _at in blocks(section):
        if decides_nothing(key, body, plan_text):
            section = section.replace(body, "")
    return section


def _without(plan_text: str, ids: set[str]) -> str:
    """The plan with the sections of `ids` taken out."""
    for t, sec in task_sections(plan_text).items():
        if t in ids:
            plan_text = plan_text.replace(sec, "")
    return plan_text


# ---- feature 375 amendment 11 (the GM 2026-10-13): a plan reviewed by its changed blocks -------------------------------------
#: "Is feature 374 growing too large in a way that eats tokens" - sixteen whole-plan reviews of 374 cost 13.7 million input
#: tokens, each re-judging every earlier decision because one edit outside a task's section staled the whole plan's verdict.
_ANY_HEAD = re.compile(r"^#{2,4}\s.*$", re.M)
#: the line `make plan-archive` leaves where finished sections were (FR-044): taken out of every digest, so it owes no review
ARCHIVE_LINE = re.compile(r"^<!-- plan-archive: [^\n]*? -->\n?", re.M)
HISTORY_CHUNK = 25  # versions of plan.md read per `cat-file --batch` while a block's earlier text is sought (D63)


def blocks(plan_text: str) -> list[tuple[str, str, int]]:
    """(key, text, offset) of every block (D60, FR-043): each heading line (`##` to `####`) to the next such heading, and the
    text before the first one (the title with it) as `preamble`. A repeated heading's key gets `#2`, `#3`."""
    heads = list(_ANY_HEAD.finditer(plan_text))
    out = [("preamble", plan_text[: heads[0].start()] if heads else plan_text, 0)]
    seen: dict[str, int] = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(plan_text)
        key = m.group(0).strip()
        seen[key] = seen.get(key, 0) + 1
        out.append((key if seen[key] == 1 else f"{key}#{seen[key]}", plan_text[m.start() : end], m.start()))
    return out


def block_digest(text: str) -> str:
    return digest(ARCHIVE_LINE.sub("", text).encode())


class History:
    """The texts of plan.md's earlier versions (D63), newest first, read in chunks of HISTORY_CHUNK by one `cat-file --batch`
    each, only as far back as a question needs - the whole history when the text sought is not there (the plan review: a cap
    of 60 would have dropped a typo's verdict on 374, whose plan already had 61 versions). Where nothing can be read (no git,
    no history) it knows nothing, and a block's earlier text found nowhere is no typo - the conservative side."""

    def __init__(self, plan_path: pathlib.Path | None, ref: str = "HEAD") -> None:
        self.path, self.ref = plan_path, ref
        self._revs: list[str] | None = None
        self._texts: list[str] = []

    def _git(self, *args: str, data: bytes | None = None) -> bytes:
        return subprocess.run(["git", "-C", str(self.path.parent), *args], input=data, capture_output=True).stdout  # type: ignore[union-attr]

    def texts(self):  # noqa: ANN201 - a generator of str
        if self.path is None or not self.path.parent.is_dir():
            return
        if self._revs is None:
            rel = self._git("ls-files", "--full-name", "--", self.path.name).decode().strip()
            rel = rel or self._git("rev-parse", "--show-prefix").decode().strip() + self.path.name
            self._rel = rel
            self._revs = self._git("log", "--format=%H", self.ref, "--", self.path.name).decode().split()
        yield from self._texts
        while len(self._texts) < len(self._revs):
            chunk = self._revs[len(self._texts) : len(self._texts) + HISTORY_CHUNK]
            got, i = self._git("cat-file", "--batch", data="".join(f"{r}:{self._rel}\n" for r in chunk).encode()), 0
            for _ in chunk:
                nl = got.find(b"\n", i)
                head = got[i:nl].split()
                if len(head) < 3 or head[1] == b"missing":
                    self._texts.append("")
                    i = nl + 1
                    continue
                size = int(head[2])
                self._texts.append(got[nl + 1 : nl + 1 + size].decode("utf-8", "replace"))
                i = nl + 1 + size + 1
            yield from self._texts[-len(chunk) :]

    def block(self, key: str, sha: str) -> str | None:
        """The text a block had when its digest was `sha`, as its verdict kept it or from the plan's history; None when neither holds it."""
        if self.path is not None and (kept := plan_seen.recall(self.path, sha)) is not None and block_digest(kept) == sha:
            return kept
        for text in self.texts():
            for k, body, _at in blocks(text):
                if k == key and block_digest(body) == sha:
                    return body
        return None

    def section(self, task: str, sha: str) -> str | None:
        for text in self.texts():
            sec = task_sections(text).get(task)
            if sec is not None and digest(sec.encode()) == sha:
                return sec
        return None


def reviewed_blocks(review: dict) -> dict[str, dict]:
    """`{key: {sha256, verdict}}` the record holds (D60): its `blocks`, or - a record from before amendment 11 - its one verdict on
    each block of the `plan_text` it reviewed."""
    if isinstance(review.get("blocks"), dict):
        return review["blocks"]
    text = review.get("plan_text")
    if not isinstance(text, str):
        return {}
    return {k: {"sha256": block_digest(body), "verdict": review.get("verdict"), "text": body} for k, body, _at in blocks(text)}


REMOVED = "(removed) "


_PART_B = re.compile(r"^### T\d+[a-z]?\s+part B \(")
_DEFINED = re.compile(r"^\*\*(D\d+[a-z]?) - ", re.M)


def decides_nothing(key: str, body: str, plan_text: str, done: str = "") -> bool:
    """A part B block that decides nothing (feature 385 T75, plan D94; the GM's approved change 3 of the 2026-10-18 step-back:
    "only one that adds a new decision gets a spec-fidelity review"): item 4 answered "No", item 5 "Neither", and every `D<n>` it
    names defined elsewhere. A rule changed, a number tuned or an earlier placement moved is a decision, labeled or not."""
    if not _PART_B.match(key):
        return False

    def answer(n: int) -> str:
        m = re.search(rf"^{n}\.\s+\*\*[^*]*\*\*\s*(.*)$", body, re.M)
        return m.group(1).strip().lower() if m else ""

    if not re.match(r"no\b", answer(4)) or not re.match(r"neither\b", answer(5)):
        return False
    return set(re.findall(r"\bD\d+[a-z]?\b", body)) <= set(_DEFINED.findall(plan_text.replace(body, "") + done))


_LANDS_OPEN = re.compile(r"^\*\*Lands open\*\*:.*$", re.M)


def lands_open_appended(earlier: str, body: str) -> str:
    """`body` with its `**Lands open**:` line put back as `earlier` had it, where the only change to the line is ids appended in
    order (feature 385 T74, plan D93; the round arbiter on hour:385-approach-checklist@24: two reviews in one hour of ids that
    `make task-add` had added); else `body` unchanged. A reorder, a dropped or a repeated id is a change."""
    was, now = _LANDS_OPEN.search(earlier), _LANDS_OPEN.search(body)
    if not was or not now:
        return body
    a, b = re.findall(r"\bT\d+[a-z]?\b", was.group(0)), re.findall(r"\bT\d+[a-z]?\b", now.group(0))
    if b[: len(a)] != a or len(set(b)) != len(b):
        return body
    return body[: now.start()] + was.group(0) + body[now.end() :]


def block_status(review: dict, plan_text: str, ruled: set[str], history: History | None = None, done: str = "") -> tuple[list[str], list[str]]:
    """(the blocks owed a review, the blocks BLOCKED): every block outside a task section with its own current verdict, judged
    against the record's verdict at its digest, a typo-scale change (FR-005(b)) from its text at that digest aside. A recorded
    block that plan.md no longer has is owed too, as `(removed) <key>`, unless `plan-done.md` (`done`) holds it - the archive
    moved it (the plan review: a decision deleted by hand is a change like any other)."""
    out_of = [(plan_text.find(sec), plan_text.find(sec) + len(sec)) for t, sec in task_sections(plan_text).items() if t in ruled]
    # ...AND A WORDING-ONLY SECTION BUT ITS PART Bs (feature 385 T118, D137): its Decisions block declares nothing decided; `make
    # tick` checks its commits against that (`wording.refusal`), and a part B that decides goes on to review as any other
    words = [(plan_text.find(sec), plan_text.find(sec) + len(sec)) for _t, sec in task_sections(plan_text).items() if wording.wording_only(sec)]
    have = reviewed_blocks(review)
    owed, blocked = [], []
    for key, body, at in blocks(plan_text):
        if any(lo <= at < hi for lo, hi in out_of if lo >= 0):
            continue
        if not _PART_B.match(key) and any(lo <= at < hi for lo, hi in words if lo >= 0):
            continue
        if not ARCHIVE_LINE.sub("", body).strip() and key == "preamble":
            continue
        if decides_nothing(key, body, plan_text, done):  # T75: its items are make tick's to check
            continue
        entry = have.get(key) or {}
        if entry.get("sha256") != block_digest(body):
            earlier = entry.get("text") or (history.block(key, str(entry.get("sha256"))) if history and entry.get("sha256") else None)
            was, now_ = ARCHIVE_LINE.sub("", earlier or ""), ARCHIVE_LINE.sub("", lands_open_appended(earlier or "", body))
            own = _TASK_ID.match(_HEAD.sub(r"\2", key).strip())  # a ticked task's blocks are judged here: the repoint rule too
            if earlier is None or not (typo_only(was, now_) or (own and typo_only(repointed(was, now_, own.group(0), plan_text + done), now_))):
                owed.append(key)
                continue
        if entry.get("verdict") == "BLOCKED":
            blocked.append(key)
        elif entry.get("verdict") != "CLEAR":
            owed.append(key)
    now = {k for k, _b, _a in blocks(plan_text)}
    archived = {block_digest(b) for _k, b, _a in blocks(done)} if done else set()
    # AN ARCHIVED BLOCK IS JUDGED AS A LIVE ONE IS (feature 385 T65, plan D84): the archive moves a section byte for byte, so a
    # block edited by a typo after its review (T47 renumbered T49) reached plan-done.md at another digest, and the tick that
    # archived it was refused for two "(removed)" blocks. Its text there, typo-scale against the reviewed text, owes nothing.
    done_text = {k: b for k, b, _a in blocks(done)} if done else {}
    for key, entry in have.items():
        if key in now or key == "preamble" or not isinstance(entry, dict) or entry.get("sha256") in archived:
            continue
        if key in done_text:
            earlier = entry.get("text") or (history.block(key, str(entry.get("sha256"))) if history and entry.get("sha256") else None)
            if earlier is not None and typo_only(ARCHIVE_LINE.sub("", earlier), ARCHIVE_LINE.sub("", done_text[key])):
                continue
        owed.append(REMOVED + key)
    return owed, blocked
