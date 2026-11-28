"""461 T23 (FR-010): each window's concurrency from the sampler - mean trees held (the samples are evenly spaced,
so the mean is time-weighted), median load1 against the cores, sample count.
Usage: python3 -I t23-conc.py SAMPLES_JSONL T0 T1 [T2 ...]"""
import json, sys, statistics
path, cuts = sys.argv[1], sys.argv[2:]
rows = []
for l in open(path):
    try:
        d = json.loads(l)
    except Exception:
        continue
    rows.append((d.get("utc", ""), len(d.get("held") or []), d.get("load1"), d.get("cores")))
for a, b in zip(cuts, cuts[1:]):
    w = [r for r in rows if a <= r[0] < b and r[2] is not None]
    if not w:
        print(f"{a}..{b}: no samples"); continue
    print(f"{a}..{b}: {len(w)} samples, trees held mean {statistics.mean(r[1] for r in w):.2f}, "
          f"load1 median {statistics.median(r[2] for r in w):.1f} on {w[0][3]} cores, max {max(r[2] for r in w):.1f}")
