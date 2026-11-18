"""The hand sheet's held cases (feature 449 T151): small sheets drawn to reach every branch of the reader, the classification and the
seating, each placed by the Python's `hand_sheet.placed` (or its refusal), written for the Rust's unit test.

KEPT AS THE RECORD OF HOW THE HELD ANSWERS WERE TAKEN (feature 449 T151): `held.json` beside this file is the Python's answers,
written by this script from the tree's `l7r/diagram/labels/`, and the Rust hand sheet's unit test reads it. This script goes when
step 3b deletes that Python; the answers stay as the record.

    python3 -I rust/mode_a/src/labels/hand_sheet/held_cases.py rust/mode_a/src/labels/hand_sheet/held.json
"""
import json, sys, traceback
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[5]))  # the tree: <tree>/rust/mode_a/src/labels/<unit>/
from l7r.diagram.labels import hand_sheet as H

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0,0 400 300">\n'
BACK = '  <rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'

def sheet(*body, head=HEAD, back=BACK):
    return head + back + "".join(body) + "</svg>\n"

EVERYTHING = sheet(
    '  <text x="200" y="14" font-size="12">Plan of everything</text>\n',
    '  <path d="M 0 150 L 60 150 H 90 V 160 C 100 160 110 150 120 150 S 140 140 150 140 Q 160 140 170 145 T 190 150 A 5 5 0 0 1 200 150 l 10 0 h 5 v 2 c 1 1 2 2 3 3 s 1 1 2 2 q 1 1 2 2 t 1 1 a 2 2 0 0 0 4 0 z" fill="none" stroke="#B8A27A" stroke-width="20" data-kind="road"/>\n',
    '  <polygon points="380,0 400,0 400,300 380,300" fill="#8FB0C6" data-kind="river"/>\n',
    '  <polyline points="370,0 370,300" fill="none" stroke="#6B5A3A" stroke-width="3" data-kind="revetment"/>\n',
    '  <rect x="20" y="180" width="120" height="100" fill="#D9C28E" data-kind="outer court" data-id="oc"/>\n',
    '  <rect x="30" y="190" width="40" height="30" fill="#BFD0A0" stroke="#7A8C5C" stroke-width="2" data-kind="garden"/>\n',
    '  <rect x="80" y="230" width="50" height="40" fill="url(#vegetable-rows)" data-kind="vegetable garden"/>\n',
    '  <rect x="150" y="180" width="80" height="60" fill="#C8B488" data-kind="practice ground" data-id="pg"/>\n',
    '  <text x="80" y="200" font-size="9" data-kind="outer court" data-names="oc">OUTER COURT</text>\n',
    '  <text x="190" y="210" font-size="8" data-kind="practice ground" data-names="pg">practice ground</text>\n',
    '  <g data-kind="residence" transform="translate(240,40)">\n'
    '    <rect x="0" y="0" width="80" height="40" fill="#DDB87A" stroke="#5A3F1E" stroke-width="1.5"/>\n'
    '    <rect x="40" y="40" width="50" height="40" fill="#DDB87A"/>\n'
    '    <line x1="40" y1="0" x2="40" y2="40" stroke="#2D2A24" stroke-width="1"/>\n'
    '    <text x="40" y="25" font-size="12" font-weight="bold" letter-spacing="1" fill="#F4EBD0">RESIDENCE</text>\n'
    '    <text x="40" y="36" font-size="7" font-style="italic" data-cont="1" data-kind="residence">lord and household</text>\n'
    '  </g>\n',
    '  <g data-kind="tubs"><circle cx="40" cy="40" r="4" fill="#5C7A8C"/><circle cx="200" cy="120" r="4" fill="#5C7A8C"/><circle cx="330" cy="200" r="4" fill="#5C7A8C"/><text x="200" y="100" font-size="7">tubs</text></g>\n',
    '  <g data-kind="kura" transform="rotate(30 100 100)"><rect x="80" y="80" width="40" height="30" fill="#2D2A24"/><text x="100" y="98" font-size="8" fill="#F4EBD0">kura</text></g>\n',
    '  <g data-kind="gatehouse" transform="matrix(1 0 0 1 150 250) scale(1.5) scale(1 1) skewX(10)"><rect x="0" y="0" width="30" height="16" fill="#C9A57A" data-texture="1"/><text x="15" y="11" font-size="6" text-anchor="middle">gate</text></g>\n',
    '  <g data-kind="pines"><ellipse cx="350" cy="250" rx="6" ry="4" fill="#4A6B3A"/><ellipse cx="358" cy="262" rx="6" ry="4" fill="#4A6B3A"/><text x="340" y="240" font-size="7" text-anchor="end">old <tspan>pines</tspan></text></g>\n',
    '  <g data-kind="river band"><rect x="300" y="100" width="12" height="120" fill="#9FBFD4"/><text x="306" y="160" font-size="7">river band</text></g>\n',
    '  <g data-kind="barge"><line x1="250" y1="160" x2="290" y2="160" stroke="#4A3318" stroke-width="1.5"/><rect x="255" y="150" width="20" height="8" fill="#8C6F3E"/><text x="260" y="140" font-size="7">tax barge</text></g>\n',
    '  <line x1="0" y1="170" x2="240" y2="170" stroke="#2D2A24" stroke-width="6" data-kind="wall"/>\n',
    '  <path d="M 10 10 L 30 10 L 30 30" fill="none" stroke="#2D2A24" stroke-width="1" data-kind="lane mark" data-leader="1"/>\n',
    '  <x:note xmlns:x="urn:example"><x:rect x="1" y="1" width="2" height="2"/></x:note>\n',
    '  <rect x="160" y="40" width="60" height="50" fill="#E8D2A8" data-kind="stores" data-id="s1"/>\n'
    '  <rect x="160" y="95" width="30" height="20" fill="#E8D2A8" data-kind="stores" data-id="s2"/>\n',
    '  <text x="190" y="70" font-size="7" data-kind="stores" data-names="s1 s2">stores</text>\n',
    '  <text x="190" y="80" font-size="7" data-kind="stores" data-names="s2">second store</text>\n',
    '  <text x="10" y="295" font-size="6" data-kind="-">scale 1:100</text>\n',
    '  <text x="5" y="5" font-size="6" data-kind="note"></text>\n',
)

