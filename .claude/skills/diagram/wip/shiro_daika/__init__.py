"""Shiro Daika - the DOMAIN CAPITAL of the Daika house (diagram skill, Mode B, 1px = 3ft).

SKELETON (feature 019) + THE GROUND-RESERVING LAYER (feature 020). The map now carries the wall,
the moat, the river, the ways, the gates, the CASTLE - and every compound and public work that
must be sited BEFORE housing: the government ward on the ote-suji, the Imperial Magistrate's
compound, the eight lineage compounds, the two sovereign temples and the teramachi rim, the
wharf with its granaries and brokers' row, the towpath, and the aqueduct. All housing (the
rank-graded samurai districts, retainer terraces, commoner machi), the public wells, the fire
towers and the kido mesh are feature 021's - the packs flow around the ground reserved here.

THE HOUSE. Daika is a Bayushi vassal house of the SCORPION, seated here; Ubame county (see
legacy-hand-authored-pool/towns/ubame/ubame.gen.py) is one of its county seats, out in Moriguchi province, and the charcoal
road that leaves Ubame westward arrives at this city's EAST gate. Scorpion patron fortunes are
Benten and Jurojin, so the two sovereign temples are theirs.

THE WAYS (GM 2026-08-08, confirmed against the campaign map). The IMPERIAL ROAD enters at the
SOUTH gate, runs north through the city, and beyond the north gate bends NORTHWEST toward Shiro
Kyo. Two unlabeled domain trunk roads leave the other gates: EAST to the Fox lands and the
Kitsune Mori, SOUTHWEST into the heart of the domain. Only the Imperial road is named - an
ordinary road's course is already visible.

THE RIVER runs NORTHEAST -> SOUTHWEST past the city's southeast flank and off both edges. NO
TRUNK ROAD RUNS ALONGSIDE IT: water carried bulk far more cheaply than carts, so a highway
shadowing a navigable river is redundant, and the roads leave in the directions the water does
not serve. The bank carries the TOWPATH (the Chinese qiandao - upstream haulage, so it
supplements the boats rather than replacing them), running to the wharf and no further. See
research/cities/capitals.md, "A river gets a TOWPATH, not a road".

THE CASTLE sits in the ring (castle_seat="ring" - both traditions nest their citadel, so it is
the median form), north of center, with its OTE-MON FACING SOUTH onto the ceremonial approach
that runs down to the Imperial road's south gate. That is the jokamachi rule: the main road
passes the castle's FRONT, "to indicate the glory of the ruler". Its interior is BLANK and stays
blank - see Settlement.castle's docstring for the sync argument.

THE GRAIN IS IN TWO PLACES FOR TWO REASONS (settlements/capitals.md): the siege stock is inside
the castle (implied, never drawn); the working stipend-and-transhipment rice is the domain
granary at the wharf. The EMPEROR'S granaries are separate again - they face brigands, not
besiegers - and this map exercises imperial_granary_seat="wharf" (grain moves by boat).
"""

# THE ENGINE BOOTSTRAP, and a DEFECT FIXED IN PASSING (feature 173, constitution Principle XIV -
# a defect found while doing something else is fixed in that work). It read:
#
#     while not os.path.exists(os.path.join(_D, "settlement.py")):
#         _D = os.path.dirname(_D)
#
# and `settlement.py` became the `settlement/` PACKAGE on 2026-08-16 (feature 025). So the walk
# never terminated: `os.path.dirname("/")` is `"/"`, and the loop spun at the filesystem root
# forever. This map has been an INFINITE LOOP rather than a failing script since that day - which is
# how it went unnoticed, because `make map GEN=wip/shiro-daika.gen.py` hangs instead of erroring
# (measured 2026-08-31: 45 minutes, no output, no traceback).
#
# It looks for the engine ROOT now - the directory holding `l7r/diagram` - which is what the
# original comment meant by walking up rather than counting directories, and it RAISES at the
# filesystem root instead of spinning there.
import os
import sys

_D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
while not os.path.isdir(os.path.join(_D, "l7r", "diagram")):
    _up = os.path.dirname(_D)
    if _up == _D:
        raise RuntimeError("shiro_daika: no l7r/diagram above this file - is the map outside the skill tree?")
    _D = _up
sys.path.insert(0, _D)

# Importing this package DRAWS THE MAP: each part executes at import, in this order. The order
# is enforced by the parts themselves - each imports `s` from the one above it (see the note at
# the top of any of them) - and this list is the readable statement of the same contract.
#
# `isort: off` IS LOAD-BEARING. ruff's I rule sorts an import block alphabetically, and it did:
# the first cut of this split shipped `castle, civic, fields, frame, housing, trades, wharf`,
# which ran `fields` - and so `s.finish()` - fourth of seven. Nothing caught it, because no test
# rolls a wip map and the only symptom is a wrong picture. The chained imports would now defeat
# a re-sort on their own; this keeps the list itself readable in the order it actually runs.
# isort: off
from . import frame as frame  # noqa: E402,F401
from . import castle as castle  # noqa: E402,F401
from . import wharf as wharf  # noqa: E402,F401
from . import housing as housing  # noqa: E402,F401
from . import trades as trades  # noqa: E402,F401
from . import civic as civic  # noqa: E402,F401
from . import fields as fields  # noqa: E402,F401
# isort: on
