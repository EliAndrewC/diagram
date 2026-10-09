"""Feature 312 T23: build the filter's calibration bundles (plan D6, research.md R1, R2). Run from the clone's root:
    python3 specs/312-uncited-source-catalog/measurement/calibrate.py OUT
40 POSITIVES - cited pages with saved text, a seeded random sample of the archive (keys, archived, 800+ characters and
under 15,000 estimated tokens, so the control stays a handful of bundles) - and the 40 NEGATIVES this session labeled
(`negatives.json`), shuffled with a seed, under opaque ids, grouped into bundles by `_uncited.groups`. Each bundle's labels
are written OUTSIDE the bundle (`<OUT>-answers/<bundle>.json`), so the agent cannot read them."""
import json, pathlib, random, sys
sys.path.insert(0, "scripts")
import _archive as ar, _sources as src, _uncited as un
root = pathlib.Path(".").resolve(); home = src.home(root); out = pathlib.Path(sys.argv[1])
here = pathlib.Path(__file__).parent
neg = json.loads((here / "negatives.json").read_text())
rows = [json.loads(p.read_text()) for p in ar.row_files(root)]
pool = sorted(r["url"] for r in rows if r.get("keys") and r.get("outcome", "").startswith("archived"))
pool = [u for u in pool if (t := un.text_of(home, u)) and len(t) > 800 and un.tokens(t) < 15_000]
random.seed(312)
pos = random.sample(pool, 40)
pages = [(u, "KEEP") for u in pos] + [(x["url"], "NOT-KEPT") for x in neg]
random.shuffle(pages)
texts = {u: un.text_of(home, u) for u, _ in pages}
missing = [u for u, _ in pages if not texts[u]]
assert not missing, missing
label = dict(pages)
ids = {u: f"p{n:05d}" for n, (u, _) in enumerate(pages, 1)}
for k, group in enumerate(un.groups([(u, texts[u]) for u, _ in pages]), 1):
    d = out / f"312-control-{k:02d}"
    un.write_bundle(d, [(ids[u], u, t) for u, t in group])
    (out.parent / f"{out.name}-answers").mkdir(exist_ok=True)
    (out.parent / f"{out.name}-answers" / f"{d.name}.json").write_text(json.dumps({ids[u]: label[u] for u, _ in group}, indent=1))
(here / "control.json").write_text(json.dumps({"positives": pos, "negatives": [x["url"] for x in neg], "ids": ids}, ensure_ascii=False, indent=1))
print(len(list(out.glob("312-control-*"))), "bundles")
