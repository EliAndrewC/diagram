"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

import math

# THE ORDER IS A CONTRACT, AND THIS IMPORT IS WHAT HOLDS IT. `s` comes from the part IMMEDIATELY
# ABOVE this one, not from `frame`, so Python cannot execute this part until that one has
# finished drawing. The first cut of this split had every part import from `frame`, which
# constrained only that `frame` ran first - and `ruff`'s isort then sorted the list in
# `__init__.py` ALPHABETICALLY, so `fields` (which calls `s.finish()`) ran fourth of seven and
# the wharf, the yashiki band and the trade works drew into a map already written to disk.
# Caught by settlement-review, 2026-08-31; invisible to the gate, which rolls no wip map.
from .frame import CX, CY, MOAT, NRING, RX, RY, s

# ---- THE CASTLE. North of center so the ceremonial approach has room to run south to the gate;
# ote-mon SOUTH, per the jokamachi rule that the main road passes the castle's front. Blank inside.
# the caption is "Shiro Daika" PLAIN: shiro already means castle, so "Shiro Daika Castle" reads
# "Castle Daika Castle" - the Mount-Fujiyama construction Constitution XI exists to catch. Town
# and castle sharing the name is the jokamachi reality (settlement-review, 2026-08-09).
# TWO GATES (GM 2026-08-09, researched): the ote-mon fronts south onto the ceremonial
# approach; the karamete-mon - the rear gate every castle kept, the sortie gate - opens north,
# its approach road bridging the castle's own moat to join the Imperial road's run to the
# city's north gate. research/cities/capitals.md, "A castle has TWO gates".
s.castle(
    1400, 880, 850, 700, label="Shiro Daika", gate_dir="south", karamete_dir="north"
)  # the castle keeps ITS axis (x=1400) - the resized wall re-centered SW, and the honmaru sits NE-of-center (the castle-at-the-back pattern); everything castle-anchored (ote-suji, ministries, karamete) reads from this axis, not from CX

# ---- the moat CIRCULATES river-to-river, every drawn drop moving NE -> SW (GM 2026-08-09,
# third cut - the second still ran its last leg up-screen). Like Minami and Nagahara the moat
# now connects to the river at BOTH ends; their moat feet touch the bank directly, this
# stand-off ring reaches it through two moat-width (66 ft, Tango's gauge) sluiced leats:
#   - the FEEDER taps the river's upper reach (downstream of the aqueduct's intake) and runs
#     monotonically down-map to the ring's east arc - every segment moves west and south, the
#     declared water_flow=135 bearing;
#   - the DRAIN leaves the ring's southeast arc and rejoins the river just below its bend,
#     approaching swept DOWNSTREAM, and the river there is genuinely lower ground than the arc.
# The towpath crosses the drain's mouth on a plank deck - a real towpath bridged every side
# drain it met, or the haulage teams could not pass.
FEED_TAP = (3080, 862)  # the river's west bank - upstream of the city, downstream of the aqueduct intake
s.stream([FEED_TAP, (2870, 875), (2650, 880), (MOAT[4][0], MOAT[4][1])], frm={"kind": "river"}, to={"kind": "moat"}, width=s.px(66))
# the boards sit a few steps DOWN their channel runs, not at the junctions (GM 2026-08-09: at a
# junction the local water direction is ambiguous, so the correctly-across board read as a
# coincidentally axis-aligned bar; astride the clear run, across-the-channel explains itself)
s.sluice_gate(
    3051, 863.8, rot=math.degrees(math.atan2(875 - FEED_TAP[1], 2870 - FEED_TAP[0])) + 90, label="sluice gate", label_xy=(3040, 845), span=26
)  # the intake board - the frame spans BANK TO BANK (posts on the abutments, the operator walks the crossbeam)
DRAIN_OUT = (MOAT[8][0], MOAT[8][1])
s.stream([DRAIN_OUT, (2000, 2460), (2172, 2557)], frm={"kind": "moat"}, to={"kind": "river"}, width=s.px(66))
s.sluice_gate(
    2018, 2408, rot=math.degrees(math.atan2(2460 - DRAIN_OUT[1], 2000 - DRAIN_OUT[0])) + 90, label="sluice gate", label_xy=(1994, 2392), span=26
)  # ON the drain's centerline (the old seat predated the drain's re-route - GM 2026-08-10)  # the outfall board, bank to bank like the intake
s.moat_flow(MOAT[4], MOAT[8])

