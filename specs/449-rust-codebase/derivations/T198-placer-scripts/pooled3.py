import sys, glob, os, json
sys.path.insert(0, '/tmp/t198')
import sim3, inventory as inv
os.chdir('/diagram/.clones/diagram-backlog')
S = sorted(glob.glob('pool/magistracies/*/*.svg')+glob.glob('pool/country-shrines/*/*.svg'))
KW = dict(first_to=None, chunk_px=48.0)
def tot(**kw):
    T = {}
    for p in S:
        st = sim3.run(p, **{**KW, **kw})
        for k, v in st.items(): T[k] = T.get(k, 0) + v
    T['work'] = sum(T[k] for k in sim3.KEYS); return T
T = tot(); print(json.dumps(T))
for kw in (dict(k=0.85), dict(k=1.15), dict(wrap='B')): print(kw, tot(**kw)['work'] / T['work'])
# order spread
orig = inv.inventory
def mk(mode):
    def f(p):
        vb, sh, caps = orig(p)
        if mode == 'reverse': caps = caps[::-1]
        if mode == 'inside_first': caps = sorted(caps, key=lambda c: not (c['fbox'] and c['wN'] <= c['fbox'][2]-c['fbox'][0] and c['hN'] <= c['fbox'][3]-c['fbox'][1]))
        if mode == 'small_first': caps = sorted(caps, key=lambda c: c['wN']*c['hN'])
        if mode == 'big_first': caps = sorted(caps, key=lambda c: -c['wN']*c['hN'])
        return vb, sh, caps
    return f
base = None; worst = {}; sums = {}
for mode in ['declared', 'reverse', 'inside_first', 'small_first', 'big_first']:
    sim3.inv.inventory = mk(mode); per = {}
    for p in S:
        st = sim3.run(p, **KW); per[p] = sum(st[k] for k in sim3.KEYS)
    if base is None: base = per
    sums[mode] = sum(per.values())
    for p in S: worst[p] = max(worst.get(p, 1), per[p]/base[p])
sim3.inv.inventory = orig
print('order: sums', sums, 'worst per sheet', {p.split('/')[-1]: round(v, 3) for p, v in worst.items()})
