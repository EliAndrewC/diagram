import ast, json, sys, pathlib, re
root = pathlib.Path('.').resolve()
KEPT = ("l7r/diagram/tools/", "l7r/diagram/ci/", "l7r/diagram/pipeline/", "l7r/diagram/interactive/", "l7r/diagram/labels/", "l7r/diagram/overlap/")
rec = json.load(open('dev/coverage-exempt.json'))
S = {e['path'] for e in rec['entries']}
mods = {}
for p in (root/'l7r').rglob('*.py'):
    rel = p.relative_to(root).as_posix()
    name = rel[:-3].replace('/', '.').removesuffix('.__init__')
    mods[name] = rel
def resolve(cur, node):
    if isinstance(node, ast.ImportFrom):
        base = node.module or ''
        if node.level:
            parts = cur.split('.')
            pkg = parts if mods.get(cur,'').endswith('__init__.py') else parts[:-1]
            pkg = pkg[:len(pkg)-(node.level-1)]
            base = '.'.join(pkg + ([base] if base else []))
        out = []
        for a in node.names:
            if f"{base}.{a.name}" in mods: out.append(f"{base}.{a.name}")
            elif base in mods:
                d = definer(base, a.name)
                out.append(d or base)
        return out
    return [a.name for a in node.names if a.name in mods]
defs = {}
for name, rel in mods.items():
    try: t = ast.parse((root/rel).read_text())
    except SyntaxError: continue
    names=set()
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): names.add(n.name)
        elif isinstance(n,ast.Assign):
            names |= {x.id for x in n.targets if isinstance(x,ast.Name)}
        elif isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name): names.add(n.target.id)
    defs[name]=names
def definer(pkg, nm):
    if not mods[pkg].endswith('__init__.py'): return None
    if nm in defs.get(pkg,()): return None
    for m in mods:
        if m.startswith(pkg+'.') and nm in defs.get(m,()):
            sub = definer(m, nm) if mods[m].endswith('__init__.py') else None
            return sub or m
    return None
importers = {r: set() for r in mods.values()}
def scan(src_rel, text, cur):
    try: tree = ast.parse(text)
    except SyntaxError: return
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for m in resolve(cur, n):
                importers[mods[m]].add(src_rel)
for name, rel in mods.items():
    scan(rel, (root/rel).read_text(), name)
# outside importers: pool gens, scripts (not tests)
for p in list((root/'pool').rglob('*.py')) + list((root/'scripts').rglob('*.py')):
    rel = p.relative_to(root).as_posix(); scan(rel, p.read_text(errors='ignore'), '')
entry = {r for r in mods.values() if re.search(r'^if __name__ == .__main__.:', (root/r).read_text(), re.M)}
changed = True
added = []
while changed:
    changed = False
    for r, imps in importers.items():
        if r in S or r.startswith(KEPT) or r in entry or not imps: continue
        if r.endswith('__init__.py'): continue
        if imps <= S:
            S.add(r); added.append(r); changed = True
for a in sorted(added): print(a, sorted(importers[a])[:3])
print(len(added), 'added; total', len(S))
print('---')
for r in sorted(importers):
    if r.startswith('l7r/diagram/hamletgen/') and r not in S:
        print(r, sorted(i for i in importers[r] if i not in S)[:4])
print('=== reachability')
S0 = {e['path'] for e in rec['entries']}
imports = {}
for r, imps in importers.items():
    for i in imps: imports.setdefault(i, set()).add(r)
roots = {r for r in importers if r.startswith(KEPT) or r in entry} | {i for i in imports if not i.startswith('l7r/')}
# package __init__ chain: importing a.b.c runs a/__init__ and a/b/__init__
def parents(r):
    parts = r.split('/')[:-1]
    return [ '/'.join(parts[:k])+'/__init__.py' for k in range(2, len(parts)+1)]
seen=set(); stack=[r for r in roots if r not in S0]
while stack:
    r=stack.pop()
    if r in seen or r in S0: continue
    seen.add(r)
    for n in list(imports.get(r,())) + [p for p in parents(r) if p in importers]:
        if n not in seen and n not in S0: stack.append(n)
dead = sorted(r for r in importers if r not in seen and r not in S0)
for d in dead: print(d)
print(len(dead))