STEPPED = sheet(
    '  <g data-kind="hall"><rect x="100" y="100" width="80" height="40" fill="#DDB87A"/><rect x="150" y="140" width="60" height="50" fill="#DDB87A"/><text x="140" y="125" font-size="9">HALL</text></g>\n',
    '  <g data-kind="shed"><rect x="250" y="100" width="40" height="40" fill="#C9A57A"/><rect x="250" y="140" width="40" height="38" fill="#C9A57A"/><text x="270" y="120" font-size="7">shed</text></g>\n',
    '  <g data-kind="garden"><rect x="40" y="200" width="120" height="80" fill="#BFD0A0"/><circle cx="60" cy="220" r="3" fill="#7A7A7A"/><text x="100" y="240" font-size="9">garden</text></g>\n',
    '  <g data-kind="well"><circle cx="300" cy="250" r="12" fill="#2D2A24"/><text x="300" y="254" font-size="7">well</text></g>\n',
    '  <g data-kind="crowded"><rect x="10" y="10" width="380" height="60" fill="#2D2A24"/><text x="200" y="40" font-size="40">A VERY LONG NAME THAT FITS NOWHERE AT ALL</text></g>\n',
)

def run(svg):
    try:
        return {"svg": svg, "placed": H.placed(svg)}
    except Exception as e:
        return {"svg": svg, "raises": traceback.format_exception_only(type(e), e)[-1].rstrip("\n")}

SCATTER = sheet(
    '  <g data-kind="cairns"><polygon points="50,50 60,50 55,40" fill="#7A7A7A"/><polygon points="80,60 90,60 85,50" fill="#7A7A7A"/><text x="70" y="80" font-size="7">cairns</text></g>\n',
)

REFUSALS = [
    sheet('<g data-kind="x"><text x="5" y="5" font-size="6">lonely</text></g>\n'),
    sheet('<g data-kind="tub"><circle cx="50" cy="50" r="5"/><text x="80" y="80" font-size="6">tub</text></g>\n', back='<_x/>' + BACK),
    sheet('<g data-kind="tub" xmlns:s="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="5"/><s:text x="80" y="80" font-size="6">tub</s:text></g>\n'),
    sheet('  <text x="5" y="5" font-size="6" data-kind="x" data-cont="1">orphan</text>\n'),
    sheet('  <text x="5" y="5" font-size="6" data-kind="x" data-names="nowhere">named</text>\n'),
    sheet('  <g data-kind="x"><text x="5" y="5" font-size="6" data-kind="x">self</text></g>\n'),
    sheet('<rect/>', head='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400">\n'),
    sheet('<rect/>', head='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 a 1">\n'),
    sheet('  <g transform="translate()"><rect width="1" height="1"/></g>\n'),
    sheet('  <g transform="rotate(x)"><rect width="1" height="1"/></g>\n'),
    "<svg",
]
out = [run(s) for s in [EVERYTHING, STEPPED, SCATTER, *REFUSALS]]
for o in out:
    print(o.get("raises", "placed %d" % len(o.get("placed", ""))), file=sys.stderr)
json.dump(out, open(sys.argv[1], "w"), indent=0)
