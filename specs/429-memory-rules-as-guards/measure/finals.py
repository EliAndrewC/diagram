"""Extract each turn's final assistant text from recent main-session transcripts."""
import json, os, sys, glob
root = os.path.expanduser('~/.claude/projects')
files = sorted(glob.glob(root + '/-diagram*/*.jsonl'), key=os.path.getmtime)[-int(sys.argv[1]):]
out = []
for f in files:
    last = None
    try:
        for line in open(f, errors='ignore'):
            try: r = json.loads(line)
            except Exception: continue
            t = r.get('type')
            if t == 'assistant':
                c = (r.get('message') or {}).get('content') or []
                txt = ''.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
                if txt.strip(): last = txt
            elif t == 'user':
                c = (r.get('message') or {}).get('content')
                real = isinstance(c, str) or (isinstance(c, list) and any(isinstance(x, dict) and x.get('type') == 'text' for x in c))
                if real and last:
                    out.append({'file': os.path.basename(f), 'text': last}); last = None
    except Exception:
        pass
json.dump(out, open(sys.argv[2], 'w'))
print(len(files), 'files', len(out), 'finals')
