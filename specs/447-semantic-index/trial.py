"""Feature 447's comparison: each question, its known answering file in the archive, today's text search with the terms a session
would try first, and the semantic index's top ten."""

import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts" / "record"))
import semantic_index as si  # noqa: E402

ARCHIVE = pathlib.Path("/diagram/.specify/source-archive")
ROOT = pathlib.Path(__file__).resolve().parents[2]

# (question, terms a session would try first, the known answering file's capture folder, the record page it answered, language)
CASES = [
    ("How big and how deep were the fish ponds of a dike-pond district?", "fish pond|depth", "2b/2b106432097b", "0019", "en"),
    ("How wide was the moat around a Chinese walled county town?", "moat|width", "5c/5c56a8ffcc30", "0151", "en"),
    ("How much more water does a hard-working horse need?", "horse|water", "7e/7ea522445c8c", "0195", "en"),
    ("How were Japanese earthen compound walls built?", "earthen wall", "6e/6e2b3e8f080c", "0092", "en"),
    ("Why would a ditch be dug across a slope rather than down it?", "ditch|slope", "1d/1d6eded5f7e6", "0054", "en"),
    ("Were there narrow alleys running between the main lanes of old Beijing?", "alley|Beijing", "fd/fd80f6d7ed33", "0121", "en"),
    ("How were the bridges along a canal towpath built?", "towpath|bridge", "71/71b5f74369cc", "0089", "en"),
    ("Which torii is the first one on a shrine's approach?", "torii|first", "1e/1e4316f6bb18", "0220", "en"),
    ("How much labor did making ramie cloth take?", "ramie|labour", "42/4288c884928c", "0312", "en"),
    ("Did Chinese farm households keep pigs beneath the privy?", "pig|toilet", "f4/f4eeeca27b8b", "0048", "en"),
    ("How wide was the alley between the back-row tenements in Edo?", "alley|tenement", "67/67dc5aaf3516", "0152", "ja"),
    ("How was the size of a farmhouse's threshing yard reckoned?", "threshing yard|mat", "05/052e5a087064", "0037", "ja"),
    ("How many public bathhouses did Edo have in the early nineteenth century?", "bathhouse|Edo", "3e/3e64bd55f251", "0202", "ja"),
    ("How many cedar trees stood in a Tonami farmstead grove?", "cedar|Tonami", "4a/4a0919d8aa81", "0072", "ja"),
    ("How long were the climbing kilns at Arita?", "climbing kiln|Arita", "b5/b597771536b4", "0192", "ja"),
    ("How long before the rice harvest was the paddy's water let off?", "drain|harvest", "f4/f4285e6ee539", "0009", "ja"),
    ("How large was the main house of a samurai residence in Matsue?", "Matsue|samurai", "3c/3c4a00e776c7", "0140", "ja"),
]


def text_search(terms: str) -> list[str]:
    files = None
    for w in [t for t in terms.split("|") if t]:
        r = subprocess.run(["grep", "-rlIiF", "--include=*.txt", "--", w, str(ARCHIVE)], capture_output=True, text=True, check=False)
        got = {str(pathlib.Path(f).parent.relative_to(ARCHIVE)) for f in r.stdout.splitlines() if "/.git/" not in f}
        files = got if files is None else files & got
    return sorted(files or ())


def main() -> None:
    embed = si.model_embed(pathlib.Path("/diagram/.specify"))
    rows = []
    for q, terms, truth, page, lang in CASES:
        t = time.time()
        hits = si.find(ARCHIVE, ROOT, q, embed, k=10)
        dt = time.time() - t
        ranks = [i + 1 for i, h in enumerate(hits) if h[1].startswith(truth)]
        page_ranks = [i + 1 for i, h in enumerate(hits) if f"/{page}-" in h[1]]
        ts = text_search(terms)
        held = any(f.startswith(truth) for f in ts)
        rows.append({
            "question": q, "lang": lang, "terms": terms, "truth": truth,
            "semantic_rank": ranks[0] if ranks else None, "record_page_rank": page_ranks[0] if page_ranks else None,
            "text_hits": len(ts), "text_holds_truth": held, "seconds": round(dt, 2),
        })
        print(json.dumps(rows[-1], ensure_ascii=False))
    json.dump(rows, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
