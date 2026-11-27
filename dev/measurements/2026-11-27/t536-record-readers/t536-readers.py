"""451 T536: every non-test Rust reference to one of 451's large records (or the helper/const that names it). Read-only.
Usage: python3 -I t536-readers.py <tree> > t536-readers.txt
A path is matched by name or by the constants/helpers that stand for it (tasks::DONE, RECORD, log_path, edit_lines, ...)."""
import os, re, sys
tree = sys.argv[1]
PAT = {
  "plan-review.json": r'plan-review\.json|\bRECORD\b',
  "plan-done.md": r'plan-done\.md',
  "tasks-done.md": r'tasks-done\.md|tasks::DONE|\bjoined\(',
  "event log": r'l7r-events|log_path(_in)?\(|edit_lines\(|text_if_file\(|landings\(|LOG\)',
}
READ = re.compile(r'fs::read|read_to_string|read_text|text_if_file|\bshow\(|BufReader|File::open|read\(')
for root, _, files in os.walk(os.path.join(tree, "rust")):
    if "/target" in root: continue
    for f in files:
        if not f.endswith(".rs") or "test" in f or "/tests" in root: continue
        p = os.path.join(root, f)
        lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith("//") or s.startswith("#["): continue
            for rec, pat in PAT.items():
                if re.search(pat, l):
                    near = " ".join(lines[max(0,i-3):i+4])
                    form = "read-near" if READ.search(near) else "-"
                    print(f"{rec}\t{os.path.relpath(p, tree)}:{i+1}\t{form}\t{s[:150]}")
