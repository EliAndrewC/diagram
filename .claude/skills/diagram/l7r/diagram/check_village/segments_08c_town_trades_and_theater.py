"""Gate segments (town trades and theater; keys 0543_011-0543_057) - bodies verbatim, registry order preserved."""


# WHY (farmers are the overwhelming majority caste): settlements.md "Historical grounding"


# MERCHANT and LABORER housing varies in SIZE by wealth, like a provincial city's (budgets.md
# Town wealth tiers): a MINORITY of merchants are very-rich / rich and live in large homes
# (~5 of ~24), and a few laborers are 'master/rich' (~2-3 of ~29); the rest live in small/standard
# dwellings. Require the larger homes (kind merchant_large / laborer_large) to be PRESENT and a
# CLEAR MINORITY - not that every house is one uniform size.


# MERCHANT RESIDENCES sit BEHIND the merchant BUSINESSES, and CLOSER to the road than the
# LABORER housing - a clean radial band: shops front the road, the merchant homes directly
# behind them, then a gap, then the laborers set further back. Scoped to road-fronted towns
# (those with a trunk M["road"], e.g. unwalled Hoshizora); a walled town's interior grid is laid
# out around cross-streets, not one radial axis, so this single-axis test does not apply there.
# droad = perpendicular distance from a building to the nearest road segment.


# a town has hundreds of farmers - we never show all the farmland, so at least
# one field must run off the map edge (implying more farmland beyond what's drawn)


# a rice-TRANSIT town (meta(granary=True)) shows a distinct tax-rice granary - a row of
# fireproof kura where grain gathered from many counties is forwarded up the kick-up
# chain. A standard county seat does NOT draw one: its grain sits inside the magistrate's
# yamen, implied by the manor. Opt-in, so the default is no check (unlike the gate
# market, theater stage, and monasteries, which are opt-OUT defaults).


# a noticeable MINORITY of merchant houses keep a fireproof storehouse (kura) for their
# (often absentee) landlords' rent-rice and bulk goods - more than a token 1-2, beyond a
# shop's ordinary inventory. Draw them with s.merchant_storehouses(...).


# a county seat is a market center: peasants from the far edge of its catchment stay
# over on market eve in a cheap communal flophouse (kichin-yado) where travelers arrive
# - the gate market of a walled town, the road of an unwalled one. Default-on (>= 1);
# meta(flophouses=N) requires more (a busy hub); meta(flophouses=0) opts out.


# a county town is a stop on the trade route: it needs ONE caravan INN (s.inn) with a STABLES
# (s.stables) next to it and OPEN GROUND beside the stables - a pasture for the wagon-train oxen
# and horses - exactly like a provincial city's gate caravan facilities, but a single one. The
# inn must sit ALONG the road (the Imperial road, or a town street) - the caravans pull up to it -
# NOT buried behind the shop rows. A WALLED town keeps it INSIDE the rampart (caravans enter the gate).


# the inn FACES the road and lies PARALLEL to it - the caravans pull straight up to it - so its
# noren front (the +y edge after the inn's `rot`) must point at the nearest route point, which also
# makes its long frontage edge run along the road. A diagonal road needs a tilted inn.


# every town has a THEATER STAGE unless meta(theater_stage=False); for a walled town
# it sits INSIDE the walls unless meta(theater_stage="outside")


# a town's monasteries: by default 2, dedicated to the patron fortunes of the clan
# whose holdings include it (meta(clan=...)). Override with an explicit list -
# meta(monastery_fortunes=[...]) - for a town that changed hands, or a 1-monastery town.
