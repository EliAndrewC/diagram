"""Score the gm-question detector (scripts/hooks/lib/hm_gm_question.py) on past final messages (feature 429 FR-002).

Usage: python3 detect.py <finals.json from finals.py> [labels json ...]
Prints how many final messages it flags, and per labels file the confusion counts against the independent labels.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "scripts" / "hooks" / "lib"))
import hm_gm_question as h  # noqa: E402

finals = json.load(open(sys.argv[1]))
print(f"flagged {sum(1 for f in finals if h.asks(f['text']))} of {len(finals)}")
for lab in sys.argv[2:]:
    c = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for k, v in json.load(open(lab)).items():
        hit, ask = bool(h.asks(finals[int(k)]["text"])), v["label"] == "ASKS"
        c["tp" if ask and hit else "fn" if ask else "fp" if hit else "tn"] += 1
    print(lab, c)
