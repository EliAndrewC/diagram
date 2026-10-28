# Phase inputs - engine work moved from feature 405 (feature 445 T03)

Load this file when: you write a stage's contract for a 444 phase (FR-001), or rebuild one of the stages named below.

Feature 405 closed on 2026-10-28 (the GM: "close it and then we'll open a new version of that feature after our Rust rewrite"; the
recommendation he accepted, `specs/445-claims-switch/request.md`). Its open engine fixes and drawing-page notes are here, each under
the stage whose rebuild settles it: the rebuild either does what the task asks, or the phase's contract records the departure
with its reason. Its claims findings are not here - they are rows of `make claims-report`, worked by the claims feature filed
after the rewrite (feature 445).

**Today's counts in these texts are marked `[today's count]`** and are not budget inputs: a MODE BUDGET bundle refuses current
counts (443 FR-008), so a derivation cites a task's rule, never its measured figures.

## web

- **405 T98** - 0081's drawing page lets a lane run on the bund between plots and touch a plot's boundary, while `clear_runs`
  keeps a lane the full `margin` off the crop and `_clear_touch` keeps a join link 7 ft off it: let a lane reach the crop's edge (a
  crop margin of 0), or record the margin on 0081 as a DEVIATION with its reason; `_clear_touch`'s 7 ft fabric gap off the crop
  decided with every `clear_runs` crop margin (405 D85, 2026-10-22).
- **405 T101** - Move `tails._DOUBLED_DEG` from 15 to 0081's 20 degrees (an end running back along another way under 20 degrees is
  cut where it comes alongside), with every reader of it (`ways/lay.py` `laid_lawfully` among them; feature 417 T67, the round
  arbiter's ruling on ask:417-T67-doubled-tail). At 20, cohort seed 10's household way read as doubled and seed 40 left a shallow
  crossing `[today's count]` (measured 2026-10-21, 405 T97); done when seeds 1-48 and the pinned rows pass at 20.

## homesteads

- **405 T104** - Every pool farm draws its kura on the north wall (Inashiro, Kashikawa, Kuwabata, Mizuguchi, Sawada: `shed_side`
  N), while 0040 puts a scattered farmstead's kura on the west; and a grove farm's fixtures are laid with no kura wall
  (`bundle._lay_fixtures` passes `shed` False for the dispersed layout): draw the kura on the side 0040 gives each form and lay the
  fixtures against it; 0043's drawing page names the guess that keeps a wood shed a ken off the kura too.
- **405 T106** - Turn a wood shed's four recorded seats by the household's roll, as the coop's are. Tried twice (2026-10-21,
  2026-10-24, `specs/405-engine-findings-from-385/t106-knots.md`): it moved Sawada's farms so two households' ways ended unjoined
  `[today's count]`, every knot gather refused; land it once the knots step has a gather that keeps 0246's 7 ft gap, or the farms
  the room (the round arbiter, ask:t106-sawada-knot).
- **405 T165** (part) - 0047's drawing page states whether the privy's 48 ft reach covers every privy place, and that a privy with
  no seat in reach refuses the bundle.

## lane_wells

- **405 T165** (part) - `seat_wells`' belt claim says belt seats rank behind coverage, never refused; 0072's drawing page states
  the maps' rule of seating wells outside the belt first.

## notice

- **405 T165** (part) - 0190's drawing page states that a notice board keeps out of a farmstead's own grove (`grove_rects`, `_fits`'
  clearance) beside its rule that a board clears no ground and may stand under a crown.

## track

- **405 T111** - 0081 has the track out leave downslope past the end of the wet ground, on the flank the cluster already sits on,
  while the dry exit's fill takes the shortest way off any frame edge: prefer the cluster's own flank downslope where it is dry; and
  the fill's water lines are `plan.sink_brook`'s while its crossing places stand on `plan.brook` - check whether the sink brook is
  ever the brook's own lower course, which would then have no crossing places.
