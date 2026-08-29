"""What counts as a DWELLING, in one leaf module with no imports of its own.

Split out of `check_village/common_03_capacity.py` on 2026-08-29 (feature 156, settlement-review round
4) because two callers now need it and they sit on opposite sides of an import cycle: the gate's
capacity checks, and the interactive page's place card, which states how many dwellings a town or a
city draws. Reaching the gate's copy from the page meant `from ..check_village...` inside a function -
which resolves safely, but executes `check_village/__init__.py` and its star-import of all 52 modules
and 14,524 lines of the check battery on every town and city page write, to obtain a ten-element set.

A leaf with no imports can be imported from anywhere, so there is one definition and no cycle.
`common_03_capacity` re-exports these names, so every existing `from .common_03_capacity import
DWELLING_KINDS` keeps working.
"""

from __future__ import annotations

#: A building's role for the population/frontage maths. A DWELLING houses one ~5-person household;
#: a BUSINESS is a commercial frontage (the merchant's house+shop is BOTH - dual-use); everything
#: else (civic, government, granary kura, barns, gate furniture) houses no one and fronts nothing.
DWELLING_KINDS = {
    "laborer",
    "laborer_large",
    "servant",
    "burakumin",
    "samurai",
    "samurai_large",
    "merchant",
    "merchant_house",
    "merchant_large",
    "monk_house",  # adept-monk households by the temple precincts (GM 2026-07-24) - real resident families, so they count as housing; they are deliberately ABSENT from the caste bands (clergy are not a lay caste)
}  # samurai_large was missing (a senior samurai house is a dwelling like every other _large variant) - found when Tango's population count kept landing 5 short of its generator's

BUSINESS_KINDS = {"shop", "merchant"}

HOUSEHOLD = 5
