#!/usr/bin/env python3
"""451 T336: the harness's records by arm - tries, tries with a build cut, with a finished session's files written, link failures."""
import json, sys, collections

rows = collections.OrderedDict()
detail = []
for path in sys.argv[1:]:
    for line in open(path):
        d = json.loads(line)
        r = rows.setdefault(d["arm"], collections.Counter())
        cuts = [b for b in d["builds"][:-1] if b.get("cut")]
        wrote = [b for b in cuts if b.get("session_files_changed")]
        guard = [b for b in cuts if any(a.startswith("rustc:l7r_guard") for a in b.get("alive_at_cut", []))]
        fail = d["final_link_fail"] > 0
        r["tries"] += 1
        r["cut"] += bool(cuts)
        r["cut, guard rustc alive"] += bool(guard)
        r["cut, session written"] += bool(wrote)
        r["link failed"] += fail
        r["failed | session written"] += fail and bool(wrote)
        r["failed | cut, none written"] += fail and bool(cuts) and not wrote
        r["failed | not cut"] += fail and not cuts
        r["failed, group empty at next build"] += fail and all(not b.get("survivors") for b in cuts)
        r["other red"] += d["final_code"] != 0 and not fail
        if "healed_code" in d:
            r["healed"] += d["healed_code"] == 0
            r.setdefault("heal_secs", [])
        for b in cuts:
            detail.append((d["arm"], b["cut_at"], bool(b.get("session_files_changed")), fail,
                           json.dumps(b.get("session_files_changed")), ",".join(b.get("alive_at_cut", []))))
cols = ["tries", "cut", "cut, guard rustc alive", "cut, session written", "link failed", "failed | session written",
        "failed | cut, none written", "failed | not cut", "failed, group empty at next build", "other red", "healed"]
print("| arm | " + " | ".join(cols) + " |")
print("|---|" + "---|" * len(cols))
for arm, r in rows.items():
    print(f"| {arm} | " + " | ".join(str(r[c]) for c in cols) + " |")
print()
w = sorted(d[1] for d in detail if d[2])
n = sorted(d[1] for d in detail if not d[2])
print("cuts that wrote a finished session: n", len(w), "earliest s", w[:1], "latest", w[-1:])
print("cuts that wrote none: n", len(n), "earliest s", n[:1], "latest", n[-1:])
kinds = collections.Counter(d[4] for d in detail if d[2])
print("what was written (extension:inode -> files), by count of cuts:", kinds.most_common(6))
