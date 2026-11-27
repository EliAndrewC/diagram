# 451 T458: the spelling survey over T443's read-only copies of the 34 real logs.
import glob, json, re, sys, collections
d = sys.argv[1]
tot = collections.Counter(); ev_sp = collections.Counter()
for f in sorted(glob.glob(d + '/*.jsonl')):
    for raw in open(f, 'rb'):
        tot['lines'] += 1
        if b'"Edit"' not in raw: continue
        tot['edit_screen'] += 1
        pre = b'"PreToolUse"' in raw
        tot['both_screens'] += pre
        try: l = raw.decode('utf-8')
        except UnicodeDecodeError: tot['non_utf8'] += 1; continue
        try: e = json.loads(l.strip())
        except Exception: tot['unparsable'] += 1; continue
        if not isinstance(e, dict): continue
        keep = e.get('ev') == 'PreToolUse' and e.get('tool') == 'Edit' and 'path' in e
        tot['kept'] += keep
        if keep and not pre: tot['KEPT_BUT_SCREENED_OUT'] += 1
        if e.get('ev') == 'PreToolUse':
            m = re.search(rb'"ev"\s*:\s*"PreToolUse"', raw)
            ev_sp[m.group(0).decode() if m else 'NO-LITERAL'] += 1
        if b'\\u00' in raw and b'PreToolUse' not in raw and e.get('ev') == 'PreToolUse': tot['escaped_ev'] += 1
print(dict(tot)); print(dict(ev_sp))
