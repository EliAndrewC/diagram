# t388: the Agent PreToolUse and PostToolUse calls of one local day, by subagent type, from a COPY of the feature event logs.
#   python3 t388-mix.py <log> [<log> ...]   (the day: 2026-11-26T05:00Z to 2026-11-27T05:00Z)
import json, sys, collections
lo, hi = '2026-11-26T05:00', '2026-11-27T05:00'
pre, post, sid_pre = collections.Counter(), collections.Counter(), collections.Counter()
for path in sys.argv[1:]:
    for line in open(path, errors='replace'):
        if '"tool":"Agent"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if not (lo <= d.get('t', '') < hi) or d.get('tool') != 'Agent':
            continue
        if str(d.get('sid', '')).startswith(('t373', 't365', 't388')):
            continue
        a = d.get('agent') or '(none)'
        if d.get('ev') == 'PreToolUse':
            pre[a] += 1; sid_pre['builder' if d.get('by') else 'session'] += 1
        elif d.get('ev') == 'PostToolUse':
            post[a] += 1
print('PreToolUse', sum(pre.values()), 'PostToolUse', sum(post.values()), dict(sid_pre))
for a, n in pre.most_common():
    print(f'{a}\t{n}\t{post[a]}')
