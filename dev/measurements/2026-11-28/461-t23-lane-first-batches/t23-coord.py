"""461 T23: the coordinator's (main session's) tool calls spent on landing, by window.

Reads the main session transcript's own assistant messages (isSidechain false), START to END, cut at CUTs.
Each tool call's Bash command is classified on its make targets and commands, with quoted strings and heredoc
bodies removed first (so a task-add TITLE or a commit message naming the lane does not count), first match wins:
  hand-land   make land / cohort-landing, or a gate's coverage run by hand (l7r-gate.sh rust cover)
  carry       make carry / builder-done, git cherry-pick, git add+commit in a carry
  lane-mend   make lane-stop / lane-start, the lane tree reset by hand (git -C ...-land ...)
  own-push    make land-tooling, sync-with-main.sh done (the session's own commits out, D13)
  wake        make lane-wait, make lane, reading a background task's output
  file-lane   make task-add whose TITLE names the lane, a carry, a batch or a landing (a lane defect filed)
  other       everything else
A model call (one message id) takes the first landing kind among its tool calls in the order above.
Usage: python3 -I t23-coord.py TRANSCRIPT START END [CUT ...]
"""
import json, re, sys
from collections import defaultdict

path, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
cuts = sys.argv[4:]
HEREDOC = re.compile(r"<<-?\s*'?(\w+)'?.*?\n\1\b", re.S)
QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'')
MK = r"\bmake\s+(?:-\S+\s+)*(?:-C\s+\S+\s+)?(?:[A-Za-z_]+=\S*\s+)*"
KINDS = [
    ("hand-land", re.compile(MK + r"(land|cohort-landing)(?![\w-])|l7r-gate\.sh\s+rust\s+cover")),
    ("carry", re.compile(MK + r"(carry|builder-done)(?![\w-])|git\s+(-C\s+\S+\s+)?cherry-pick|\bgit\s+add\b[^\n]*&&\s*git\s+(-c\s+\S+\s+)?cherry-pick")),
    ("lane-mend", re.compile(MK + r"(lane-stop|lane-start)(?![\w-])|git\s+-C\s+\S*-land\b|git\s+-C\s+\$L\b")),
    ("own-push", re.compile(MK + r"land-tooling(?![\w-])|sync-with-main\.sh\s+done")),
    ("wake", re.compile(MK + r"(lane-wait|lane)(?![\w-])|/tasks/\w+\.output|l7r-lane/")),
]
FILE_LANE = re.compile(r"make\s+task-add\b[^\n]*TITLE=\"[^\"]*\b(lane|carry|batch|landing|hand-in)\b", re.I)
ORDER = [k for k, _ in KINDS] + ["file-lane"]


def classify(cmd):
    if FILE_LANE.search(cmd):
        return "file-lane"
    bare = QUOTED.sub("''", HEREDOC.sub("", cmd))
    for name, rx in KINDS:
        if rx.search(bare):
            return name
    return "other"


def window(t):
    return sum(1 for c in cuts if t >= c)


calls = defaultdict(lambda: defaultdict(int))
per = {}
with open(path, "rb") as f:
    for raw in f:
        if b'"role":"assistant"' not in raw[:600]:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        t = d.get("timestamp", "")
        if not (start <= t < end):
            continue
        m = d.get("message", {})
        w = window(t)
        kinds = []
        for c in m.get("content", []) or []:
            if c.get("type") != "tool_use":
                continue
            inp = c.get("input", {}) or {}
            cmd = inp.get("command") or ""
            if not cmd and "-land/" in str(inp.get("file_path", "")):
                k = "carry"
            else:
                k = classify(cmd) if cmd else "other"
            calls[w][k] += 1
            kinds.append(k)
        rec = per.setdefault(m.get("id") or id(d), {"w": w, "kinds": set(), "u": {}})
        rec["kinds"].update(kinds)
        if m.get("usage"):
            rec["u"] = m["usage"]

msgs = defaultdict(lambda: defaultdict(int))
out_tok = defaultdict(lambda: defaultdict(int))
cache_rd = defaultdict(lambda: defaultdict(int))
for rec in per.values():
    w, kinds, u = rec["w"], rec["kinds"], rec["u"]
    k = next((n for n in ORDER if n in kinds), "tool" if kinds else "text")
    land = k in ORDER
    msgs[w][k] += 1
    msgs[w]["ALL"] += 1
    out_tok[w]["landing" if land else "not"] += u.get("output_tokens", 0)
    cache_rd[w]["landing" if land else "not"] += u.get("cache_read_input_tokens", 0)

bounds = [start] + cuts + [end]
for w in range(len(bounds) - 1):
    lo, hi = bounds[w], bounds[w + 1]
    c = calls[w]
    landing = sum(c[k] for k in ORDER)
    print(f"window {w}: {lo} .. {hi}")
    print(f"  tool calls: {sum(c.values())}, landing-side {landing}: " + ", ".join(f"{k} {c[k]}" for k in ORDER) + f", other {c['other']}")
    mm = msgs[w]
    print(f"  model calls: {mm['ALL']}, landing-side {sum(mm[k] for k in ORDER)}: " + ", ".join(f"{k} {mm[k]}" for k in ORDER))
    print(f"  output tokens landing-side {out_tok[w]['landing']}, other {out_tok[w]['not']}; "
          f"cache-read landing-side {cache_rd[w]['landing']}, other {cache_rd[w]['not']}")
