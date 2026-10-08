#!/usr/bin/env python3
"""Feature 330, T05 (plan D6): re-aim every live pointer into the retired backlog directory. Run once from the clone
root; kept as the record. A pointer to an entry that became a feature names the feature; a pointer to an entry closed
before this feature (its title survives only in git history) is dropped to "since closed", as FR-007 says; a mention of
the directory as the place deferred work goes says it is filed as a feature now.

    repoint.py [--dry-run]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FW = "future" + "-work"  # split so this record is not its own finding

F = {  # the features the live entries became (filed.json)
    "fabric": "specs/344-fabric-first-generation-research-direction/",
    "funerary": "specs/350-village-funerary-grounds-headman-gate/",
    "shrine-grove": "specs/351-village-generator-draws-no-shrine-grove/",
    "seasonal": "specs/354-seasonal-maps-straw-rick-hasa-frames/",
    "two-ways": "specs/356-ways-meet-material-changes/",
    "knobs": "specs/357-owed-conversion-knob-candidates/",
    "found-280": "specs/358-found-feature280-settlement-reviews-measured-fixed/",
    "torii": "specs/342-torii-drawn-as-elevation-silhouette-mode/",
    "fan-floor": "specs/365-enclosed-fan-tract-floor/",
    "deep-audit": "specs/367-town-deep-audit-open-items/",
}
CLOSED = "the backlog (an entry since closed; git history)"

# (file, line, regex, replacement) - each applied on that one line only
RULES: list[tuple[str, int, str, str]] = [
    ("dev/lessons.md", 4, rf"in `{FW}/`\)", "in a filed feature - `make speckit-todo` lists them)"),
    ("dev/lessons.md", 372, rf"\({FW} audit, 2026-10-07\)", "(the backlog audit, 2026-10-07)"),
    ("docs/buildings.md", 296, rf"an open redraw in \[`{FW}/compounds\.md`\]\(\.\./{FW}/compounds\.md\)", f"an open redraw, [feature 342](../{F['torii']}spec.md)"),
    ("docs/guards.md", 48, rf"waits in `{FW}/cross-cutting\.md` for", "was deferred (the backlog entry since closed; git history) for"),
    ("docs/migration-plan.md", 148, rf"`{FW}/farming-communities\.md` \(the frozen hamlets and villages\), `{FW}/towns\.md` and `{FW}/cities\.md`", "the features filed for them (the frozen hamlets and villages, the towns, the cities - `make speckit-todo` lists them)"),
    ("docs/migration-plan.md", 278, rf"`{FW}/farming-communities\.md`, \"OWED AT CONVERSION: a village's funerary grounds\"", f"`{F['funerary']}`"),
    ("docs/migration-plan.md", 286, rf"in the same {FW} entry", "in the same feature (350)"),
    ("docs/migration-plan.md", 291, rf"`{FW}/cross-cutting\.md`,", f"`{F['fabric']}`,"),
    ("l7r/diagram/CLAUDE.md", 67, rf"The deferred-engineering backlog is \[`{FW}/`\]\(\.\./\.\./{FW}/CLAUDE\.md\), by map type\.", "Deferred engineering is filed as spec-kit features; `make speckit-todo` lists the open ones."),
    ("l7r/diagram/hamletgen/consts.py", 254, rf"flagged in {FW}/ as", "flagged in the backlog as"),
    ("l7r/diagram/hamletgen/hinterland/frame.py", 248, rf"{FW}, \"", "the backlog (since closed), \""),
    ("l7r/diagram/hamletgen/hinterland/parcels.py", 34, rf"See {FW}/, \"the woodland scan vetted a SQUARE\"\.", "The backlog entry \"the woodland scan vetted a SQUARE\" (closed 2026-08-19) has it."),
    ("l7r/diagram/hamletgen/water/brook.py", 178, rf"`{FW}/farming-communities\.md`", CLOSED),
    ("l7r/diagram/hamletgen/water/brook.py", 694, rf"{FW} \"The weir's root lands on", f"`{F['knobs']}` \"The weir's root lands on"),
    ("l7r/diagram/hamletgen/water/brook_rules.py", 212, rf"{FW} \"The weir's root lands on", f"`{F['knobs']}` \"The weir's root lands on"),
    ("l7r/diagram/hamletgen/ways/joints.py", 251, rf"\({FW}/farming-communities\.md, \"Found by feature 280's settlement-reviews\"\)", f"(`{F['found-280']}`)"),
    ("l7r/diagram/hamletgen/ways/law.py", 399, rf"{FW}'s \"one clearance short\"", "the backlog's \"one clearance short\" (since closed)"),
    ("l7r/diagram/hamletgen/ways/law.py", 443, rf"{FW}/farming-communities\.md 2c", "the backlog's 2c (since closed)"),
    ("l7r/diagram/hamletgen/ways/law.py", 471, rf"{FW} 2c's", "the backlog's 2c's (since closed)"),
    ("l7r/diagram/settlement/fields/comb.py", 783, rf"is in {FW}/\.", "is in git history (the backlog entry since closed)."),
    ("l7r/diagram/settlement/fields/features.py", 100, rf"`{FW}` '", "the backlog's (since closed) '"),
    ("l7r/diagram/settlement/land/wet.py", 701, rf"it is recorded in `{FW}/`\.", "it was recorded in the backlog (since closed; git history)."),
    ("l7r/diagram/settlement/water_ways/lanes.py", 60, rf"{FW}, \"", "the backlog (since closed), \""),
    ("l7r/diagram/tools/mapcheck.py", 85, rf"# {FW} entry \"the tier under the T99 engine\"\.", "# backlog entry \"the tier under the T99 engine\" (since closed; git history)."),
    ("l7r/diagram/waterfields/banks.py", 836, rf"and `{FW}/` carries them\.", "and the backlog carried them (since closed; git history)."),
    ("l7r/diagram/waterfields/polder.py", 136, rf"\({FW}, \"Two ways", f"(`{F['two-ways']}`, \"Two ways"),
    ("l7r/diagram/waterfields/ring_rules.py", 94, rf"\({FW} 'the paddy area floor cannot see WIDTH'\)", "(the backlog's 'the paddy area floor cannot see WIDTH', since DECIDED)"),
    ("l7r/diagram/waterfields/ring_rules.py", 111, rf"\({FW} '", "(the backlog's '"),
    ("legacy-hand-authored-pool/capitals/shiro-daika/shiro-daika.notes.md", 3, rf"`{FW}/cross-cutting\.md`, \"Fabric-first generation\"", f"`{F['fabric']}`"),
    ("legacy-hand-authored-pool/capitals/shiro-daika/shiro-daika.notes.md", 220, rf"to {FW}/ per", "to the backlog per"),
    ("legacy-hand-authored-pool/capitals/shiro-daika/shiro-daika.notes.md", 226, rf"\({FW}/ #2, which now carries #5's inputs\)", "(the backlog's #2, which carried #5's inputs - now feature 344)"),
    ("legacy-hand-authored-pool/towns/ubame/ubame.notes.md", 269, rf"\[`\.\./\.\./{FW}/`\]\(\.\./\.\./\.\./{FW}/\)", "the filed features (`make speckit-todo`)"),
    ("pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.notes.md", 43, rf"\({FW}/farming-communities\.md\)", f"(`{F['shrine-grove']}`)"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 105, rf"{FW}/ \(\"Pocket ponds", "the backlog (since closed) (\"Pocket ponds"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 203, rf"logged in {FW}/", "logged in the backlog (since closed)"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 611, rf"\(`{FW}/`\)", "(the backlog, since closed)"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 702, rf"see {FW}/ for", "see git history (the backlog, since closed) for"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 860, rf"\(ledgered in `{FW}/`\)", "(ledgered in the backlog, since closed)"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 896, rf"Also in `{FW}/`\.", "Also in the backlog (since closed)."),
    ("pool/hamlets/inashiro/inashiro.notes.md", 990, rf"\[`{FW}/`\]\(\.\./\.\./\.\./{FW}/\) carries", "The backlog carried"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 996, rf"written up in `{FW}/`\.", "written up in the backlog (since closed)."),
    ("pool/hamlets/inashiro/inashiro.notes.md", 1098, rf"\[`\.\./\.\./{FW}/farming-communities\.md`\]\(\.\./\.\./\.\./{FW}/farming-communities\.md\)", "the backlog (since closed; git history)"),
    ("pool/hamlets/inashiro/inashiro.notes.md", 1452, rf"in `{FW}/farming-communities\.md` \(", "in the backlog (since closed) ("),
    ("pool/hamlets/kashikawa/kashikawa.notes.md", 54, rf"in {FW}/\)", "in the backlog, since closed)"),
    ("pool/hamlets/kashikawa/kashikawa.notes.md", 335, rf"\(ledgered in `{FW}/`\)", "(ledgered in the backlog, since closed)"),
    ("pool/hamlets/kashikawa/kashikawa.notes.md", 454, rf"in `{FW}/farming-communities\.md`\.", "in the backlog (since closed)."),
    ("pool/hamlets/kuwabata/kuwabata.notes.md", 453, rf"`{FW}/cross-cutting\.md` because", "the backlog (since closed) because"),
    ("pool/hamlets/kuwabata/kuwabata.notes.md", 733, rf"{FW}/farming-communities\.md's OPEN 2026-09-28 \(269 B26, PARTIAL\) entry", "The backlog's OPEN 2026-09-28 (269 B26, PARTIAL) entry (since closed)"),
    ("pool/hamlets/kuwabata/kuwabata.notes.md", 748, rf"in `{FW}/farming-communities\.md`", "in the backlog (since closed)"),
    ("pool/hamlets/kuwabata/kuwabata.notes.md", 787, rf"is owed, {FW}\)", "is owed, the backlog, since closed)"),
    ("pool/hamlets/mizuguchi/mizuguchi.notes.md", 310, rf"Both are in `{FW}/`\.", "Both were in the backlog (since closed)."),
    ("pool/hamlets/mizuguchi/mizuguchi.notes.md", 321, rf"\(ledgered in `{FW}/`\)", "(ledgered in the backlog, since closed)"),
    ("pool/hamlets/sawada/sawada.notes.md", 188, rf"logged in `{FW}/` rather", "logged in the backlog (since closed) rather"),
    ("pool/hamlets/sawada/sawada.notes.md", 346, rf"Both in `{FW}/`\.", "Both were in the backlog (since closed)."),
    ("pool/hamlets/sawada/sawada.notes.md", 357, rf"\(ledgered in `{FW}/`\)", "(ledgered in the backlog, since closed)"),
    ("pool/magistracies/ubame-magistracy/ubame-magistracy.notes.md", 3, rf"a canon gap put to the GM, `{FW}/compounds\.md`\)", "a canon gap put to the GM; canon gaps are not tracked as work, GM 2026-10-07)"),
    ("research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html", 23, rf"its ledger, {FW}/closed\.md, was retired", "its ledger was retired"),
    ("research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html", 3, rf"{FW}/farming-communities\.md \"DEFERRED 2026-08-27", f"{F['seasonal']} \"DEFERRED 2026-08-27"),
    ("research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html", 5, rf"\({FW}/farming-communities\.md, \"Seasonal maps\"\)", f"({F['seasonal']})"),
    ("research/questions/0014-bunds-between-the-paddies-aze.drawing.html", 19, rf"{FW}/farming-communities\.md carries the residue\.", "the backlog carried the residue (since closed)."),
    ("research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html", 3, rf"{FW}/towns\.md, \"the enclosed-fan tract floor\"", F["fan-floor"]),
    ("research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html", 20, rf"waits in {FW}/towns\.md, \"Enclosed-fan tract floor\"", f"waits in {F['fan-floor']}"),
    ("research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html", 20, rf"{FW}/farming-communities\.md, \"Seasonal maps\"", F["seasonal"]),
    ("research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html", 5, rf"{FW}/farming-communities\.md \"the copse", "the backlog's (since closed) \"the copse"),
    ("research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html", 25, rf"the {FW} note \"The belt and the copse share one crown vocabulary\" in {FW}/farming-communities\.md", "the backlog note \"The belt and the copse share one crown vocabulary\" (since closed)"),
    ("research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html", 3, rf"{FW}/farming-communities\.md \"Kashikawa", "the backlog's (since closed) \"Kashikawa"),
    ("research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html", 5, rf"{FW}/farming-communities\.md \"Kashikawa", "the backlog's (since closed) \"Kashikawa"),
    ("research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html", 3, rf"{FW}/farming-communities\.md F \"Woodland", "the backlog's (since closed) F \"Woodland"),
    ("research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.html", 5, rf"{FW}/farming-communities\.md F \"Woodland", "the backlog's (since closed) F \"Woodland"),
    ("research/questions/0121-town-plans-the-street-town-gaison-the-planned-grid-and-the-castle-town.drawing.html", 16, rf"<!-- {FW}/towns\.md, \"the T plan and the crank at a town's ends\" -->", "<!-- the backlog's \"the T plan and the crank at a town's ends\" (since closed; git history) -->"),
    ("research/questions/0136-town-streets-side-lanes-and-back-alleys-roji.drawing.html", 31, rf"the work is {FW}/towns\.md, \"the T plan and the crank at a town's ends\"", "the work was the backlog's \"the T plan and the crank at a town's ends\" (since closed; git history)"),
    ("research/questions/0181-how-big-a-citys-wall-is-for-its-population-and-how-many-live-outside-it.drawing.html", 51, rf"logged in {FW}/cross-cutting\.md \(item 2\)", f"filed as {F['fabric']}"),
    ("scripts/hooks/pair-hooks.sh", 588, rf"What remains goes to {FW}, or to the GM", "What remains is filed as a feature (make claim), or goes to the GM"),
    ("tests/hamletgen/ways/test_joints.py", 181, rf"recorded in {FW}\)", "recorded in the backlog, since closed)"),
    ("tests/hamletgen/ways/test_law.py", 297, rf"\({FW}: Inashiro", "(the backlog, since closed: Inashiro"),
    ("tests/hamletgen/ways/test_settle.py", 529, rf"\({FW} 2c\)", "(the backlog's 2c, since closed)"),
    ("tests/labels/test_caption_paths.py", 6, rf"\(`{FW}/cities\.md`\)", "(`specs/332-town-city-capital-tiers-hand-seated/`)"),
    ("tests/settlement/test_wet_ground.py", 259, rf"the {FW} entry's", "the backlog entry's"),
]


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    by_file: dict[str, list[tuple[int, str, str]]] = {}
    for f, n, rx, new in RULES:
        by_file.setdefault(f, []).append((n, rx, new))
    misses = 0
    for f, rules in by_file.items():
        p = ROOT / f
        lines = p.read_text().split("\n")
        for n, rx, new in rules:
            line = lines[n - 1]
            out, k = re.subn(rx, new.replace("\\", "\\\\"), line, count=1)
            if not k:
                print(f"MISS {f}:{n}: {rx[:70]}")
                misses += 1
                continue
            lines[n - 1] = out
        if not dry:
            p.write_text("\n".join(lines))
    print(f"{len(RULES) - misses} re-aimed, {misses} missed")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
