"""Land the write-ups in SOURCES.html (feature 211, T08). Run once from the skill root.

Input: the checked drafts, one file per batch, each a run of `<h3 id="key">...</h3>` followed by the two paragraphs
`<p><em>What it is:</em> ...</p>` and `<p><em>Why it applies, and its limits:</em> ...</p>`. For each key the two
paragraphs are inserted into the registry entry directly after its citation line (the entry's first `<p>`), before
`Used for:`. A key already carrying a write-up is replaced. Asserts every draft key exists in the registry and every
cited key received both paragraphs. `--check` reports without writing.
"""

from __future__ import annotations

import glob
import re
import sys

from l7r.diagram.interactive.sources import RESEARCH_DIR

DRAFTS = sys.argv[1]
CHECK = "--check" in sys.argv
_DRAFT = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)"><code>\1</code></h3>\s*(<p><em>What it is:</em>.*?</p>)\s*(<p><em>Why it applies, and its limits:</em>.*?</p>)', re.S)
_ENTRY = re.compile(r'(<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*<p>.*?</p>\n)(?:<p><em>What it is:</em>.*?</p>\n<p><em>Why it applies, and its limits:</em>.*?</p>\n)?', re.S)

drafts: dict[str, tuple[str, str]] = {}
for path in sorted(glob.glob(f"{DRAFTS}/batch-*.html")):
    text = open(path, encoding="utf-8").read()
    found = _DRAFT.findall(text)
    assert found, path
    for key, what, why in found:
        assert key not in drafts, f"duplicate draft {key}"
        for para in (what, why):
            assert "\u2014" not in para and "\u2013" not in para, f"{key}: a dash"
        drafts[key] = (re.sub(r"\s+", " ", what).strip(), re.sub(r"\s+", " ", why).strip())
print(f"{len(drafts)} drafts")

path = f"{RESEARCH_DIR}/SOURCES.html"
src = open(path, encoding="utf-8").read()
keys_in_registry = set(re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)">', src))
missing = sorted(set(drafts) - keys_in_registry)
assert not missing, f"drafts for keys the registry lacks: {missing}"
landed: list[str] = []


def _sub(m: re.Match[str]) -> str:
    key = m.group(2)
    if key not in drafts:
        return m.group(0)
    landed.append(key)
    what, why = drafts[key]
    return f"{m.group(1)}{what}\n{why}\n"


out = _ENTRY.sub(_sub, src)
print(f"landed {len(landed)} of {len(drafts)}; not landed: {sorted(set(drafts) - set(landed))}")
assert len(landed) == len(drafts)
if not CHECK:
    open(path, "w", encoding="utf-8").write(out)
    print(f"wrote {path} ({len(out)} bytes, was {len(src)})")
