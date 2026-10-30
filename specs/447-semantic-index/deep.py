"""Feature 447: each case's rank in the first 200, the Japanese cases also asked in Japanese, and a search's time split."""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts" / "record"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import semantic_index as si
from trial import CASES, ARCHIVE, ROOT
JA = {
 "67/67dc5aaf3516": "江戸の裏長屋の路地の幅はどれくらいか",
 "05/052e5a087064": "農家の庭(脱穀場)の広さはどう決められたか",
 "3e/3e64bd55f251": "江戸時代後期の江戸に銭湯はいくつあったか",
 "4a/4a0919d8aa81": "砺波の散居村の屋敷林に杉は何本あるか",
 "b5/b597771536b4": "有田の登り窯の長さ",
 "f4/f4285e6ee539": "稲刈りの何日前に田の水を落とすか",
 "3c/3c4a00e776c7": "松江の武家屋敷の主屋の広さ",
}
embed = si.model_embed(pathlib.Path("/diagram/.specify"))
t = time.time(); embed(["warm"]); print("embed one", round(time.time() - t, 3))
t = time.time()
shards = [si.load_shard(p) for p in sorted((ARCHIVE / si.INDEX_DIR / si.MODEL_DIR).glob("*.npz"))]
print("load shards", round(time.time() - t, 2), sum(len(z["fps"]) for z in shards))
rows = []
for q, _terms, truth, page, lang in CASES:
    for qq, ql in [(q, "en")] + ([(JA[truth], "ja")] if truth in JA else []):
        hits = si.find(ARCHIVE, ROOT, qq, embed, k=200)
        r = next((i + 1 for i, h in enumerate(hits) if h[1].startswith(truth)), None)
        pr = next((i + 1 for i, h in enumerate(hits) if f"/{page}-" in h[1]), None)
        files = []
        for h in hits:
            f = h[1].split("/")[1] if not h[1].startswith("research") else h[1]
            if f not in files: files.append(f)
        fr = next((i + 1 for i, f in enumerate(files) if truth.endswith(f)), None)
        rows.append({"truth": truth, "q_lang": ql, "passage_rank": r, "file_rank": fr, "page_rank": pr})
        print(json.dumps(rows[-1]))
json.dump(rows, open(sys.argv[1], "w"), indent=1)
