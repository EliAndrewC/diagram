import sys, json
sys.path.insert(0, '/tmp/t198')
import inventory as inv, sim3 as sim2
from inventory import GROUND
c = 48.0
# pooled branch shares and per-query ratios, from sim2 over all six sheets (my own script on the SVG input)
f_t, p_in, m1, x_off, q_n, p_s, Cb, p_L = 227/286, 135/286, 801/151, 81/801, 142/286, 65/286, 88/65, 28/286
kappa = (27850/7140) / (5163/1673.4)        # entries per cell read near captions / mean entries per cell of the sheet
ex_q, nd_q, iv_e, cmp_iv = 2702/945, 517/142, 5477/13451, 12382/5477
rows = []
for p in sys.argv[1:]:
    vb, shapes, caps = inv.inventory(p); caps = [x for x in caps if x['fbox']]
    N = len(caps); A = vb[2]*vb[3]
    w = sum(x['wN'] for x in caps)/N; h = sum(x['hN'] for x in caps)/N; g = sum(x['fs'] for x in caps)/N/2
    parts = sum(x['parts'] for x in caps)/N
    blk = [s for s in shapes if s['kind'] not in GROUND]
    segs = sum(s['segs'] for s in blk); ids = sum(1 for s in shapes if s['ids'])
    I0 = sum((int(s['box'][2]//c)-int(s['box'][0]//c)+1)*(int(s['box'][3]//c)-int(s['box'][1]//c)+1) for s in blk)
    rho = I0/(A/c/c)
    st = sim2.run(p, c, first_to=None, chunk_px=c)
    # the sheet's own branch shares and ratios (my script on its input)
    f_t, p_in = st['tried_inside']/N, st['inside']/N
    m1 = st['r1_seats']/max(st['reach_r1'],1)
    x_off = 1 - (st['queries']-st['q_sweep']-st['q_near']-st['tried_inside'] + (st['tried_inside']-sum(1 for _ in [])))/max(st['r1_seats'],1)
    seatq = st['queries']-st['q_sweep']-st['q_near']
    x_off = 1 - (seatq - st['tried_inside'])/max(st['r1_seats'],1)
    q_n = st['q_near']/N; p_s = (st['within2g']+st['leader'])/N; Cb = st['chunks']/max(st['within2g']+st['leader'],1); p_L = st['leader']/N
    kappa = (st['entries']/st['cells'])/(I0/(A/c/c))
    ex_q = st['exact_segs']/max(seatq,1); nd_q = st['near_dist']/max(st['q_near'],1)
    iv_e = st['sweep_intervals']/max(st['sweep_entries'],1); cmp_iv = st['sweep_cmp']/max(st['sweep_intervals'],1)
    rl = kappa*rho
    Ks = (1+w/c)*(1+h/c); Kn = (1+(w+2*g)/c)*(1+(h+2*g)/c)
    Kh = (1+(w+c)/c)*(1+h/c); Kv = (1+w/c)*(1+(h+c)/c); Kc = (1+(w+c)/c)*(1+(h+c)/c)
    Kw = (2*Kh+2*Kv+4*Kc)/8
    seats = f_t + (1-p_in)*m1 + p_s*Cb*8
    qs = f_t + (1-p_in)*m1*(1-x_off); qw = p_s*Cb*8
    queries = qs + q_n + qw
    cells = qs*Ks + q_n*Kn + qw*Kw
    entries = cells*rl
    exact = qs*ex_q
    near = q_n*nd_q
    ivs = qw*Kw*rl*iv_e
    cmps = ivs*cmp_iv
    leader = p_L*parts*1.0
    inserts = Ks
    lookups = parts
    writes = 6
    P = seats+queries+cells+entries+exact+near+ivs+cmps+leader+inserts+lookups+writes
    once = segs + ids + I0
    simtot = sum(st[x] for x in sim2.KEYS) + st['setup_inserts'] - st['cuts'] + segs + ids + N*(6) + sum(x['parts'] for x in caps)
    rows.append(dict(sheet=p.split('/')[-1][:-4], f_t=round(f_t,3), p_in=round(p_in,3), m1=round(m1,2), x_off=round(x_off,3), q_n=round(q_n,3), p_s=round(p_s,3), Cb=round(Cb,2), p_L=round(p_L,3), kappa=round(kappa,2), ex_q=round(ex_q,2), nd_q=round(nd_q,2), iv_e=round(iv_e,3), cmp_iv=round(cmp_iv,2), N=N, A=A, w=round(w,1), h=round(h,1), g=round(g,2), rho=round(rho,2), rl=round(rl,2),
        Ks=round(Ks,2), Kn=round(Kn,2), Kw=round(Kw,2), parts=round(parts,2), segs=segs, ids=ids, I0=I0,
        seats=round(seats,2), queries=round(queries,2), cells=round(cells,2), entries=round(entries,1), exact=round(exact,2),
        near=round(near,2), ivs=round(ivs,2), cmps=round(cmps,2), leader=round(leader,2), inserts=round(inserts,2),
        P=round(P,1), once=once, total1=round(once+N*P), budget=round(once+N*P*1.5), sim=simtot))
for r in rows: print(json.dumps(r))
print('kappa', round(kappa,3), 'sum total1', sum(r['total1'] for r in rows), 'sum budget', sum(r['budget'] for r in rows), 'sum sim', sum(r['sim'] for r in rows))

import math
# the budget by counted kind, per sheet: search kinds x slack 1.5, exact kinds at 1
S = 1.5
kinds = [('seat', lambda r: r['N']*r['seats']*S), ('index_query', lambda r: r['N']*r['queries']*S),
         ('index_cell', lambda r: r['N']*r['cells']*S), ('index_entry', lambda r: r['N']*r['entries']*S),
         ('exact_test', lambda r: r['N']*r['exact']*S), ('shape_distance', lambda r: r['N']*(r['near']+r['leader'])*S),
         ('sweep_interval', lambda r: r['N']*r['ivs']*S), ('sweep_compare', lambda r: r['N']*r['cmps']*S),
         ('leader_crossing', lambda r: 0), ('wrap_cut', lambda r: 0),
         ('index_insert', lambda r: r['I0'] + r['N']*r['inserts']), ('shape_box', lambda r: r['segs']),
         ('name_lookup', lambda r: r['ids'] + r['N']*r['parts']), ('write', lambda r: r['N']*6)]
print('| kind | ' + ' | '.join(r['sheet'] for r in rows) + ' | all six |')
tot = [0]*len(rows)
for k, f in kinds:
    vals = [round(f(r)) for r in rows]
    tot = [a+b for a, b in zip(tot, vals)]
    print(f'| {k} | ' + ' | '.join(str(v) for v in vals) + f' | {sum(vals)} |')
print('| total | ' + ' | '.join(str(v) for v in tot) + f' | {sum(tot)} |')
xs = [math.log(r['N']) for r in rows]; ys = [math.log(t) for t in tot]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
print('loglog slope', sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs))

print()
for r in rows:
    search = round(r['seats']+r['queries']+r['cells']+r['entries']+r['exact']+r['near']+r['leader']+r['ivs']+r['cmps'], 1)
    fixed = round(r['inserts']+r['parts']+6, 2)
    once = r['once']
    val = once + r['N']*(search*1.5+fixed)
    print(f"- at {r['sheet']}: {r['segs']} + {r['ids']} + {r['I0']} + {r['N']} x ({search} x 1.5 + {fixed}) = {val:.0f}   [typical {once + r['N']*(search+fixed):.0f}, sim {r['sim']}]")
    r['_search'], r['_fixed'], r['_val'] = search, fixed, val
print('sum', round(sum(r['_val'] for r in rows)))
print('| sheet | N | A px2 | w | h | g | rho | kappa | rho_loc | Ks | Kn | Kw | parts |')
for r in rows: print(f"| {r['sheet']} | {r['N']} | {r['A']:.0f} | {r['w']} | {r['h']} | {r['g']} | {r['rho']} | {r['kappa']} | {r['rl']} | {r['Ks']} | {r['Kn']} | {r['Kw']} | {r['parts']} |")
print('| sheet | f_t | p_in | m1 | x_off | q_n | p_s | Cb | p_L | ex_q | nd_q | iv_e | cmp_iv |')
for r in rows: print(f"| {r['sheet']} | {r['f_t']} | {r['p_in']} | {r['m1']} | {r['x_off']} | {r['q_n']} | {r['p_s']} | {r['Cb']} | {r['p_L']} | {r['ex_q']} | {r['nd_q']} | {r['iv_e']} | {r['cmp_iv']} |")
print('| sheet | seats | queries | cells | entries | exact | near | leader | ivs | cmps | inserts | search | fixed |')
for r in rows: print(f"| {r['sheet']} | {r['seats']} | {r['queries']} | {r['cells']} | {r['entries']} | {r['exact']} | {r['near']} | {r['leader']} | {r['ivs']} | {r['cmps']} | {r['inserts']} | {r['_search']} | {r['_fixed']} |")
