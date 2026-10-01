"""The country shrine's own kinds (feature 277): what a village district's shrine sheet draws that no magistracy does.

Written in the magistracy kinds' form (feature 262) and from the same record - research religion-and-death 090 to 128 -
so the country shrine's page is read from its sheet's `data-kind` tags exactly as a magistracy's is. A kind both draw
(the torii, the grove, the well, the kitchen, the latrine, the garden, the fire-water tubs, the genkan) is written
once, in its magistracy family, and serves both.
"""

from __future__ import annotations

from ..classes import Kind


# The GM's ruling: one roof over the hall and the dwelling is the setting's form for its country shrines.
class HallAndDwelling(Kind):
    """
    What: The shrine's one building under one roof: the villagers' hall at its center, the country monk's kitchen at
    one end and their rooms at the other, the small sanctuary standing behind it on the approach's axis.

    Why: A village shrine with a monk living at it was a common form before 1868, if an uncounted one - the
    shrine-temple kept by a resident monk - and the monk's dwelling was a farmhouse in form, earth-floored kitchen and
    matted rooms. One roof over the hall and the dwelling is attested at one temple and is this project's chosen form for the
    setting's country shrines; so the building is a farmhouse with a hall at its heart, larger than a farmhouse
    because it contains one.

    Note: The resident monk and their farmhouse-form dwelling are read, though no source counts how many village
    shrines had one; one roof over hall and dwelling is attested once, and called unusual there, and is this project's form
    for the setting. The building's size is set from the record's bands - a village hall about 20
    to 35 ft on a side, the one-roof building 2,100 to 3,600 sq ft, no deeper than the one attested example - and where
    in those bands it falls is a guess.

    Caveat: The building's size is set from the record's bands - a village hall about 20 to 35 ft on a side, the
    one-roof building 2,100 to 3,600 sq ft, no deeper than the one attested example - and where in those bands it falls
    is a guess.

    Name: hall and dwelling
    Covers: the one-roof building, its outline, its roof and its caption
    Label: accurate
    Sources: kuri-jawiki, jinguji-enwiki, bettoji-jawiki, sakai-kaieji, ehime-pref-honden-56, saitama-kannonji-kannondo
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html, research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html, research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
    """

    key = "hall and dwelling"


class Sanctuary(Kind):
    """
    What: The sanctuary, the small closed shrine that houses the deity, standing behind the hall on the approach's
    axis - one bay wide under a sweeping front roof.

    Why: A shrine's buildings line up on one axis, the hall of worship before and the sanctuary at the rear, where the
    deity is enshrined and nobody gathers. At a village shrine it is small: the sanctuary was often one bay wide, and
    a measured village sanctuary runs a few feet to a side. So it is drawn behind the hall, on the approach's line, at
    its true few feet.

    Note: The halls' axis, the sanctuary at the rear and its one-bay form are read; the approach running on that axis
    is a map convention, and its drawn size is the measured village sanctuary's, about 6 ft.

    Caveat: the approach running on that axis is a map convention, and its drawn size is the measured village
    sanctuary's, about 6 ft.

    Name: sanctuary
    Covers: the sanctuary behind the hall
    Label: accurate
    Sources: jaanus-honden, jaanus-haiden, nagarezukuri-jawiki, kotobank-nagarezukuri, ehime-pref-honden-56
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "sanctuary"


class MonksRooms(Kind):
    """
    What: The country monk's own rooms at the dwelling end of the building - matted living rooms, part of the one roof.

    Why: The monk lives at the shrine, and their dwelling is a farmhouse in form: an earth-floored kitchen at one end
    and matted rooms beyond it. An ordinary temple's priest's house was like a house of the district, not a great
    hall's quarters.

    Note: The form is read - a priest's house like the farmhouse of its region. Its size is a guess: no page we read
    measures a small priest's house, so the dwelling is sized from the village map's own farmhouse, 46 by 28 ft, and
    under one roof it is no separate building but the hall's dwelling end - a form attested once, at Kaie-ji, and
    called unusual there; that a monk lived at a village shrine is read, but how common it was, no source counts.

    Name: the monk's rooms
    Covers: the dwelling end's rooms
    Label: guess
    Sources: kuri-jawiki, kawasaki-chonenji-kuri, bunka-tokuunji-kuri
    Entry: research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.html; research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
    """

    key = "the monk's rooms"


class WritingRoom(Kind):
    """
    What: A small room along the dwelling's front where the district's registers are kept and written - a desk and a
    record chest, in the monk's own house.

    Why: The monk keeps the district's registers, as a temple certified its parishioners under the Edo registration,
    and a small shrine often had no office of its own, its business done at the keeper's home: so the books live in
    the dwelling, never in a separate hall. So the writing room is a room of the monk's house, near its entrance, where
    the villagers who come on business are met.

    Note: That a small shrine often had no office of its own, its business done at the keeper's home, is read; the
    yearly register itself was compiled by the village headmen, so that the monk's house holds the district's
    registers is this project's choice; the room itself, its size and its place along the front are a guess.

    Caveat: the yearly register itself was compiled by the village headmen, so that the monk's house holds the
    district's registers is this project's choice; the room itself, its size and its place along the front are a
    guess.

    Name: writing room
    Covers: the writing room in the dwelling
    Label: accurate
    Sources: terauke-seido-jawiki, shumon-ninbetsu-jawiki, jaanus-shamusho
    Entry: research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.html; research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
    """

    key = "writing room"


# The GM's rulings: the number of arches along the approach and their pitch.
class ShrineApproach(Kind):
    """
    What: The approach - the path that runs from where the way enters the precinct under its arch to the hall's
    step.

    Why: A shrine is entered along its approach, and the arch stands where the approach enters the shrine's ground; a
    row of arches along it is a donors' row, each arch a gift - before modern times only at a great Inari site. This setting raises arches along any shrine's approach, a deliberate deviation from the historical norm. So the path runs up to the hall along a line the map's author draws to fit the ground, and the arches
    stand over it.

    Note: The approach and the arch at its entry are read; its line is drawn to fit the ground, and its innermost arch standing 12 ft off the hall is a map convention; a row of arches at an ordinary shrine is attested only in modern times, and drawn here as a deliberate deviation; its width is a guess, and the arches' number and pitch are
    this project's choice, not the record's.

    Caveat: its line is drawn to fit the ground, and its innermost arch standing 12 ft off the hall is a map convention; a row of arches at an ordinary shrine is attested only in modern times, and drawn here as a deliberate deviation; its width is a guess, and the arches' number and pitch are this project's choice, not the record's.

    Name: approach
    Covers: the path from the precinct's edge to the hall
    Label: accurate
    Sources: jinja-jawiki, kudamatsu-stone-torii, kato-kawataka-torii
    Entry: research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html, research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html, research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "approach"


