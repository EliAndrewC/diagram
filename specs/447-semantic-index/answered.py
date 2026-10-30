"""Feature 447 amendment 2: "have we already answered this?" - each question asked of the record through the index (its rank among
the record's pages) and through a text search of the record with up to three term sets chosen blind to the pages (each set every
term required, as `make archive-find` does; found when any file of the page's number is among the hits).

    cd /tmp && python3 <clone>/specs/447-semantic-index/answered.py <questions.json> <terms.json> <out.json>
"""

import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "record"))
import semantic_index as si  # noqa: E402

ARCHIVE = pathlib.Path("/diagram/.specify/source-archive")
QDIR = ROOT / "research" / "questions"


def grep(terms: list[str]) -> set[str]:
    """The page numbers whose files hold every term (any case)."""
    got = None
    for w in terms:
        r = subprocess.run(["grep", "-rlIiF", "--include=*.html", "--", w, str(QDIR)], capture_output=True, text=True, check=False)
        nums = {pathlib.Path(f).name[:4] for f in r.stdout.splitlines()}
        got = nums if got is None else got & nums
    return got or set()


def main() -> None:
    questions = json.load(open(sys.argv[1]))
    terms = {t["page"]: t["term_sets"] for t in json.load(open(sys.argv[2]))}
    embed = si.model_embed(pathlib.Path("/diagram/.specify"))
    rows = []
    for q in questions:
        page = q["page"]
        t = time.time()
        hits = si.find(ARCHIVE, ROOT, q["question"], embed, k=200)
        pages: list[str] = []
        for _sim, rel, _s, _e in hits:
            if rel.startswith("research/") and pathlib.Path(rel).name[:4] not in pages:
                pages.append(pathlib.Path(rel).name[:4])
        rank = pages.index(page) + 1 if page in pages else None
        tries = []
        for ts in terms.get(page, [])[:3]:
            got = grep(ts)
            tries.append({"terms": ts, "pages": len(got), "found": page in got})
        first = next((i + 1 for i, x in enumerate(tries) if x["found"]), None)
        rows.append({"page": page, "question": q["question"], "semantic_page_rank": rank, "text_tries": tries,
                     "text_found_on_try": first, "seconds": round(time.time() - t, 2)})
        print(json.dumps(rows[-1], ensure_ascii=False))
    json.dump(rows, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
