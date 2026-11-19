"""The hand sheet's held cases (feature 449 T151): small sheets drawn to reach every branch of the reader, the classification and the
seating, each placed by the Python's `hand_sheet.placed` (or its refusal), written for the Rust's unit test.

KEPT AS THE RECORD OF HOW THE HELD ANSWERS WERE TAKEN (feature 449 T151): `held.json` beside this file is the Python's answers,
written by this script from the tree's `l7r/diagram/labels/`, and the Rust hand sheet's unit test reads it. This script goes when
step 3b deletes that Python; the answers stay as the record.

    python3 -I rust/mode_a/src/labels/hand_sheet/held_cases.py rust/mode_a/src/labels/hand_sheet/held.json

Feature 449 T188 added eight sheets after the refusals (a one-text caption stranded, a sheet binding SVG to a prefix alone, a garden
named on its hall, beside it, or on its hall's surface, a turned rectangle drawn as a polygon, a disc in a turned group and a scatter of
kites named level, and a garden named beside on a road) and, after the plan review's round 3, a ninth: a turned ellipse of unequal
radii named at its angle beside one of equal radii named level, and a circle scaled unequally named at its angle beside one drawn round and re-took every answer from its fixed Python.
Feature 449 T189 added a tenth: a turned garden holding its lantern, a lone turned hall with its privy and a turned L-shaped house, named
beside at their angle off their turned edge, and an L-shaped kura named inside at its angle, and re-took every answer from its fixed Python.
Feature 449 T191 added an eleventh: a lone turned L-shaped house hemmed by sheds, its caption led out past twice the gap, its leader
scored and drawn to the house itself, and re-took every answer from its fixed Python.
Feature 449 T192 added a twelfth: a lone well, two striking posts, a weapon rack of three rails and a moored barge, each penned by dark
sheds with a gap below, their captions led out past twice the gap, each leader scored and drawn to the drawn ink - a disc's curve, not
its box, and several parts' own ink, not their box - and re-took every answer from its fixed Python.
Feature 449 T193 added a thirteenth: a 9 px wall with its cap unsaid and one square-capped on its group, each penned with a gap beyond its
east end, and a house outlined in a 4 px stroke penned with a gap below, their captions led out past twice the gap, each leader scored and
drawn to the ink as the sheet draws it - a stroke's flat or square end, an outline drawn out by its stroke - and re-took every answer from
its fixed Python.
Feature 449 T194 added a fourteenth: a rope ring drawn in two dashed arcs, a well's roof drawn as a dashed square whose `Z` draws its upper
side, and two raked lines, each a quadratic curve, in one path of two subpaths under a group's `fill="none"`, each penned with a gap
below, their captions led out past twice the gap, each leader scored and drawn to the ink as the sheet draws it - the ring's curve, not a
line doubled back between its arcs' end points, the upper side the `Z` draws, the curves, not a box read round a path with no fill of its own -
and re-took every answer from its fixed Python; and a fifteenth: a wall dashed 20 on and 20 off from 10 px into its pattern, its east end in a gap, a 9 px
wall bent to a 60 degree V pointing down at its opening, and a 6 px dot of no length ending flat, each penned with a gap below, each
leader scored and drawn to the ink as the sheet draws it - a dash's end, not the gap; the V's mitered point; the dot's place, which a
butt dot draws nothing at - and re-took every answer from its fixed Python.
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
    '  <rect x="160" y="40" width="60" height="50" fill="#E8D2A8" data-kind="stores" data-id="s1"/>\n  <rect x="160" y="95" width="30" height="20" fill="#E8D2A8" data-kind="stores" data-id="s2"/>\n',
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

# feature 449 T184: a caption of two texts on a field of stones where no seat is free goes back to its declared lines, where it had kept
# a cheaper wrap (0242: "if nothing clears, it goes back to one line")
STRANDED = sheet(
    '  <g data-kind="stones">' + "".join(f'<circle cx="{x}" cy="{y}" r="2" fill="#7A7A7A"/>' for x in range(4, 200, 24) for y in range(4, 150, 24)) + '</g>\n',
    '  <g data-kind="hut"><rect x="80" y="60" width="40" height="30" fill="#C9A57A"/><text x="100" y="75" font-size="12">old hut of the ferry keeper</text>'
    '<text x="100" y="85" font-size="8" data-cont="1">and his three sons</text></g>\n',
    head='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0,0 200 150">\n',
    back='  <rect x="0" y="0" width="200" height="150" fill="#EFE3C2" data-kind="-"/>\n',
)

# feature 449 T184: a caption beside a feature turned a quarter turn is level (0242), where it stood on end at the outline's 90 degrees
QUARTER = sheet(
    '  <g data-kind="shrine" transform="rotate(90 200 150)"><rect x="190" y="144" width="20" height="12" fill="#C9A57A"/><text x="200" y="150" font-size="8">wayside shrine</text></g>\n',
)

# feature 449 T188: a one-text caption on a field of stones where no seat is free goes back to one line (0242), where it kept a wrap
ONE_LINE = sheet(
    '  <g data-kind="stones">' + "".join(f'<circle cx="{x}" cy="{y}" r="2" fill="#7A7A7A"/>' for x in range(4, 200, 24) for y in range(4, 150, 24)) + '</g>\n',
    '  <g data-kind="hut"><rect x="80" y="60" width="40" height="30" fill="#C9A57A"/><text x="100" y="75" font-size="10">old hut of the ferry keeper</text></g>\n',
    head='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0,0 200 150">\n',
    back='  <rect x="0" y="0" width="200" height="150" fill="#EFE3C2" data-kind="-"/>\n',
)

# feature 449 T188: a sheet binding SVG to a prefix alone - its captions, their lines and their leaders written under the prefix, where a
# plain `<text>` fell into no namespace
PREFIXED = (
    '<s:svg xmlns:s="http://www.w3.org/2000/svg" viewBox="0 0 400 300">\n  <s:rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>\n'
    '  <s:rect x="0" y="0" width="170" height="300" fill="#2D2A24" data-kind="-"/><s:rect x="230" y="0" width="170" height="300" fill="#2D2A24" data-kind="-"/>\n'
    '  <s:g data-kind="hut"><s:rect x="185" y="140" width="30" height="20" fill="#C9A57A"/><s:text x="200" y="150" font-size="8">old hut of the ferry keeper</s:text></s:g>\n'
    '  <s:g data-kind="well"><s:circle cx="150" cy="60" r="4" fill="#5C7A8C"/><s:text x="150" y="60" font-size="7">well</s:text>'
    '<s:text x="150" y="68" font-size="6" data-cont="1">dug 1102</s:text></s:g>\n</s:svg>\n'
)

# feature 449 T188: a garden whose every inside seat covers the hall in it is named beside the garden where a seat there is free (0242: a
# building "is never covered while any other choice exists"), and keeps its ground where none is, or where it lies on the hall's roof
# marked as surface, light ink
def ground(x, y, w, h, surface=""):
    return sheet(
        f'  <g data-kind="garden"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#BFD0A0"/><rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{h - 4}" fill="#C9A57A"{surface}/>'
        '<text x="200" y="150" font-size="10">inner garden</text></g>\n'
    )


# feature 449 T188 (the plan review): a rectangle turned 30 degrees and drawn as a polygon, to a tenth of a pixel, is named inside it at
# its own angle, as the same <rect> is; a closing point repeating its first changes nothing
TURNED_OUTLINE = sheet(
    '  <g data-kind="granary"><polygon points="175.4,112.7 244.6,152.7 224.6,187.3 155.4,147.3" fill="#C9A57A"/><text x="200" y="150" font-size="8">granary</text></g>\n',
    '  <g data-kind="shed"><polygon points="55.4,192.7 124.6,232.7 104.6,267.3 35.4,227.3 55.4,192.7" fill="#C9A57A"/><text x="80" y="230" font-size="8">shed</text></g>\n',
)


# the T188 claims round: a well (a disc) in a turned group, and a scatter of kites (four points, no rectangle), are named level; a road
# under the whole sheet leaves a garden's name a seat beside on the road alone, taken over the inside seat on its hall and the road
LEVEL_THINGS = sheet(
    '  <g data-kind="well" transform="rotate(30 100 100)"><circle cx="100" cy="100" r="6" fill="#5C7A8C"/><text x="100" y="100" font-size="7">well</text></g>\n',
    '  <g data-kind="cairns"><polygon points="250,200 270,205 270,215 247,210" fill="#7A7A7A"/><polygon points="290,200 310,205 310,215 287,210" fill="#7A7A7A"/>'
    '<text x="280" y="190" font-size="7">cairns</text></g>\n',
)
ROAD = ground(140, 110, 120, 80).replace('<g data-kind="garden">', '<line x1="0" y1="150" x2="400" y2="150" stroke="#B8A27A" stroke-width="800" data-kind="road"/><g data-kind="garden">', 1)

# the T188 plan review, round 3: an ellipse of unequal radii in a turned group has its axes turned with the group and is named at its
# angle; one of equal radii is a circle and stays level
TURNED_ELLIPSE = sheet(
    '  <g data-kind="pond" transform="rotate(30 120 150)"><ellipse cx="120" cy="150" rx="60" ry="25" fill="#9FBFD4"/><text x="120" y="150" font-size="8">pond</text></g>\n',
    '  <g data-kind="basin" transform="rotate(30 300 150)"><ellipse cx="300" cy="150" rx="30" ry="30" fill="#9FBFD4"/><text x="300" y="150" font-size="8">basin</text></g>\n',
    # a circle scaled unequally in a turned group is drawn as an ellipse and is named at the group's angle; one drawn round stays level
    '  <g data-kind="tub" transform="rotate(30 120 250) translate(120 250) scale(2,1)"><circle cx="0" cy="0" r="15" fill="#9FBFD4"/><text x="0" y="0" font-size="6">tub</text></g>\n',
    '  <g data-kind="drum" transform="rotate(30 300 250)"><circle cx="300" cy="250" r="20" fill="#9FBFD4"/><text x="300" y="250" font-size="8">drum</text></g>\n',
)

# feature 449 T189: a turned garden holding its lantern, a lone turned hall with its privy, and a turned L-shaped house drawn as one outline,
# each too long a name to stand inside, are named beside at their angle off their turned edge (0242: "seated off its turned edge", "not
# off an upright box around it"), where the garden and the hall were named level beside the upright box and the house level throughout;
# a second L-shaped house holds its short name inside at its angle
TURNED_BESIDE = sheet(
    '  <g data-kind="garden" transform="rotate(30 90 70)"><rect x="60" y="55" width="60" height="30" fill="#BFD0A0"/><rect x="86" y="66" width="6" height="6" fill="#7A7A7A"/>'
    '<text x="90" y="70" font-size="8">garden of the moon-viewing lantern</text></g>\n',
    '  <g data-kind="hall" transform="rotate(30 300 70)"><rect x="275" y="50" width="50" height="40" fill="#C9A57A"/><rect x="329" y="94" width="6" height="6" fill="#C9A57A"/>'
    '<text x="300" y="70" font-size="10">great hall of the ancestral spirits</text></g>\n',
    '  <g data-kind="house" transform="rotate(30 90 210)"><polygon points="60,190 120,190 120,205 80,205 80,230 60,230" fill="#C9A57A"/>'
    '<text x="90" y="210" font-size="8">house of the river warden</text></g>\n',
    '  <g data-kind="kura" transform="rotate(30 300 210)"><polygon points="250,180 350,180 350,210 290,210 290,240 250,240 250,180" fill="#D9C28E"/>'
    '<text x="300" y="200" font-size="7">kura</text></g>\n',
)


# feature 449 T191: a lone L-shaped house turned 30 degrees, hemmed by sheds with a privy at its notch, its caption led out past twice the
# gap: its leader is scored to the house itself, so a standard seat below, on one line, is free - scored to its turned box's corner over
# the empty notch, along the privy's edge, that seat's leader cost an obstacle, and the caption took a two-line seat of the fallback search
LED_L = sheet(
    '  <g data-kind="sheds" transform="rotate(30 200 150)"><rect x="163" y="113" width="74" height="20" fill="#2D2A24"/>'
    '<rect x="163" y="162" width="24" height="20" fill="#2D2A24"/><rect x="163" y="133" width="20" height="29" fill="#2D2A24"/>'
    '<rect x="217" y="133" width="20" height="15" fill="#2D2A24"/><rect x="215" y="160" width="12" height="12" fill="#2D2A24"/></g>\n',
    '  <g data-kind="house" transform="rotate(30 200 150)"><polygon points="185,135 215,135 215,145 195,145 195,160 185,160" fill="#DDB87A"/>'
    '<text x="200" y="150" font-size="8">ferry house</text></g>\n',
)


# feature 449 T192: a lone well, two striking posts, a weapon rack of three rails and a moored barge, each penned by dark sheds with a gap
# below, their captions led out past twice the gap: each leader is scored and drawn to the drawn ink - the well's curve, where it was scored
# to the well's box and its seat below, led to the box's corner across the shed, was passed over; the parts' own ink, where they were
# scored to their box and drawn to the ink
def pen(x, y, w, h):
    # dark sheds 6 px thick round a w x h yard at (x, y), 4 px off it, with a 10 px gap in the middle of the lower side
    x0, y0, x1, y1 = x - 10, y - 10, x + w + 4, y + h + 4
    mid = x + w / 2
    return (f'<rect x="{x0}" y="{y0}" width="{x1 - x0 + 6}" height="6" fill="#2D2A24"/><rect x="{x0}" y="{y0 + 6}" width="6" height="{y1 - y0}" fill="#2D2A24"/>'
            f'<rect x="{x1}" y="{y0 + 6}" width="6" height="{y1 - y0}" fill="#2D2A24"/><rect x="{x0}" y="{y1}" width="{mid - 5 - x0}" height="6" fill="#2D2A24"/>'
            f'<rect x="{mid + 5}" y="{y1}" width="{x1 + 6 - mid - 5}" height="6" fill="#2D2A24"/>')


LED_PARTS = sheet(
    '  <g data-kind="sheds">' + pen(46, 46, 18, 18) + pen(242, 42, 26, 23) + pen(40, 180, 40, 28) + pen(236, 185, 36, 25) + '</g>\n',
    '  <g data-kind="well"><circle cx="55" cy="55" r="9" fill="#5C7A8C"/><text x="55" y="55" font-size="8">well of the old shrine</text></g>\n',
    '  <g data-kind="striking posts"><circle cx="245" cy="45" r="3" fill="#6B5A3A"/><circle cx="265" cy="62" r="3" fill="#6B5A3A"/><text x="255" y="55" font-size="8">striking posts</text></g>\n',
    '  <g data-kind="weapon rack"><rect x="40" y="180" width="24" height="4" fill="#6B5A3A"/><rect x="40" y="192" width="24" height="4" fill="#6B5A3A"/>'
    '<rect x="56" y="204" width="24" height="4" fill="#6B5A3A"/><text x="55" y="195" font-size="8">weapon rack</text></g>\n',
    '  <g data-kind="barge"><rect x="236" y="185" width="22" height="9" fill="#8C6F3E"/><line x1="258" y1="190" x2="272" y2="210" stroke="#4A3318" stroke-width="1.5"/>'
    '<text x="255" y="195" font-size="8">tax barge of the river</text></g>\n',
)


# feature 449 T193: a 9 px wall with its cap unsaid (SVG's butt) and one square-capped on its group, each penned by dark sheds with a gap
# beyond its east end, and a house outlined in a 4 px stroke penned with a gap below, their captions led out past twice the gap: each
# leader is scored and drawn to the ink as the sheet draws it - the wall's flat or square end, where a round cap was read past either,
# and the house's outline drawn out by its stroke, where it ended on the bare outline inside the stroke
def pen_east(x, y, w, h):
    # dark sheds 6 px thick round a w x h yard at (x, y), 4 px off it, with a 10 px gap in the middle of the east side
    x0, y0, x1, y1 = x - 10, y - 10, x + w + 4, y + h + 4
    mid = y + h / 2
    return (f'<rect x="{x0}" y="{y0}" width="{x1 - x0 + 6}" height="6" fill="#2D2A24"/><rect x="{x0}" y="{y1}" width="{x1 - x0 + 6}" height="6" fill="#2D2A24"/>'
            f'<rect x="{x0}" y="{y0 + 6}" width="6" height="{y1 - y0 - 6}" fill="#2D2A24"/><rect x="{x1}" y="{y0 + 6}" width="6" height="{mid - 5 - y0 - 6}" fill="#2D2A24"/>'
            f'<rect x="{x1}" y="{mid + 5}" width="6" height="{y1 - mid - 5}" fill="#2D2A24"/>')


LED_CAPS = sheet(
    '  <g data-kind="sheds">' + pen_east(40, 40, 40, 20) + pen_east(40, 140, 40, 20) + pen(240, 40, 24, 16) + '</g>\n',
    '  <g data-kind="fox wall" stroke="#4A3318" stroke-width="9"><line x1="40" y1="50" x2="80" y2="50"/><text x="60" y="50" font-size="8" stroke="none">fox wall</text></g>\n',
    '  <g data-kind="east wall" stroke="#4A3318" stroke-width="9" stroke-linecap="square"><line x1="40" y1="150" x2="76" y2="150"/>'
    '<text x="60" y="150" font-size="8" stroke="none">east wall</text></g>\n',
    '  <g data-kind="kura"><rect x="240" y="40" width="24" height="16" fill="#DDB87A" stroke="#5A3F1E" stroke-width="4"/><text x="252" y="50" font-size="8">old kura of the toll</text></g>\n',
)


# feature 449 T194: a rope ring drawn in two dashed arcs, a well's roof drawn as a dashed square whose `Z` draws its upper side, and two raked
# lines, two quadratic curves in one path of two subpaths under a group's `fill="none"`, each penned by dark sheds with a gap below, their
# captions led out past twice the gap: each leader is scored and drawn to the ink as the sheet draws it - the ring's curve, where the reader
# kept a 10 px line doubled back; the upper side, which the reader left undrawn; the curves, where it read a box round the path
LED_CURVES = sheet(
    '  <g data-kind="sheds">' + pen(46, 46, 18, 18) + pen(242, 42, 26, 23) + pen(40, 180, 40, 28) + '</g>\n',
    '  <g data-kind="sacred rope"><path d="M 50 55 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0" fill="none" stroke="#4A3318" stroke-width="2" stroke-dasharray="2 1.5"/>'
    '<text x="55" y="55" font-size="8">rope of the old tree</text></g>\n',
    '  <g data-kind="well"><path d="M 244 43 v 20 h 22 v -20 z" fill="none" stroke="#6B5836" stroke-width="1.1" stroke-dasharray="3 2"/>'
    '<text x="255" y="55" font-size="8">well of the toll house</text></g>\n',
    '  <g data-kind="raked gravel" stroke="#4A3318" stroke-width="1.4" fill="none"><path d="M 42 190 q 18 -8 36 0 M 42 204 q 18 -8 36 0"/>'
    '<text x="60" y="195" font-size="8" fill="#2D2A24" stroke="none">raked gravel of the court</text></g>\n',
)


# feature 449 T194: a wall dashed 20 on and 20 off from 10 px into its pattern, its east end in a gap, a 9 px wall bent to a 60 degree V pointing down at its
# opening (SVG's default miter, 9 px past the corner), and a 6 px dot of no length ending flat, each penned by dark sheds with a gap below,
# their captions led out past twice the gap: the reader drew no dash, measured the V's corner round and drew the dot as a disc
LED_STROKES = sheet(
    '  <g data-kind="sheds">' + pen(40, 40, 60, 24) + pen(240, 40, 36, 40) + pen(52, 180, 16, 16) + '</g>\n',
    '  <g data-kind="dashed fence" stroke="#4A3318" stroke-width="6" stroke-dasharray="20 20" stroke-dashoffset="10"><line x1="40" y1="52" x2="100" y2="52"/>'
    '<text x="70" y="52" font-size="8" stroke="none">fence of the old toll</text></g>\n',
    '  <g data-kind="bent wall" stroke="#4A3318" stroke-width="9" fill="none"><polyline points="240,44 258,75.18 276,44"/>'
    '<text x="258" y="60" font-size="8" stroke="none">wall of the shrine yard</text></g>\n',
    '  <g data-kind="post" stroke="#4A3318" stroke-width="6"><line x1="60" y1="188" x2="60" y2="188"/>'
    '<text x="60" y="188" font-size="8" stroke="none">post of the gate</text></g>\n',
)


REFUSALS = [
    sheet('<g data-kind="x"><text x="5" y="5" font-size="6">lonely</text></g>\n'),
    sheet('<g data-kind="tub"><circle cx="50" cy="50" r="5"/><text x="80" y="80" font-size="6">tub</text></g>\n', back='<_x/>' + BACK),
    # feature 449 T182: an element an internal entity expands to has no start tag in the source: refused by name
    sheet(
        '<g data-kind="tub"><circle cx="50" cy="50" r="5"/><text x="80" y="80" font-size="6">tub</text></g>\n',
        head='<!DOCTYPE svg [<!ENTITY e "<rect x=\'1\' y=\'1\' width=\'1\' height=\'1\'/>">]>' + HEAD,
        back='&e;' + BACK,
    ),
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
out = [run(s) for s in [EVERYTHING, STEPPED, SCATTER, STRANDED, QUARTER, *REFUSALS, ONE_LINE, PREFIXED, ground(140, 110, 120, 80), ground(1, 1, 398, 298), ground(140, 110, 120, 80, ' data-texture="1"'), TURNED_OUTLINE, LEVEL_THINGS, ROAD, TURNED_ELLIPSE, TURNED_BESIDE, LED_L, LED_PARTS, LED_CAPS, LED_CURVES, LED_STROKES]]
for o in out:
    print(o.get("raises", "placed %d" % len(o.get("placed", ""))), file=sys.stderr)
json.dump(out, open(sys.argv[1], "w"), indent=0)
