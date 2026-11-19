import json, subprocess
SEARCH = ('seat', 'span_query', 'index_query', 'index_cell', 'index_entry', 'exact_test', 'span_interval', 'span_compare')
PLACE = ('mass', 'ell', 'door', 'part', 'roji')
SL = 1.5
res = {}
for s in ('county-magistracy-example', 'ochiba-roundtrip-test'):
    out = subprocess.run(['python3', '-I', '/tmp/t208/count.py', f'pool/magistracies/{s}/{s}.svg', s, '40', 'base'],
                         capture_output=True, text=True, cwd='/diagram/.clones/diagram-backlog').stdout
    d = json.loads(out.splitlines()[0]); res[s] = d
for s, d in res.items():
    by = d['by']; z = d['sizes']
    B = z['masses'] - z['joins']; D = z['doors']; P = sum(z[k] for k in ('bath', 'wells', 'tubs', 'privies', 'board', 'tree', 'rack', 'posts'))
    items = z['masses'] + D + P + (1 if z['stones'] else 0)
    m = by['mass']; dr = by['door']; p = by['part']; e = by['ell']; zo = by['zone']; o = by['once']; r = by.get('roji', {})
    srch = {k: sum(by[k].get(x, 0) for x in SEARCH) for k in PLACE if k in by}
    fixd = {k: sum(by[k].values()) - srch[k] for k in PLACE if k in by}
    zone_t = sum(zo.values()); once_t = sum(o.values())
    S = sum(srch.values()); F = sum(fixd.values())
    tot = zone_t + once_t + F + SL * S
    print(f'== {s}: items {items} (B {B} + ell {z["joins"]} + D {D} + P {P} + roji {1 if z["stones"] else 0}); zones {z["zones"]} gates {z["gates"]}')
    print(f'  per building: chunks {m["span_query"]/B:.2f} cells {m["index_cell"]/B:.2f} entries {m["index_entry"]/B:.2f} intervals {m["span_interval"]/B:.2f} compares {m["span_compare"]/B:.2f} checks {m["rule_check"]/B:.2f} inserts {m["index_insert"]/B:.2f}')
    print(f'  per door: cells {dr["index_cell"]/D:.2f} entries {dr["index_entry"]/D:.2f} inserts {dr["index_insert"]/D:.2f}')
    q = p['index_query']
    print(f'  parts: {P} parts, {q} face queries ({q/P:.3f}/part); per query cells {p["index_cell"]/q:.2f} entries {p["index_entry"]/q:.2f} intervals {p["span_interval"]/q:.2f} compares {p["span_compare"]/q:.2f}; exact {p["exact_test"]}; checks {p["rule_check"]}; inserts {p["index_insert"]}')
    print(f'  ell {e}; roji {r}; zone {zo}; once {o}')
    print(f'  search by step {srch} = {S}; fixed by step {fixd} = {F}; zone {zone_t}; once {once_t}')
    print(f'  cells written at the build (zones+gates): {zo["index_insert"] + o["index_insert"]}; density: mean entries per occupied cell at the end?')
    expr = f'{zone_t} + {once_t} + {F} + {SL} x {S}'
    print(f'  TOTAL {expr} = {round(tot)}  ({tot}); per item {tot/items:.1f}; at slack 1 {zone_t+once_t+F+S}')
    d['_tot'] = round(tot); d['_items'] = items
    # budget by kind
    kinds = {}
    for step, v in by.items():
        for k, n in v.items():
            mult = SL if (step in PLACE and k in SEARCH) else 1
            kinds[k] = kinds.get(k, 0) + n * mult
    d['_kinds'] = kinds
allk = sorted(set(k for d in res.values() for k in d['_kinds']))
print('kind | ' + ' | '.join(res))
for k in allk:
    vals = [res[s]['_kinds'].get(k, 0) for s in res]
    print(k, [f'{v:g}' for v in vals], f'{sum(vals):g}')
print('sum', [res[s]['_tot'] for s in res], sum(res[s]['_tot'] for s in res), 'items', sum(res[s]['_items'] for s in res))
