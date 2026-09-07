"""Every hook refusal in every Claude Code transcript, with the command that was refused."""
import json, glob, os, re, sys, collections
root = os.path.expanduser('~/.claude/projects/-diagram')
files = glob.glob(root + '/*.jsonl') + glob.glob(root + '/*/subagents/*.jsonl') + glob.glob(root + '/**/agent-*.jsonl', recursive=True)
files = sorted(set(files))
out = []
HDR = re.compile(r'PreToolUse:(\w+) hook error: \[([^\]]+)\]:?\s*(.*)', re.S)
for f in files:
    uses = {}
    sub = '/subagents/' in f or '/agent-' in f
    try:
        with open(f, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                m = d.get('message') or {}
                c = m.get('content')
                if not isinstance(c, list):
                    continue
                for blk in c:
                    if not isinstance(blk, dict):
                        continue
                    if blk.get('type') == 'tool_use':
                        uses[blk.get('id')] = (blk.get('name'), blk.get('input'))
                    elif blk.get('type') == 'tool_result' and blk.get('is_error'):
                        txt = blk.get('content')
                        if isinstance(txt, list):
                            txt = ' '.join(x.get('text', '') for x in txt if isinstance(x, dict))
                        if not isinstance(txt, str) or 'hook error' not in txt:
                            continue
                        mm = HDR.search(txt)
                        if not mm:
                            continue
                        name, inp = uses.get(blk.get('tool_use_id'), (None, None))
                        out.append({'file': os.path.basename(f), 'sub': sub, 'ts': d.get('timestamp'),
                                    'tool': mm.group(1), 'hook': os.path.basename(mm.group(2).split()[0]),
                                    'mode': mm.group(2).split()[-1], 'msg': mm.group(3)[:600],
                                    'name': name, 'input': inp})
    except Exception as e:
        print('ERR', f, e, file=sys.stderr)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
cnt = collections.Counter((r['hook'], r['tool']) for r in out)
for k, v in sorted(cnt.items()):
    print(v, k)
print(len(out), 'refusals in', len(files), 'transcripts')