class ShrineBasin(Kind):
    """
    What: A plain stone water basin beside the approach, where the villagers rinse their hands and mouth before they
    worship.

    Why: The basin stands beside the approach, and the rite is old; the roofed pavilion over it is the newer and the
    richer form - the one found dated before 1868 stands at a shrine whose following reached Edo - and no page says
    whether a village shrine's basin then stood in the open. A parish gave its shrine a dated basin in 1828.

    Note: The basin beside the approach and the rite are read; the plain, unroofed basin at a village shrine is a
    guess - neither the open basin nor the roofed one is attested at a village shrine before 1868.

    Caveat: the plain, unroofed basin at a village shrine is a guess - neither the open basin nor the roofed one is
    attested at a village shrine before 1868.

    Name: basin
    Covers: the stone basin by the approach
    Label: accurate
    Sources: jinja-jawiki, liga-temizuya, kawasaki-nagao-chozubachi, ubusuna-jinja-ameblo
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "basin"


class SacredTree(Kind):
    """
    What: The sacred tree - the precinct's greatest tree, ringed at its trunk by a straw rope.

    Why: A shrine keeps a sacred tree, marked as the deity's by the rope round it; one encyclopedia article, itself
    flagged as short of sources, says most shrines were built where such a tree already stood. So one great tree
    stands near the approach, roped.

    Note: The roped sacred tree is read; that shrines were built where such a tree stood rests on one article flagged
    as short of sources, and how common one was at a village shrine is a guess, no count having been found.

    Caveat: that shrines were built where such a tree stood rests on one article flagged as short of sources, and how
    common one was at a village shrine is a guess, no count having been found.

    Name: sacred tree
    Covers: the sacred tree and its rope
    Label: accurate
    Sources: kotobank-shinboku, shinboku-jawiki
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "sacred tree"


class SweptClearing(Kind):
    """
    What: The open ground of the precinct round the building - ground left clear of the wood about it, its edge
    ragged, with the forecourt before the hall's step where the villagers gather.

    Why: A village shrine's precinct held its wood and open ground, the wood covering some or nearly all of it and the
    rest open, and the open ground is where the hall, its sanctuary and the forecourt stand. Open ground spreads from
    where people walk and stops where they do not, so its edge is ragged, never ruled. That the ground about a shrine
    was swept is found only in present-day folklore that gives no date, so the map claims no sweeping.

    Note: The precinct's open ground is read; how far the open ground reaches past the hall is a guess, its ragged edge
    is the project's reading of how such ground spreads, and the forecourt's depth is a guess from its use.

    Caveat: how far the open ground reaches past the hall is a guess, its ragged edge is the project's reading of how
    such ground spreads, and the forecourt's depth is a guess from its use.

    Name: precinct clearing
    Covers: the open ground and the forecourt about the building
    Label: accurate
    Sources: chinju-no-mori-jawiki, sando-jawiki
    Entry: research/questions/0224-ground-swept-clear-around-shrines-and-graves.html; research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html
    """

    key = "precinct clearing"


