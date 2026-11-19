"""Per-sheet factors for the derivation's tables, from count.py's per-step tallies."""
import json, subprocess, sys
SEARCH = ('seat', 'span_query', 'index_query', 'index_cell', 'index_entry', 'exact_test', 'span_interval', 'span_compare')
for s in ('county-magistracy-example', 'ochiba-roundtrip-test'):
    out = subprocess.run(['python3', '-I', '/tmp/t208/count.py', f'pool/magistracies/{s}/{s}.svg', s, sys.argv[1], sys.argv[2]],
                         capture_output=True, text=True, cwd='/diagram/.clones/diagram-backlog').stdout
    d = json.loads(out.splitlines()[0]); by = d['by']; z = d['sizes']
    print('==', s, 'total', d['total'], json.dumps(z))
    for k, v in by.items():
        srch = sum(v.get(x, 0) for x in SEARCH); fixed = sum(v.values()) - srch
        print(f'  {k:5s} search {srch:4d} fixed {fixed:4d}', v)
    tot_s = sum(sum(v.get(x, 0) for x in SEARCH) for v in by.values())
    print('  search total', tot_s, 'fixed total', d['total'] - tot_s, 'at slack 1.5:', round(d['total'] + 0.5 * tot_s))
