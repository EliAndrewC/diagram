#!/usr/bin/env python3
"""The seeded-fault runs of feature 250 D6: does a check still find what it found when it reads a bundle?

Five agents, two legs, three runs a leg (the tier rule). Every run of a case reads the SAME bytes; the
legs differ only in WHERE the files are: the TREE leg reads them under `research/_seeded250/`, where the
harness attaches every CLAUDE.md above them; the BUNDLE leg reads them under `/tmp/l7r-seeded/`, where it
attaches none. A run is judged on whether its REPORT names every planted fault.

    seeded.py setup          the base bundles, the plants, one directory per run, the prompts
    seeded.py run            the 18 headless sessions, three at a time (hooks off, as feature 251's were)
    seeded.py judge          which planted faults each run's report names
    seeded.py clean          removes research/_seeded250/ from the tree

The runs are headless sessions started in this clone (`claude -p --agent <name>`) because the parent
session's Agent tool loads the MIRROR's agent files, which do not carry the bundle contract yet.
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
CLONE = HERE.parents[2]
SKILL = CLONE / ".claude/skills/diagram"
BASE = pathlib.Path("/tmp/l7r-seeded")
TREE = SKILL / "research" / "_seeded250"
RUNS = 3

RF_SEC = "010-how-far-past-the-bank-does-a-bridge-land"
QC_SEC = "020-how-densely-is-a-quarter-built-and-what-counts-as-empty-ground"

#: case -> (agent, the planted faults as {label: regex a report naming it must match})
CASES = {
    "rf": ("record-format", {
        "SESSION NOTE: the Grounds field": r"Grounds|LANDING_FT|_geom/ways\.py",
        "HISTORY: what the entry used to say": r"used to (say|give)|corrected to 10|6 ft for the landing",
        "SESSION NOTE: the TODO": r"TODO|re-run the source pass",
        "VOCABULARY: corbel": r"corbel",
    }),
    "qc": ("quote-check", {
        "a mark on a sentence its quote does not support": r"jokamachi[^\n]{0,400}(DOES-NOT-SUPPORT|PARTIAL|does not support|misplaced|wrong sentence)|(DOES-NOT-SUPPORT|does not support|misplaced|wrong sentence)[^\n]{0,400}jokamachi",
        "the unfootnoted 60 square meters": r"60 square",
    }),
    "sa": ("source-applicability", {
        "the missing limit: the article's maintenance banners": r"banner|large language model|LLM|machine-generated|inline citation",
    }),
    "ed": ("entry-drift", {
        "DRIFTED on the modal's two thirds": r"DRIFTED[\s\S]{0,1500}(two.thirds|tenth|1/10)|(two.thirds|tenth|1/10)[\s\S]{0,1500}DRIFTED",
    }),
    "sr": ("source-reader", {
        "CONTRADICTED: the page gives 70%, not 90%": r"CONTRADICTED[\s\S]{0,800}70\s?%|70\s?%[\s\S]{0,800}CONTRADICTED",
        "READ: the density contrast": r"much more densely populated",
    }),
}
#: the cases added on the plan review of 2026-09-26 (entry-drift and source-reader are bundled too)
LATER = ("ed", "sr")


def sh(cmd: list[str], cwd: pathlib.Path = SKILL) -> str:
    got = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if got.returncode:
        raise SystemExit(f"seeded: {' '.join(cmd)} failed:\n{got.stdout}{got.stderr}")
    return got.stdout


def plant(path: pathlib.Path, pairs: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert text.count(old) == 1, (path.name, old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def setup(only: tuple[str, ...] = ()) -> None:
    base = {c: BASE / f"base-{c}" for c in CASES}
    if only:
        setup_later(base)
    else:
        shutil.rmtree(BASE, ignore_errors=True)
        shutil.rmtree(TREE, ignore_errors=True)
        setup_first(base)
    for case, (agent, _faults) in CASES.items():
        if (only and case not in only) or (not only and case in LATER):
            continue
        make_runs(case, agent, base)
    print(f"seeded: run directories under {BASE}; tree copies under {TREE}")


def setup_later(base: dict[str, pathlib.Path]) -> None:
    # entry-drift: the section now says a tenth where the modal still says two thirds
    sh(["make", "check-bundle", "PAGE=fields", "SECTION=190", "NO_QUOTES=1", "KIND=WetPaddy", f"OUT={base['ed']}"])
    frag = next(p for p in base["ed"].glob("190-*.html") if not p.name.endswith(".notes.html"))
    plant(frag, [("more than two-thirds of the nation's paddies became dry paddy", "about one tenth of the nation's paddies became dry paddy"),
                 ("全国の水田の2/3以上は乾田となったといわれる", "全国の水田の1/10ほどが乾田となったといわれる")])
    # source-reader: the saved Edo page, and three claims with known answers
    shutil.copytree(base["sa"], base["sr"])
    m = base["sr"] / "MANIFEST.md"
    m.write_text(m.read_text(encoding="utf-8").replace(str(base["sa"]), str(base["sr"])), encoding="utf-8")


def setup_first(base: dict[str, pathlib.Path]) -> None:
    sh(["make", "check-bundle", "PAGE=ways", "SECTION=010", "NO_QUOTES=1", f"OUT={base['rf']}"])
    sh(["make", "check-bundle", "PAGE=cities/sizing", "SECTION=020", f"OUT={base['qc']}"])
    sh(["make", "check-bundle", "KEY=edo-enwiki", f"OUT={base['sa']}"])
    # rf: a visible Grounds field, a history sentence, a TODO to a session, an undefined term on the list
    rf = base["rf"] / f"{RF_SEC}.html"
    text = rf.read_text(encoding="utf-8")
    first_p = text.index("<p>", text.index("</h2>"))
    planted = ("<p>Grounds: LANDING_FT = 10.0 in settlement/_geom/ways.py. This section used to give 6 ft for the landing; "
               "it was corrected to 10 ft on 2026-09-12. TODO: re-run the source pass on this entry. Where the bank is soft "
               "the girder rests on a corbel set into the abutment. ")
    rf.write_text(text[:first_p] + planted + text[first_p + 3:], encoding="utf-8")
    plant(base["rf"] / "prepass.txt", [("## What to hand the check", "(also raised: corbel (1))\n\n## What to hand the check")])
    # qc: the jokamachi mark moved to a sentence its quote does not support; an unfootnoted real-world figure
    qc = base["qc"] / f"{QC_SEC}.html"
    plant(qc, [
        ('with no gap between them.<sup class="fn" data-note="jokamachi-wiki"></sup>', "with no gap between them. Edo's townsmen's lots averaged about 60 square meters."),
        ("so that a government ward's yamen does not make the ward read as under-built.", 'so that a government ward\'s yamen does not make the ward read as under-built.<sup class="fn" data-note="jokamachi-wiki"></sup>'),
    ])
    # sa: the registry entry as it stood before the slice added the maintenance-banner limit (e9124caf)
    (base["sa"] / "sources" / "edo-enwiki.html").write_text(
        sh(["git", "-C", str(CLONE), "show", "e9124caf:.claude/skills/diagram/research/sources/010-works-cited/4220-edo-enwiki.html"]), encoding="utf-8")


def make_runs(case: str, agent: str, base: dict[str, pathlib.Path]) -> None:
    for leg in ("tree", "bundle"):
        for n in range(1, RUNS + 1):
            name = f"{case}-{leg}-{n}"
            out = BASE / name
            if leg == "bundle":
                shutil.copytree(base[case], out)
                m = out / "MANIFEST.md"
                m.write_text(m.read_text(encoding="utf-8").replace(str(base[case]), str(out)), encoding="utf-8")
                files = f"Your bundle is {out}/MANIFEST.md - read it first, then only the files it lists."
            else:
                out.mkdir(parents=True)
                where = TREE / name
                shutil.copytree(base[case], where)
                (where / "MANIFEST.md").unlink()
                listed = "\n".join(f"- {p}" for p in sorted(where.rglob("*")) if p.is_file())
                files = (f"No bundle: read these files, which are under the repository, and nothing else:\n{listed}\n"
                         f"Write your report to {out}/REPORT.md.")
            (out / "prompt.txt").write_text(PROMPTS[case].format(files=files), encoding="utf-8")
            (out / "agent").write_text(agent, encoding="utf-8")


PROMPTS = {
    "ed": ("You are given ONE pair: the modal class `WetPaddy` (its docstring, `kind.txt`, is what the map says) and the research section it was "
           "written from (the question fragment and its notes). The section's body changed and the modal's prose did not. {files}\n"
           "Report IN-STEP, DRIFTED or CANNOT-TELL, as your contract says."),
    "sr": ("Report, claim by claim, whether the saved page says it: READ with the verbatim passage, CONTRADICTED with the passage that says "
           "otherwise, or NOT-FOUND. The page is en.wikipedia 'Edo' (https://en.wikipedia.org/wiki/Edo), saved in full under pages/ - grep "
           "it; do not fetch. {files}\nThe claims:\n1. Edo's townspeople lived in a far more densely populated area than the samurai class.\n"
           "2. Samurai and daimyo residences occupied up to 90% of Edo's area.\n3. Temples and shrines occupied roughly 15% of the city's surface."),
    "rf": "Check ONE research entry the way its reader meets it. {files}\nRule on EVERY word on the prepass's WORDS TO RULE ON list. Report VOCABULARY, SESSION NOTE and HISTORY findings.",
    "qc": ("Check ONE research entry's footnotes: per note READABLE, VERBATIM, SUPPORTS, then every real-world assertion in the entry's "
           "prose that carries no footnote. {files}\nThe quote-verbatim pre-pass has checked the quotations character for character; "
           "the Chang PDF is image-only - judge its support from the quotation as given. Do not fetch a page the pre-pass calls VERBATIM."),
    "sa": ("Judge ONE source and its registry write-up: `edo-enwiki`. Its new use: the sizing page cites it QUALITATIVELY for the statement "
           "that a commoner quarter packs far denser than a samurai ward, and that a great lord's residence spread over large grounds; no "
           "number reaches a map or a rule. {files}\nThe page's full text is saved under pages/ in the same directory as the registry entry - "
           "grep it; do not re-fetch it. Verdict: APPLICABLE / APPLICABLE-WITH-LIMITS / NOT-APPLICABLE, and whether the write-up's limits are "
           "HONEST, MISSING one, or OVERSTATED."),
}


def run_one(out: pathlib.Path) -> str:
    sid = str(uuid.uuid4())
    (out / "session").write_text(sid, encoding="utf-8")
    cmd = ["timeout", "1500", "claude", "-p", "--agent", (out / "agent").read_text().strip(), "--session-id", sid,
           "--settings", '{"disableAllHooks": true}', "--permission-mode", "bypassPermissions", "--output-format", "json"]
    with (out / "prompt.txt").open() as stdin, (out / "run.json").open("w") as so, (out / "run.err").open("w") as se:
        rc = subprocess.run(cmd, cwd=CLONE, stdin=stdin, stdout=so, stderr=se, check=False).returncode
    return f"{out.name} rc={rc}"


def run(only: tuple[str, ...] = ()) -> None:
    dirs = sorted(p for p in BASE.iterdir() if (p / "prompt.txt").is_file() and (not only or p.name.split("-")[0] in only))
    with ThreadPoolExecutor(max_workers=3) as pool:
        for line in pool.map(run_one, dirs):
            print(line, flush=True)
    print("ALL DONE", flush=True)


def transcript(sid: str) -> pathlib.Path | None:
    return next(iter((pathlib.Path.home() / ".claude/projects").glob(f"*/{sid}.jsonl")), None)


def judge() -> int:
    sys.path.insert(0, str(HERE)); sys.path.insert(0, str(CLONE / "scripts"))
    import tokens  # noqa: PLC0415

    rows = []
    for out in sorted(p for p in BASE.iterdir() if (p / "prompt.txt").is_file()):
        case, leg, n = out.name.split("-")
        report = (out / "REPORT.md").read_text(encoding="utf-8") if (out / "REPORT.md").is_file() else ""
        reply = ""
        try:
            reply = json.loads((out / "run.json").read_text(encoding="utf-8")).get("result") or ""
        except (OSError, ValueError):
            pass
        text = report or reply
        found = {label: bool(re.search(rx, text, re.I | re.S)) for label, rx in CASES[case][1].items()}
        tp = transcript((out / "session").read_text().strip()) if (out / "session").is_file() else None
        msgs = tokens.messages(tokens.records(tp)) if tp else []
        recs = tokens.records(tp) if tp else []
        nested = sum(1 for r in recs if r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "nested_memory")
        rows.append({"run": out.name, "case": case, "leg": leg, "found": found, "report_file": bool(report),
                     "reply_lines": len(reply.strip().splitlines()), "turns": len(msgs), "nested": nested,
                     "input": sum(m["fresh"] + m["cached"] for m in msgs), "output": sum(m["output"] for m in msgs),
                     "peak": max((m["fresh"] + m["cached"] for m in msgs), default=0)})
    for r in rows:
        hit = sum(r["found"].values())
        missed = [k for k, v in r["found"].items() if not v]
        print(f"{r['run']:<14} faults {hit}/{len(r['found'])}  nested {r['nested']}  turns {r['turns']:>2}  input {r['input']:>9,}  peak {r['peak']:>7,}  "
              f"out {r['output']:>6,}  report-file {r['report_file']!s:<5} reply-lines {r['reply_lines']:>3}  {'MISSED: ' + '; '.join(missed) if missed else ''}")
    (HERE / "seeded-results.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return 0


def main(argv: list[str]) -> int:
    verb = argv[0] if argv else ""
    if verb == "setup":
        setup(tuple(argv[1:]))
    elif verb == "run":
        run(tuple(argv[1:]))
    elif verb == "judge":
        return judge()
    elif verb == "clean":
        shutil.rmtree(TREE, ignore_errors=True)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
