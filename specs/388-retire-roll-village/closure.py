"""Names defined in l7r/ whose only production references were in removed files: a fixpoint by name.
usage: closure.py ROOT removed1.py [removed2.py ...]"""
import ast, os, re, sys
from collections import Counter
root = sys.argv[1]; removed = {os.path.join(root, p) for p in sys.argv[2:]}
files = []
for top in ("l7r", "pool"):
    for d, _, fs in os.walk(os.path.join(root, top)):
        files += [os.path.join(d, f) for f in fs if f.endswith(".py")]
text = {f: open(f).read() for f in files}
defs = {}  # name -> list of (file, node)
for f, t in text.items():
    for n in ast.walk(ast.parse(t)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.setdefault(n.name, []).append((f, n))
        elif isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper() and n.col_offset == 0:
            defs.setdefault(n.targets[0].id, []).append((f, n))
def spans(f):  # source spans of defs removed so far in file f
    return dead_spans.get(f, [])
def refs(live):
    c = Counter()
    for f, t in text.items():
        if f in live_removed: continue
        lines = t.split("\n")
        cut = set()
        for (a, b) in dead_spans.get(f, []): cut |= set(range(a, b + 1))
        body = "\n".join(l for i, l in enumerate(lines, 1) if i not in cut)
        import io, tokenize
        try:
            toks = tokenize.generate_tokens(io.StringIO(body).readline)
            c.update(tok.string for tok in toks if tok.type == tokenize.NAME)
        except (tokenize.TokenError, IndentationError, SyntaxError):
            c.update(re.findall(r"\b[A-Za-z_]\w*\b", body))
    return c
live_removed = set(); dead_spans = {}
dead = []
base = refs(None); live_removed = set(removed)
while True:
    c = refs(None)
    new = []
    for name, ds in defs.items():
        if name in dead or name.startswith("__") or name.startswith("test_"): continue
        ndef = len([1 for f, _ in ds if f not in live_removed])
        if ndef == 0: continue
        if c[name] <= ndef and base[name] > ndef:  # referenced before, only by its own def(s) now
            new.append(name)
    if not new: break
    for name in new:
        dead.append(name)
        for f, n in defs[name]:
            if f in live_removed: continue
            dead_spans.setdefault(f, []).append((n.lineno - len(getattr(n, "decorator_list", [])), n.end_lineno))
for name in dead:
    print(name, *sorted({os.path.relpath(f, root) + ":" + str(n.lineno) for f, n in defs[name] if f not in live_removed}))