# ---- THE AQUEDUCT (feature 020; rebuilt to the researched josui form, GM 2026-08-09). What
# the research says a josui IS (research/cities/capitals.md, "How a josui actually ran"): an
# intake WEIR on the river peeling off at a SHALLOW DOWNSTREAM angle (Hamura's nagewatashi
# weir); an OPEN earth cut - open-topped, hence water-blue between spoil banks - falling
# gently and continuously (Tamagawa: 92 m over 43 km, never a climb); a terminus at the city
# gate's waterworks head (Yotsuya Okido), the settling tank on the moat's OUTER bank; and
# BURIED wooden mains (mokuhi) beyond it, feeding cistern-wells (josui-ido) the residents
# bucket from - feature 021's, with the wells. The first draft ran the cut up-screen around
# the whole northeast and crossed the moat on a flume; the corrected route peels off
# downstream and falls straight to the EAST gate - short and direct because the river is
# near, where the real ones wound only to HOLD their gradient across long country.
AQ = [(2962.4, 1047.9), (2790, 1130), (2660, 1215), (2554.4, 1294.2)]  # the duct, head to terminus
s.aqueduct(AQ)  # terminus pulled up its own line to land the settling basin CLEAR of the moat (it was IN the channel - GM 2026-08-10)


def _beside(a, b, off=17):
    """A seat `off` px to the UPHILL side of the duct at point `a`, derived from the duct's own
    bearing there (GM 2026-08-11: the end labels were pinned and drifted 195 and 348 ft from the
    points they name, with nothing but open ground between). Derived, so a re-routed duct carries
    its words with it instead of stranding them - and near enough that the label reads as naming
    the thing rather than floating beside it."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy) or 1.0
    return (a[0] - dy / ln * off, a[1] + dx / ln * off)


# the two ends carry the words the glyphs cannot (GM 2026-08-09): the river end is the INTAKE
# WEIR (the Hamura form - a barrier angled across part of the stream, shouldering water into
# the cut), and the gate end is the SETTLING BASIN, where silt drops before the buried mains
# All three aqueduct words share the duct's bearing and the same ~20px uphill offset from the
# channel line (GM 2026-08-09: the end labels were level while "aqueduct" lay along the cut).
_IW = _beside(AQ[0], AQ[1])
s.label(_IW[0], _IW[1], "intake weir", 9, italic=True, color="#5E7A8A", rot=151, linear=True, full_tilt=True)
# the terminus stands ON the moat's outer bank by design, so BOTH of its flanks are rampart ink -
# the caption goes back UP the duct instead, over the open ground the cut runs through
_SBd = math.hypot(AQ[-2][0] - AQ[-1][0], AQ[-2][1] - AQ[-1][1]) or 1.0
# 26 px back up the cut and 16 px off its uphill flank: the terminus stands ON the moat's outer
# bank, so both of its own flanks are rampart ink and the caption has to step back along the duct
# to find open ground. Derived from AQ, so a re-routed duct carries the words with it.
_SBu, _SBp = 26, 16
_SBx = AQ[-1][0] + (AQ[-2][0] - AQ[-1][0]) / _SBd * _SBu - (AQ[-2][1] - AQ[-1][1]) / _SBd * _SBp
_SBy = AQ[-1][1] + (AQ[-2][1] - AQ[-1][1]) / _SBd * _SBu + (AQ[-2][0] - AQ[-1][0]) / _SBd * _SBp
_SB = (_SBx, _SBy)
s.label(_SB[0], _SB[1], "settling basin", 9, italic=True, color="#5E7A8A", rot=-33, linear=True, full_tilt=True)  # beside the terminus, on the duct's uphill side
s.label(2705, 1160, "aqueduct", 10, italic=True, color="#5E7A8A", rot=151, linear=True, full_tilt=True)

# ---- THE TOWPATH (feature 020): on the wharf's own (west) bank, coming up from downstream -
# upstream haulage is the whole reason it exists - and ending at the wharf, no further.
# ...ending AT the quay by the downstream landing stage (GM 2026-08-09: the old end stopped
# short of the jetty and hugged the waterline, reading as a line that dissolves into the
# river), and LABELED - the haulage path cannot explain itself at fit zoom
s.towpath([(1877, 3109), (2221, 2400)])  # the CURRENT river's bank, offset w/2+6 landward (the old pts predated the re-route - GM 2026-08-10)
_TWL = (1877 + (2221 - 1877) * 0.72, 3109 + (2400 - 3109) * 0.72)  # DERIVED from the towpath itself, up toward the wharf it serves
s.label(_TWL[0], _TWL[1], "towpath", 10, italic=True, color="#8A7050", rot=-64, linear=True, full_tilt=True)
s.bridge(2000.2, 2459.3, -32.5, 49, 4)  # the wharf shore path's plank over the moat drain (GM 2026-08-10: no way stands in water without a deck)
s.M["bridges"][-1]["foot"] = True
s.bridge(
    2150.9, 2545.1, -64.1, 28, 4
)  # the towpath's plank AT the computed towpath x drain crossing (the drain's river-to-river re-route moved the ford and the deck kept its old seat - review 2026-08-10); oblique span 22px water / sin(84 deg) + 6px bank rests
s.M["bridges"][-1]["foot"] = True  # a footplank on the haulage path, not a road deck

# ---- carry every way over the water it crosses. AFTER all roads and water, as bridges() requires:
# the south/east/southwest/north gates' moat crossings, the east road over the RIVER, and the
# ote-suji over the castle's own moat all take decks from the one shared source (feature 020).
s.bridges()

# ---- THE GOVERNMENT WARD (feature 020): the six domain ministries flanking the ote-suji in two
# files of three, the House Chancellery and the domain school continuing the same axis south of
# the kagi-no-te bend. Both anchor traditions converge on exactly this form - Beijing's Six
# Ministries lined the Corridor of a Thousand Steps outside Chengtianmen, and a jokamachi's
# offices spilled out of the ninomaru into the town (settlements/capitals.md, "The government
# ward"). Default ministry compound: 224x148 ft, the researched provincial size - a domain
# ministry is the same bureau of clerks and archives at a bigger desk.
# the files sit a ~21 ft setback off the avenue's edge - corridor frontage, not detached
# blocks; captions ON the glyphs (the estate rule applied to state offices, GM 2026-08-09 -
# a provincial city's smaller compounds keep theirs beside)
for i, nm in enumerate(("Rites", "Revenue", "Retainers")):
    s.ministry(1348, 1330 + 85 * i, f"Ministry of {nm}", label_inside=True)
for i, nm in enumerate(("War", "Works", "Justice")):
    s.ministry(1452, 1330 + 85 * i, f"Ministry of {nm}", label_inside=True)
# NO House Chancellery compound (GM 2026-08-09, researched): the council of lineage
# representatives meets IN the castle - Edo's Hyojosho and Roju sat within Edo castle, China's
# Grand Secretariat inside the palace. Executive ministries out, the ruler's council in; the
# chamber is part of the castle's implied goten. The DOMAIN SCHOOL is the hanko - a school of
# letters with a martial wing - so it takes the martial-hall vocabulary, not a ministry box.
s.hanko(1482, 1658)  # ~1 ha compound (size audit 2026-08-09) - shifted east so its wall clears the road

# ---- THE IMPERIAL MAGISTRATE'S COMPOUND (feature 020): FOREIGN SOVEREIGN GROUND - ~56 staff plus
# family, funded at 700 koku/yr for "manor maintenance, grounds, stable, fortified walls,
# ceremonial halls" (budgets.md). The manor form in its OWN ink, deep jade against the ministries'
# state violet, so it reads as not-of-the-domain; gate west, facing the government ward it works
# beside.
# captioned as the INSTITUTION, not the officeholder (settlement-review 2026-08-09; Ubame's
# sibling is "Magistrate's Manor" and capitals.md says "the Imperial Magistrate's compound")
# "Imperial Magistracy" - the institution, shortened so the caption fits INSIDE the court
s.manor(1720, 1445, 100, 75, "Imperial Magistracy", gate_dir="west", ink="#274D3D", label_inside=True)


# ---- THE LINEAGE COMPOUNDS (feature 020): eight named walled yashiki in the samurai ground,
# graded by households housed. The four grand chancellery estates flank the castle east and west
# (closest to the court = highest standing); kurogi - a full chancellor whose people live out in
# Moriguchi - takes a visibly smaller estate near the east gate; the three modest houses hold the
# band north of the castle. daika, the ninth, IS the castle.
def lineage_manor(x: float, y: float, w: float, h: float, name: str, gate_dir: str) -> None:
    # label INSIDE the blank court (GM 2026-08-09: the estate's contents live on its own Mode A
    # sheet, so the empty court is the label's ground - like a governor's mansion caption)
    s.manor(x, y, w, h, f"{name.title()} Estate", gate_dir=gate_dir, label_inside=True)
    s.M["manors"][-1]["lineage"] = name  # the field capital_lineage_compounds_labeled reads


lineage_manor(2035, 720, 158, 122, "hazama", "west")
lineage_manor(2075, 975, 152, 118, "utsuro", "west")
# the west pair stands WEST of the Imperial road's kagi-no-te leg (x=800) - the strip between
# that leg and the castle moat is too narrow for a grand estate. Tokiwa sits in the narrowing
# band between the ring road and the leg, trimmed a size so its corner clears the patrol road
# (ring_road_kept_clear runs at this tier since 2026-08-09; the grand band still steps >= 1.5x
# over kurogi's estate)
lineage_manor(700, 700, 140, 112, "tokiwa", "east")
lineage_manor(665, 975, 140, 110, "anzu", "east")
lineage_manor(2040, 1330, 108, 84, "kurogi", "west")
# the modest row sits south of the road's diagonal run to the north gate
lineage_manor(1150, 425, 76, 58, "yodo", "south")  # below the flattened diagonal to the north gate
lineage_manor(1520, 390, 72, 56, "nio", "south")  # east of the karamete approach road
lineage_manor(1660, 385, 70, 54, "seki", "south")

# ---- THE SOVEREIGN TEMPLES + THE TERAMACHI RIM (feature 020). Two sovereign temples with grand
# abbots - the head houses of domain-wide orders, dedicated to the Scorpion patrons Benten and
# Jurojin - stand in the fabric; the remaining temples BELT the inner face of the rampart as the
# teramachi rim, part of the defenses, rather than gathering in one quarter
# (settlements/capitals.md, "Placements that change").
# Benten, the PRIMARY sovereign temple, is pinned to the full 7-arch avenue (torii_count=7,
# Nagahara's donation-row stride): the per-temple roll gave the primary a 3-arch stub while its
# co-sovereign rolled 7, which read the declared hierarchy inverted (settlement-review 2026-08-09).
s.shrine_hall(1850, 1620, "Temple of Benten", w=s.px(150), h=s.px(100), kind="temple", primary=True, torii=[(1850, 1700), (1850, 1820)], torii_count=7)
# Jurojin's sando faces NORTH, toward the kagi-no-te road it serves (temple_torii_face_the_street,
# GM 2026-08-09 - the first cut marched the avenue away from the road, gateway behind the temple)
s.shrine_hall(950, 1620, "Temple of Jurojin", w=s.px(150), h=s.px(100), kind="temple", torii=[(950, 1583), (950, 1547)])
# THE PRECINCT IS RESERVED EVEN THOUGH ONLY THE HALL IS DRAWN (settlement-review 2026-08-09): a
# sovereign temple is a HEAD HOUSE - abbot's residence, order administration, library, the monks
# living inside the precinct (capitals.md, "a different program, not a scaled precinct") - and
# this is the ground-reserving feature, so the complex's ~390x300 ft ground is held NOW and
# feature 021 draws it. Both registries, like the castle: block_polys is center-tested by the
# packs, placed is distance-tested and stops a wide building overhanging the precinct.
s.precinct_interior(1850, 1620, rear="north")  # sando south (torii 1700/1820): program gathers north
s.precinct_interior(950, 1620, rear="south")  # sando north (torii 1583/1547): program gathers south


def rim_temple(idx: float, name: str) -> None:
    """A modest teramachi hall on the rampart's inner face, ~130px inside the wall ellipse -
    inside the ring road's patrol strip, spaced off the gates and the government axis. Each
    hall's torii approach marches INWARD, toward the city it serves - the rim faces the fabric,
    its back to the defenses."""
    a = -math.pi / 2 + 2 * math.pi * idx / NRING
    tx, ty = round(CX + (RX - 130) * math.cos(a)), round(CY + (RY - 130) * math.sin(a))
    ux, uy = -math.cos(a), -math.sin(a)
    s.shrine_hall(tx, ty, name, w=s.px(96), h=s.px(64), kind="temple", torii=[(tx + ux * 45, ty + uy * 45), (tx + ux * 95, ty + uy * 95)])
    s.cemetery(tx - ux * 42, ty - uy * 42, 20, 14, parish=True)  # the rim temple's own plot in its backstrip (closes the 020 graveyard claim)


rim_temple(2, "Temple of Bishamon")
rim_temple(7, "Temple of Ebisu")
rim_temple(11.5, "Temple of Inari")
rim_temple(15, "Temple of Daikoku")
rim_temple(17.5, "Temple of Hotei")
