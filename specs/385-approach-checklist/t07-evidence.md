# T07 - two claims findings left at landing (2026-10-18)

T07 moved `TREAD_WALL_FT` 4 -> 3 ft (0247 and 0081's drawing page: a Japanese village house about 3 ft back from a road; a north
Chinese house's drip strip of 2-3 chi). Pool rolled on T07's build (`make maps SCOPE=all`): clean, Kuwabata's seating shifted, the
rest unchanged; the 48-seed cohort 54/54.

1. `settlement/houses.py::HousesMixin._on_a_tread#a building's corners held to it` - MISLABELED (impl-drift round 1): every corner
   of a building is held at least 7 ft (`LANE_MIDDLE_CLEAR_FT`) off a lane's middle - 0246's figure for a garden fence - so for a
   footpath or a spur the 7 ft governs beyond the attested 3 ft from the tread. The reviewer: cite 0081 for houses and record the
   7 ft as a DEVIATION (or keep GUESS for sheds and byres). A DEVIATION must be recorded on a drawing page - a record edit that
   owes another check round. The rule predates T07 (feature 328 wave 48); T07 moved only the 3 ft under it.
2. `settlement/rolling/roll.py::RollVillageMixin._roll_cluster#lane width and clearance` - DRIFTED (impl-drift round 1): the
   legacy village roll's `clearance=40` appears on no page (0246's 18 ft lane room, 0081's 3 ft tread-to-wall). Old code, not
   touched by T07; the triage sent it on only because 0081's drawing page moved.

3. `hamletgen/ways/law.py::span_walkable#a walkable span` - CANNOT-TELL (impl-drift round 3): the code keeps 7 ft off EVERY garden,
   while 0246 lets a household's own way run beside its own fence; the reviewer asked whether span_walkable ever judges a
   household's own way beside its own garden. Measured: its only caller is `near_misses` (law.py:544), which judges the span
   joining a lane's FREE end to another way; door ends are excluded ("a door end is no short join"), so the span is a join between
   two ways, never a household's way from its dooryard. T07 DID touch this unit (the house gap `TREAD_HALF_FT + TREAD_WALL_FT`
   in place of 3.0, and the threshing yard split into its own claim), so the claims gate counts the finding as introduced, not
   carried.
