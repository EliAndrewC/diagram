"""The glossary the map's explanations use (feature 134, GM 2026-08-28: "a glossary of terms defined so
that when we use those terms in our modals ... someone can hover their mouse over it to get an
explanation of the word ... 'bund' or 'coppiced', but also any Japanese words that are not so common
that we would expect everyone to know them").

Each entry: the term as it appears in the prose (matched whole-word, case-insensitive, with the
listed variants) and a one- or two-sentence definition. The page wraps every occurrence in the
explanation text in a hover tooltip. Definitions are written from the research entries the
explanations cite; a term here is a term the prose in `classes.py` actually uses.
"""

from __future__ import annotations

#: term -> (variants matched in the prose, the definition)
GLOSSARY: dict[str, tuple[tuple[str, ...], str]] = {
    "bund": (
        ("bund", "bunds", "aze"),
        "The low earthen ridge between two paddy basins, a foot or two wide and about a foot high, re-plastered each spring so each basin holds its water; farmers walk the bunds to reach the plots.",
    ),
    "azemame": (("azemame",), "Bund beans: soybeans planted along the top of a paddy bund, a second crop from ground that would otherwise grow weeds."),
    "coppice": (
        ("coppice", "coppiced", "coppicing"),
        "A wood cut on a cycle - every 10 to 30 years the stems are cut to the stump and regrow - for firewood, poles and fodder; the floor stays open and the canopy young.",
    ),
    "iriai": (("iriai",), "The customary common land of a Japanese village - woods, grass and scrub held by the village and governed by its own rules on who may cut, when, and how much."),
    "satoyama": (("satoyama",), "The managed country between the village and the mountain: the coppice woods, grasslands, paddies and ponds a farming community worked and drew on."),
    "tameike": (("tameike",), "An irrigation reservoir - a pond made by damming a valley head with an earthen dike, sitting above the fields it waters, with a single outlet."),
    "yashikirin": (("yashikirin",), "A homestead grove: the belt of trees planted around a farmhouse plot as its own shelter from wind and sun."),
    "fengshui grove": (
        ("fengshui forest", "fengshui back grove", "fengshui grove", "fengshui"),
        "The grove a village keeps on its windward, high side - the back grove of Chinese village planning - as its wall against the winter wind.",
    ),
    "hokora": (("hokora",), "A small roadside or household shrine, a knee-high shelter of stone or wood for a local spirit."),
    "kosatsuba": (("kosatsuba",), "The notice board: a small roofed frame where the authorities posted the standing law, rate tables and ban lists, sited where everyone passes."),
    "minka": (("minka",), "A traditional Japanese farmhouse - a timber-framed dwelling under a steep thatched roof, its ridge on the long axis."),
    "take-yabu": (("take-yabu",), "A bamboo thicket: a clonal stand of bamboo with a hard edge, held and cut like a coppice."),
    "shitsuden": (
        ("shitsuden",),
        "Wet paddy: rice ground too poorly drained to dry out, which holds water even out of season. Harder to work, colder, and lower-yielding than a paddy that can be emptied, and it takes no winter crop.",
    ),
    "kanden": (("kanden",), "Dry paddy: rice ground that drains, so that when the water is let out it dries to an ordinary dry field and can carry a winter crop before the next flooding."),
    "hatake": (("hatake",), "Dry-field farmland - the unirrigated ground that grows grains, beans and vegetables, as against the flooded paddy."),
    "goemon-buro": (("goemon-buro",), "The cauldron bath: an iron tub heated from below, the bath of self-sufficient farm villages."),
    "magariya": (("magariya",), "The L-shaped farmhouse of northern Japan, with the stable under the same roof as the dwelling - a cold-country form."),
    "daizu": (("daizu",), "The soybean - grown as a field crop of its own on the dry hem, and along the paddy bunds as azemame."),
    "catena": (("catena",), "The sequence of soils and crops down a slope: paddy on the wet valley floor, dry crops on the well-drained ground above, woodland on the hill."),
    "hem": (("hem",), "The band of dry ground above the paddy's supply canal where the dry crops grow."),
    "head race": (("head race",), "The channel that carries water from the intake along the field's high edge to where it is divided into the ditches."),
    "lateral": (("lateral", "laterals"), "A branch ditch running down-slope from the head race between the plots."),
    "polder": (("polder",), "Land reclaimed from marsh or lake behind an enclosing dike and drained by canals."),
    "night soil": (("night soil",), "Human waste collected from privies and composted as fertilizer."),
    "dooryard": (("dooryard",), "The yard at a farmhouse's door - the household's own ground beside the house."),
    "toe": (("toe",), "The low foot of a slope or a field, where the water collects."),
}
