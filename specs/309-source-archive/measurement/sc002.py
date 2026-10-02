"""SC-002: 20 archived copies drawn at random - 5+ Wikipedia, 5+ PDFs, 5+ other sites - opened from a FRESH clone of the
archive repository (a partial clone, only the sampled directories checked out), each checked to open (an MHTML parses with
an HTML part; a PDF has text) and to hold its registry entry's quoted passage where the entry quotes one in the original
(a 「...」 run of 8+ characters found in the capture's text, whitespace ignored).

Run from the skill directory: python3 ../../../specs/309-source-archive/measurement/sc002.py <scratch dir> [seed]
"""

from __future__ import annotations

import email
import glob
import json
import os
import pathlib
import random
import re
import subprocess
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "../../../scripts")
import _archive as ar  # noqa: E402

from l7r.diagram.interactive.record import archive as rec  # noqa: E402
from l7r.diagram.interactive.sources import RESEARCH_DIR  # noqa: E402

scratch = pathlib.Path(sys.argv[1])
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 309)
rows = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob("research/archive/[0-9a-f]*.json"))]
rows = [r for r in rows if r["outcome"] in ("archived", "archived-earlier-snapshot") and r.get("keys") and r.get("path")]
wiki = [r for r in rows if "wikipedia.org" in r["url"]]
pdf = [r for r in rows if r["url"].lower().split("?")[0].endswith(".pdf") or "/_pdf" in r["url"]]
other = [r for r in rows if r not in wiki and r not in pdf]
sample = rng.sample(wiki, 6) + rng.sample(pdf, min(6, len(pdf))) + rng.sample(other, 8)
sample = sample[:20]

clone = scratch / "fresh"
env = ar.git_env(ar.token(pathlib.Path("../../..").resolve()))
if not clone.exists():
    subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", ar.REMOTE, str(clone)], env=env, check=True)
subprocess.run(["git", "-C", str(clone), "sparse-checkout", "set", "--no-cone", *[r["path"] + "/" for r in sample]], env=env, check=True)
subprocess.run(["git", "-C", str(clone), "checkout", "-q", "main"], env=env, check=True)

registry = {m.group(1): m.group(2) for m in rec._ENTRY.finditer(rec.store.registry_html(RESEARCH_DIR))}
squash = lambda s: re.sub(r"\s+", "", s)  # noqa: E731
opened = quoted = had_quote = 0
for r in sample:
    d = clone / r["path"]
    names = sorted(os.listdir(d)) if d.is_dir() else []
    ok = False
    if "page.mhtml" in names:
        msg = email.message_from_bytes((d / "page.mhtml").read_bytes())
        ok = any(p.get_content_type() == "text/html" for p in msg.walk())
    elif any(n.startswith("served.pdf") for n in names):
        ok = (d / "text.txt").is_file() and (d / "text.txt").stat().st_size > 0
    else:
        ok = (d / "text.txt").is_file()
    text = squash((d / "text.txt").read_text(encoding="utf-8", errors="replace")) if (d / "text.txt").is_file() else ""
    quotes = [squash(q) for q in re.findall(r"「([^」]{8,})」", registry.get(r["keys"][0], ""))]
    hit = next((q for q in quotes if q[:20] in text), None) if quotes else None
    opened += ok
    had_quote += bool(quotes)
    quoted += bool(hit)
    print(f"{'OPENS' if ok else 'BROKEN':6} {'QUOTE-FOUND' if hit else ('quote-not-found' if quotes else 'no-quote'):15} {r['keys'][0]:34} {r['url']}")
print(f"\nSC-002: {opened}/{len(sample)} open; of the {had_quote} whose entry quotes an original, {quoted} hold a quoted passage")
