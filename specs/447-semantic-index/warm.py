"""Feature 447: a search with the model and every shard already loaded, stacked into one matrix."""
import pathlib, sys, time
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts" / "record"))
import semantic_index as si
A = pathlib.Path("/diagram/.specify/source-archive")
embed = si.model_embed(pathlib.Path("/diagram/.specify"))
embed(["warm"])
t = time.time()
zs = [si.load_shard(p) for p in sorted((A / si.INDEX_DIR / si.MODEL_DIR).glob("*.npz"))]
M = np.concatenate([z["vecs"] for z in zs]).astype(np.float32)
print("load and stack", round(time.time() - t, 2), M.shape)
for q in ["有田の登り窯の長さ", "How wide was the moat around a Chinese walled county town?", "How much more water does a hard-working horse need?"]:
    t = time.time(); v = embed([q])[0]; s = M @ v; top = np.argpartition(-s, 10)[:10]; top = top[np.argsort(-s[top])]
    print("warm search", round(time.time() - t, 3))
