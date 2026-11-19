import sys, json
sys.path.insert(0, '/tmp/t198')
import inventory as inv, hybrid
orig = inv.inventory
def mk(mode):
    def f(p):
        vb, shapes, caps = orig(p)
        if mode == 'reverse': caps = caps[::-1]
        if mode == 'inside_first':
            caps = sorted(caps, key=lambda c: not (c['fbox'] and c['wN'] <= c['fbox'][2]-c['fbox'][0] and c['hN'] <= c['fbox'][3]-c['fbox'][1]))
        if mode == 'small_first': caps = sorted(caps, key=lambda c: c['wN']*c['hN'])
        if mode == 'big_first': caps = sorted(caps, key=lambda c: -c['wN']*c['hN'])
        return vb, shapes, caps
    return f
KEYS = ['queries','cells','entries','exact_segs','seats','near_dist','sweep_intervals','leader_dist','caption_inserts','swept']
for mode in ['declared','reverse','inside_first','small_first','big_first']:
    hybrid.inventory = mk(mode)
    per = {}
    for p in sys.argv[1:]:
        r = hybrid.run(p, 48.0)
        per[p.split('/')[-1][:-4]] = sum(r[k] for k in KEYS)
    print(mode, per, 'sum', sum(per.values()))
