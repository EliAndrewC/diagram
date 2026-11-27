#!/usr/bin/env python3
"""451 T499: bytes of plan.md / plan-done.md returned to each builder's context (read-only).

Builders = subagent transcripts under /home/agent/.claude/projects/-diagram*/ whose first user prompt
carries a BUILDER-BRIEF line, first timestamp on 2026-11-26 or 27. A call counts when it is a Read of a
file named plan.md / plan-done.md (its returned text) or a Bash whose command names them (its output).
Run: python3 -I plan-reads.py [out.json]   Bytes are UTF-8 bytes of the tool result text.
"""
import glob, json, os, re, statistics, sys, collections
PLAN = re.compile(r'plan(-done)?\.md')
def text_of(c):
    if isinstance(c, str): return c
    return ''.join(b.get('text', '') for b in c if isinstance(b, dict) and b.get('type') == 'text')
def shape_bash(cmd):
    c = cmd
    if re.search(r'\b(rg|grep|egrep)\b', c): return 'grep'
    if re.search(r'\bsed\b', c): return 'sed range'
    if re.search(r'\bawk\b', c): return 'awk'
    if re.search(r'\b(cat|head|tail)\b', c): return 'cat/head/tail'
    return 'other bash'
def shape_read(inp):
    return 'Read with offset/limit' if (inp.get('offset') or inp.get('limit')) else 'Read whole file'
def main():
    out = sys.argv[1] if len(sys.argv) > 1 else None
    builders = []; seen = set()
    for p in glob.glob('/home/agent/.claude/projects/-diagram*/**/*.jsonl', recursive=True):
        if '/subagents/' not in p or os.path.basename(p) in seen: continue
        seen.add(os.path.basename(p))
        first = None; ts0 = None; uses = {}; calls = []; total = 0; n = 0
        for line in open(p, errors='replace'):
            try: d = json.loads(line)
            except Exception: continue
            ts0 = ts0 or d.get('timestamp')
            m = d.get('message')
            if not isinstance(m, dict): continue
            c = m.get('content')
            if first is None and d.get('type') == 'user':
                first = text_of(c) if not isinstance(c, list) else text_of(c)
                if not re.search(r'^BUILDER-BRIEF \d+ T\d+', first, re.M): break
            if not isinstance(c, list): continue
            for b in c:
                if b.get('type') == 'tool_use':
                    uses[b['id']] = (b['name'], b.get('input', {}))
                elif b.get('type') == 'tool_result':
                    sz = len(text_of(b.get('content', '')).encode()); total += sz; n += 1
                    nm, inp = uses.get(b.get('tool_use_id'), (None, {}))
                    if nm == 'Read' and PLAN.search(inp.get('file_path', '')):
                        calls.append((shape_read(inp), sz, inp['file_path']))
                    elif nm == 'Bash' and PLAN.search(inp.get('command', '')):
                        calls.append((shape_bash(inp['command']), sz, inp['command'][:160]))
        if not first or not re.search(r'^BUILDER-BRIEF \d+ T\d+', first, re.M) or not ts0 or ts0[:10] not in ('2026-11-26', '2026-11-27'): continue
        mm = re.search(r'^BUILDER-BRIEF (\S+) (\S+)', first, re.M)
        if mm and mm.group(2) == 'T499' and 'plan-reads' in first: continue  # this measurement itself
        builders.append(dict(file=os.path.basename(p), task=' '.join(mm.groups()) if mm else '?', ts=ts0,
                             total=total, results=n, plan=sum(c[1] for c in calls), calls=calls))
    builders.sort(key=lambda b: b['ts'])
    if out: json.dump(builders, open(out, 'w'))
    print(f"builders: {len(builders)}")
    print("| task | start | plan bytes | tool-result bytes | share | calls |\n|---|---|---|---|---|---|")
    for b in builders:
        print(f"| {b['task']} | {b['ts'][5:16]} | {b['plan']:,} | {b['total']:,} | {100*b['plan']/max(b['total'],1):.1f}% | {len(b['calls'])} |")
    pl = sorted(b['plan'] for b in builders); sh = sorted(100*b['plan']/max(b['total'],1) for b in builders)
    def q(a, f): return a[min(len(a)-1, int(f*len(a)))]
    S = sum(pl); T = sum(b['total'] for b in builders)
    print(f"\nplan bytes per builder: median {statistics.median(pl):,.0f}, p90 {q(pl,.9):,}, max {pl[-1]:,}")
    print(f"share per builder: median {statistics.median(sh):.1f}%, p90 {q(sh,.9):.1f}%, max {sh[-1]:.1f}%")
    print(f"sum plan bytes {S:,} of {T:,} tool-result bytes ({100*S/T:.1f}%); builders reading any plan: {sum(1 for x in pl if x)}")
    print(f"estimate only (about 4 bytes a token): {S//4:,} tokens total, {S//4//max(len(pl),1):,} a builder mean")
    sh_ = collections.defaultdict(lambda: [0, 0])
    for b in builders:
        for s, z, _ in b['calls']: sh_[s][0] += 1; sh_[s][1] += z
    print("\n| shape | calls | bytes | share of plan bytes |\n|---|---|---|---|")
    for s, (n, z) in sorted(sh_.items(), key=lambda x: -x[1][1]): print(f"| {s} | {n} | {z:,} | {100*z/max(S,1):.1f}% |")
    allc = sorted((c for b in builders for c in b['calls']), key=lambda c: -c[1])[:8]
    print("\nlargest single calls:")
    for s, z, d in allc: print(f"- {z:,} {s}: {d}")
main()
