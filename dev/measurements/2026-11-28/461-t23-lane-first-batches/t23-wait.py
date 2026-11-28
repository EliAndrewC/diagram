"""461 T23 (D9): each background `make lane-wait` the coordinator started - when it started, when its turn ended
(the next assistant message with no tool call after it, or the next user prompt), and when its completion notice came.
Usage: python3 -I t23-wait.py TRANSCRIPT START"""
import json, re, sys
path, start = sys.argv[1], sys.argv[2]
starts = {}   # tool_use id -> t
bg = {}       # bg task id -> (tool_use id, t)
ends = {}
status = {}
turn_end = []  # times of assistant text-only messages (a turn's end)
with open(path, "rb") as f:
    for raw in f:
        try:
            d = json.loads(raw)
        except Exception:
            continue
        t = d.get("timestamp", "")
        if t < start or d.get("isSidechain"):
            continue
        m = d.get("message") or {}
        if d.get("type") == "assistant":
            content = m.get("content") or []
            if content and all(c.get("type") == "text" for c in content):
                turn_end.append(t)
            for c in content:
                if c.get("type") == "tool_use" and c.get("name") == "Bash":
                    inp = c.get("input") or {}
                    if "lane-wait" in (inp.get("command") or "") and inp.get("run_in_background"):
                        starts[c["id"]] = t
        s = json.dumps(m) if d.get("type") == "user" else ""
        if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
            s = d.get("content") or ""
            st = re.search(r"<status>(\w+)</status>", s)
            for mm in re.finditer(r"<task-id>(\w+)</task-id>", s):
                status[mm.group(1)] = st.group(1) if st else "?"
                ends.setdefault(mm.group(1), t)
        if d.get("type") == "user":
            for c in (m.get("content") or []) if isinstance(m.get("content"), list) else []:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in starts:
                    txt = json.dumps(c.get("content"))
                    mm = re.search(r"ID: (\w+)", txt)
                    if mm:
                        bg[mm.group(1)] = (c["tool_use_id"], starts[c["tool_use_id"]])
            for mm in re.finditer(r"<task-id>(\w+)</task-id>", s):
                if mm.group(1) in bg and mm.group(1) not in ends:
                    ends[mm.group(1)] = t
from datetime import datetime as D
ts = lambda s: D.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for b, (u, t0) in sorted(bg.items(), key=lambda kv: kv[1][1]):
    te = next((x for x in turn_end if x > t0), None)
    t1 = ends.get(b)
    life = (ts(t1) - ts(t0)).total_seconds() / 60 if t1 else None
    past = (ts(t1) - ts(te)).total_seconds() / 60 if (t1 and te and te < t1) else None
    rows.append((t0, te, t1, life, past))
    print(f"{b} start {t0[:19]} turn-end {te[:19] if te else '-'} notice {t1[:19] if t1 else 'still running'}"
          f" life {life and round(life,1)} min past-turn {past and round(past,1)} min status {status.get(b)}")
pl = [r[4] for r in rows if r[4] is not None]
print(f"n={len(rows)}, with a notice after their turn ended: {len(pl)}, longest past its turn {max(pl):.1f} min" if pl else "none")
