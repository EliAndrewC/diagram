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
from .castle import s
from .frame import RIVER

# ---- THE WHARF (feature 020): the collecting-and-disbursing end of the domain's rice, on the
# river outside the southeast arc - the Asakusa Okura / Kuramae model, a working chain from river
# to store: jetties and a dock basin at the bank, the DOMAIN granary behind the quay (stipend rice
# in, surplus shipping out), the brokers' row fronting the lane before it (MERCHANT, not state -
# the fudasashi pattern: the contracts and lending sit outside the Ministry of Retainers' narrow
# stipend function, and the brokers' money is what will build the theaters next door in 021).
# The EMPEROR'S granaries stand apart upstream (imperial_granary_seat="wharf"): a different
# threat model - brigands, not besiegers - so a stout row outside the castle, near the water the
# grain moves on.
# JETTIES ARE LANDING STAGES, NOT CAUSEWAYS (GM 2026-08-09: at 66 ft they reached past
# mid-river). A stage runs a boat-length into the stream and no further - the fairway stays
# clear by law (the log-boom research) - so ~39 ft into a 120 ft river, a third of the channel.
# One stage per granary complex end: barges tie up AT the kura frontage and unload straight in.
s.jetty(2303, 2265, rot=29.9, length=13)  # the domain row's upstream stage
s.jetty(2236, 2381, rot=25.9, length=13)  # this stage stands on the bend below the row - its own bearing, not the row's  # ...and its downstream one, just past the row's end
# the Emperor's complex gets its OWN landing (GM 2026-08-09: its grain moves by boat - that is
# the whole reason imperial_granary_seat="wharf" - so it does not borrow the domain quay 200 ft
# downstream; separate stores, separate barges, separate tally)
s.jetty(2405, 2089, rot=29.9, length=13)
# NO dock basin: the rectangular canal-head cut is Nagahara's in-city vocabulary and read as a
# floating blue square against this diagonal bank (GM 2026-08-09) - a riverside wharf is jetties
# and quay, not a basin. The granary rows stand ON the wharf, turned PARALLEL to the bank they
# load from, a cart's width off the water; captions plural, one per complex. These are the
# STAGING/working stores - the strategic siege stock is inside the castle, implied, and it would
# indeed be foolish to keep the domain's main reserve outside the walls.
# ...and the kura stand AT the quay (GM 2026-08-09: the first seat held them ~84 ft back "for
# flood", but the Kuramae anchor unloads barges STRAIGHT into the stores - the flood answer is
# the kura's own raised floor and the stone revetment, not distance; a granary you must
# porter sacks to has lost the wharf's whole point)
BANK_ROT = -60.1  # DERIVED from the river's current bearing at the wharf (119.9 deg): the
# rows lie ALONG the bank. Recompute this when the course moves - the first draw was cut to
# a -54 constant and stayed there when the channel shifted (GM 2026-08-10).
# ---- THE QUAY FACE (GM 2026-08-11: "is three piers the only way barges unload? Is there some
# sort of dock that is not a boardwalk?"). Research in research/cities/river-cities.md: on a river
# the working face is the BANK, faced with stone and notched with STEPPED landings, because the
# water level moves feet across the year and a flight of steps is the right height at every one of
# them. The piers are for reach; the quay is where most of the cargo actually comes ashore.
# DERIVED from the river's own line, so a re-routed river carries its wharf with it.
_QSEG = (RIVER[2], RIVER[3])  # the reach the granary rows stand on
_qdx, _qdy = _QSEG[1][0] - _QSEG[0][0], _QSEG[1][1] - _QSEG[0][1]
_qlen = math.hypot(_qdx, _qdy)
_qnx, _qny = -_qdy / _qlen, _qdx / _qlen  # unit normal pointing at the CITY (northwest) bank - the side the granaries stand on
_QOFF = 40.0 / 2 + 4  # the river's half-width, plus the face's own footing
QUAY = [(_QSEG[0][0] + _qdx * t + _qnx * _QOFF, _QSEG[0][1] + _qdy * t + _qny * _QOFF) for t in (0.44, 0.66, 0.92)]
s.quay(QUAY, steps=3)  # three landings along the frontage the six granaries and three warehouses share

s.granary(2253, 2312, n=4, w=20, h=12, gap=8, label="domain granaries", append=True, rot=BANK_ROT)
s.granary(2368, 2121, n=3, w=20, h=12, gap=8, label="Imperial granaries", append=True, rot=BANK_ROT)  # a cart's width UP the bank - the row's ends were lapping the river's stroke
# the brokers' lane runs shore-parallel between the granaries and the quay; its frontage is the
# brokers' row. The wharf suburb is OUTSIDE the ring-road bound the urban packs honor, so the
# frontage places against the suburb's own ground and the bound is restored after.
BROKER_LANE = [(2330, 2120), (2220, 2280), (2135, 2410)]
# a STREET, not a lane (021): the kashi quay street is real machi frontage - the brokers'
# row and warehouse fronts must satisfy businesses_front_streets like any other shops
s.street(BROKER_LANE, width=s.lw(15))
_CITY_BOUND = s.bound
s.bound = [[1940, 1950], [2480, 1950], [2480, 2530], [1940, 2530]]
s.frontage(BROKER_LANE, (["merchant", "merchant", "shop"] * 4), width=8, spacing=19, rows=1, jitter=1, setback=3, dense=True)
s.bound = _CITY_BOUND
