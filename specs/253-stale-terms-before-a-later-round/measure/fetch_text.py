#!/usr/bin/env python3
"""fetch_text.py URL OUT - the page's visible text, fetched and decoded by `_quote_verbatim.Pages` (one attempt, a
timeout, charset honored). Prints `FETCHED <chars>` or the state and why. The source-fetcher experiment's one tool."""
import importlib.util, pathlib, sys
CLONE = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("qv", CLONE / "scripts" / "_quote_verbatim.py"); qv = importlib.util.module_from_spec(spec); spec.loader.exec_module(qv)
got = qv.Pages().get(sys.argv[1])
if got["state"] == "FETCHED":
    pathlib.Path(sys.argv[2]).write_text(got["text"], encoding="utf-8"); print("FETCHED", len(got["text"]), "chars ->", sys.argv[2])
else:
    print(got["state"], "-", got.get("why", ""))