class Footpath(Kind):
    """
    What: A worn footpath from the building's kitchen side to the well.

    Why: Water is carried from the well to the kitchen every day, and a way worn by feet runs where they go - off
    the sanctuary's ground.

    Note: The path is a guess, the drawing's own reading of daily use; no page read draws a shrine's path to its well.

    Name: footpath
    Covers: the path from the clearing to the well
    Label: guess
    Sources: not recorded
    Entry: research/contents.json#religion-and-the-dead (no dedicated entry - recorded as silent)
    """

    key = "footpath"


class GuardianFigures(Kind):
    """
    What: A pair of stone guardian figures facing each other across the approach - lion-dogs, or at a Bishamon shrine
    his tigers.

    Why: Stone guardian pairs were commoners' donations, multiplying from the Edo period on, so a shrine has them only as its parish
    grows richer; at average wealth there are none.

    Note: The donations and their date are read, as are Bishamon's tigers at named temples; that the tigers reach a village shrine is a guess, and which shrines carry them is the wealth knob.

    Caveat: that the tigers reach a village shrine is a guess, and which shrines carry them is the wealth knob.

    Name: guardian figures
    Covers: the guardian pair beside the approach
    Label: accurate
    Sources: komainu-jawiki, gltjp-zenkokuji, darumamuseum-bishamonten
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "guardian figures"


class StoneLanterns(Kind):
    """
    What: Stone lanterns set along the approach, each the gift of villagers of the parish.

    Why: Stone lanterns were votive donations, dated by the villagers who gave them, so a shrine has them only as its
    parish grows richer; at average wealth there are none.

    Note: The donations are read; which shrines carry them is the wealth knob.

    Caveat: which shrines carry them is the wealth knob.

    Name: lanterns
    Covers: the stone lanterns along the approach
    Label: accurate
    Sources: niiza-ishigami-lantern
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "lanterns"


class StrengthStones(Kind):
    """
    What: Strength stones beside the approach - great rounded stones the young men lifted in contests.

    Why: Strength stones stood beside shrine approaches from the late Edo period on, so a shrine has them only as its
    parish grows richer; at average wealth there are none.

    Note: The stones and their date are read; which shrines carry them is the wealth knob.

    Caveat: which shrines carry them is the wealth knob.

    Name: strength stones
    Covers: the strength stones beside the approach
    Label: accurate
    Sources: nerima-hikawa-chikaraishi
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "strength stones"


class FarmersStage(Kind):
    """
    What: A farmers' stage on the shrine's ground, for the plays the parish put on at its festival.

    Why: Farmers' stages stood on shrine ground from the early 1800s on, in some regions many to a province; so it is a
    knob, absent by default.

    Note: The stages, their date and their regional spread are read; whether a shrine has one is a knob.

    Caveat: whether a shrine has one is a knob.

    Name: stage
    Covers: the farmers' stage
    Label: accurate
    Sources: noson-kabuki-butai-jawiki
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "stage"


class SumoRing(Kind):
    """
    What: A sumo ring on the shrine's ground, for the bouts dedicated to its deity.

    Why: The ring's consecration rite is performed for the sumo offered at shrines across the country, though no page read dates it or places a ring at a village shrine; it is a knob, absent by
    default.

    Note: The rite for sumo offered at shrines across the country is read, in the present tense and undated; a ring at a village shrine is not read, and whether a shrine has one is a knob.

    Caveat: a ring at a village shrine is not read, and whether a shrine has one is a knob.

    Name: sumo ring
    Covers: the sumo ring
    Label: accurate
    Sources: kokugakuin-dohyo
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "sumo ring"


class BellTower(Kind):
    """
    What: A small bell tower on the shrine-temple's ground.

    Why: A minimal temple is described as a main hall and a bell tower, and the country monk's shrine is a
    shrine-temple; but a village hall may have had neither, so it is a knob.

    Note: The minimal temple as a main hall and a bell tower rests on one undated commercial page in the present tense,
    and a village hall may have had neither - so its presence is a knob, and the rule for it a guess.

    Name: bell tower
    Covers: the bell tower
    Label: guess
    Sources: homemate-shichido-garan
    Entry: research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html; research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
    """

    key = "bell tower"


class ShrineBurialGround(Kind):
    """
    What: The village's burial ground where it lies by the shrine - graves at the country monk's building, the setting's
    parish temple.

    Why: The graves lie by the monk-run building, and in the setting the country monk's shrine is the parish temple;
    so where a village buries in the shrine's yard, the burial ground stands by it.

    Note: A ground in a shrine's own yard is a deliberate deviation, resting on the setting's own canon: real Shinto shuns death, and the two-grave villages surveyed keep the shrine at the upper end and the burial ground below the houses, so it is this setting's and not history's. Whether a village's one ground lies in the shrine's yard or apart from it is rolled per village at even odds, a guess, since no page counts the villages taking each form.

    Name: burial ground
    Covers: the burial ground by the shrine, where the village has it there
    Label: deviation
    Sources: danka-terauke-encyclopedia, bunkotsu-jawiki
    Entry: research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html; research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.drawing.html
    """

    key = "burial ground"
