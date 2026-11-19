import sys, glob, os, json
sys.path.insert(0, '/tmp/t198')
import sim3
os.chdir('/diagram/.clones/diagram-backlog')
S = sorted(glob.glob('pool/magistracies/*/*.svg')+glob.glob('pool/country-shrines/*/*.svg'))
cfgs = [('8g, no first strip', dict(first_to=None, chunk_g=8)), ('4g, no first strip', dict(first_to=None, chunk_g=4)),
        ('2g then 4g', dict(first_to=2.0, chunk_g=4)), ('2g then 8g', dict(first_to=2.0, chunk_g=8)),
        ('2g then 24px (half cell)', dict(first_to=2.0, chunk_px=24)), ('2g then 48px (one cell)', dict(first_to=2.0, chunk_px=48)),
        ('2g then 96px (two cells)', dict(first_to=2.0, chunk_px=96)), ('48px, no first strip', dict(first_to=None, chunk_px=48))]
for name, kw in cfgs:
    tot = 0; sweep = 0; a = {}
    for p in S:
        st = sim3.run(p, **kw)
        tot += sum(st[k] for k in sim3.KEYS)
        sweep += st['sweep_cells'] + st['sweep_entries'] + st['sweep_intervals'] + st['sweep_cmp'] + st['q_sweep']*2
        for k in ('within2g', 'leader', 'stop_first', 'stop_later', 'later_chunks'): a[k] = a.get(k, 0) + st[k]
    print(f'{name:28s} work {tot:6d} sweep-part {sweep:6d}', a)
