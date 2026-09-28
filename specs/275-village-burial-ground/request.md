# Feature 275 - the village's own burial ground in the generator (claimed 2026-09-28 as feature 273's follow-up)

Carried from feature 273 (plan D5, task T06): the GM's request of 2026-09-27 is verbatim in
`specs/273-hamlet-graveyards/request.md`. Feature 269 (Diagram supplemental) handed its owed burial-generator change to
273: 269 R1's knob in religion-and-death 280 (a village's burial ground in the shrine or temple yard, or a ground of its own
apart - even odds, a hilltop shrine always apart), 270's siting (a ground apart downstream, beyond the last house, within
~650 ft of the middle of the houses), and 160's band as a rule in the population served (the village's own households
plus those of its hamlets that roll `village_ground`). 273 could not land it because 269's 270 and 280 are not yet on
main; this feature builds it once they are, with 273's shared edge seat (`settlement/civic_grounds/edge_seat.py`) and
its village cremation ground's `cremation_seat` "beside_burial" form, which until then seats as on its own.

## The GM's constraint (2026-09-28, verbatim)

> When you say that you will build the village's own burial ground, do you mean the hamlets or the actual village? Because I do not want you to modify hand-rolled maps as part of this.

So this feature changes the village GENERATOR only (the roller's village tier and its tests). No hand-rolled map -
Hoshigaoka or any other frozen village - is edited or regenerated as part of it.

## WITHDRAWN 2026-09-28

The GM: *"So what actually is feature 275 then? ... I think you can get rid of it entirely, and instead, we just want to
make sure that [when] we make village maps scripted that we do the correct things in the scripted generation."* No
village is scripted yet, so a village-generator change would reach no map. The design moved to
`.claude/skills/diagram/future-work/farming-communities.md` ("OWED AT CONVERSION: a village's funerary grounds") and
is named in `migration-plan.md` step 5. The number stays spent; nothing is built under it.
