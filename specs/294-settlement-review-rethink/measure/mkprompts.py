import sys,pathlib
S=pathlib.Path(sys.argv[1])
ASK = {
    "settlement-review": "the WHOLE-MAP review of {on}: {occasion}. Run your contract's whole-map sweeps on it.",
    "building-review": "the review of the sheet {on}: {occasion}. Run the sections of your contract this occasion owes.",
    "glyph-check": "the glyph check of the element {subject!r}, on {on}: {occasion}. Judge that element where it stands on this map - nothing else on the map is under review.",
    "size-audit": "the size audit of {subject!r} on {on}: {occasion}. Anchor that kind's size; nothing else is under review.",
    "fix-check": "the fix check on {on}: {occasion}. Answer the GM's complaint at fit zoom first, then whether the fix fired and whether its record can bear it.",
}
DISPATCH = """UNIT: {slug}
{check} - {ask}

This prompt was written by the tooling (feature 294): one agent per owed unit, and the pair guard refuses a dispatch that
names more than one. Do not review anything else - its own agent has it - and wait for nothing but your own work.

Clone: {clone} (the directory holding `.git/review-snapshot/`; run the `make` targets from its
`.claude/skills/diagram/`). Engine key: not computed. The gate went green on this content before this dispatch.

Snapshot - read THESE:
  after (the clone): {after}
  before (main):     {before}
{extra}
Follow your contract end to end, then `make review-verdict UNIT={slug} VERDICT=<PASS|NEEDS-WORK|NOT-REVIEWABLE> [FINDINGS=<json file>]`
as your last act, and quote the line it prints.
"""
CASES = {
 "glyph": ("glyph-check","drying rack","sawada","glyph-redrawn: drying rack (the threshing yard's rack by the house, feature 282's racks gathered by the houses, redrawn)",True,""),
 "settle": ("settlement-review","ashigawa","ashigawa","a map new to the pool (pool/hamlets/ashigawa)",False,""),
 "fix": ("fix-check","kashikawa","kashikawa",'gm-fix: kashikawa - "two ditches run side by side down the paddies, like a doubled line"',True,
   "\nThe feature's record offered as verifying the fix (tasks.md verify note): `drop_twin_deliveries` takes every delivery that would\nrun as a twin out of the comb's planned channel list before it is drawn; asked over the comb's plan for Kashikawa it returns\n0 pairs left, so the twin is gone.\n"),
 "building": ("building-review","hoshigaoka-shrine","hoshigaoka-shrine","layout-revised: hoshigaoka-shrine (the monk's kitchen garden moved for its six hours of sun)",True,""),
 "size": ("size-audit","latrine","hoshigaoka-shrine","a sized kind new to the sheet: `latrine` on hoshigaoka-shrine (no band in types.json)",True,""),
}
import re
for leg in ("opus","sonnet"):
    T=S/f"{leg}-tree"
    for key,(check,subj,on,occ,hasmain,extra) in CASES.items():
        slug=f"{check}--{re.sub(r'[^A-Za-z0-9]+','-',subj).strip('-').lower()}"
        snap=T/".git"/"review-snapshot"/slug
        txt=DISPATCH.format(slug=slug,check=check,ask=ASK[check].format(on=on,subject=subj,occasion=occ),clone=T,
            after=snap/"clone",before=(snap/"main") if hasmain else "unavailable (main has no such map)",extra=extra)
        for n in ((1,) if leg=="opus" else (1,2,3)):
            d=S/"runs"/f"{key}-{leg}{n}"; d.mkdir(parents=True,exist_ok=True)
            (d/"prompt.txt").write_text(txt)
            t=d/"tree"
            if not t.exists(): t.symlink_to(T)
print("ok")
